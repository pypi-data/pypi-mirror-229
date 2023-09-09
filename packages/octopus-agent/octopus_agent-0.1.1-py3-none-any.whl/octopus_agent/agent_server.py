# vim:fenc=utf-8
#
# Copyright (C) 2023 dbpunk.com Author imotai <codego.me@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import logging
import sys
from octopus_proto.agent_server_pb2_grpc import AgentServerServicer
from octopus_proto.agent_server_pb2_grpc import add_AgentServerServicer_to_server
from octopus_proto import agent_server_pb2
from octopus_kernel.sdk.kernel_sdk import KernelSDK
from dotenv import dotenv_values
from typing import AsyncIterable, Any, Dict, List, Optional, Sequence, Union, Type
from tempfile import gettempdir
from pathlib import Path
from langchain.agents import AgentType
import aiofiles
from aiofiles import os as aio_os
from grpc.aio import ServicerContext, server
import os

from langchain.agents import initialize_agent
from langchain.schema.messages import SystemMessage
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain import LLMChain
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent

from .gpt_tools import ExecutePythonCodeTool, ExecuteShellCodeTool, ExecuteTypescriptCodeTool, PrintCodeTool, PrintFinalAnswerTool
from .tools import OctopusAPIMarkdownOutput
from .prompt import OCTOPUS_FUNCTION_SYSTEM
from .gpt_async_callback import AgentAsyncHandler
import random
import string

config = dotenv_values(".env")
LOG_LEVEL = logging.DEBUG
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)
os.environ["OPENAI_API_TYPE"] = config["llm_type"]
os.environ["OPENAI_API_VERSION"] = config["llm_api_version"]
os.environ["OPENAI_API_BASE"] = config["llm_api_base"]
os.environ["OPENAI_API_KEY"] = config["llm_api_key"]


class AgentRpcServer(AgentServerServicer):

    def __init__(self):
        self.agents = {}
        self.max_file_size = int(config["max_file_size"])
        self.verbose = (
            True if "verbose" in config and config["verbose"] == "1" else False
        )
        self.llm = AzureChatOpenAI(
            temperature=0,
            deployment_name=config["llm_api_deployment"],
            verbose=self.verbose,
        )

    async def add_kernel(
        self, request: agent_server_pb2.AddKernelRequest, context: ServicerContext
    ) -> agent_server_pb2.AddKernelResponse:
        """Create a token, only the admin can call this method"""
        metadata = dict(context.invocation_metadata())
        if "api_key" not in metadata or metadata["api_key"] != config["admin_key"]:
            await context.abort(10, "You are not the admin")
        if request.key in self.agents and self.agents[request.key]:
            return agent_server_pb2.AddKernelResponse(code=0, msg="ok")
        # init the sdk
        sdk = KernelSDK(request.endpoint, request.key)
        await sdk.connect()
        # TODO a data dir per user
        api = OctopusAPIMarkdownOutput(sdk, request.workspace)
        # init the agent
        tools = [
            ExecutePythonCodeTool(octopus_api=api),
            ExecuteShellCodeTool(octopus_api=api),
            ExecuteTypescriptCodeTool(octopus_api=api),
            PrintCodeTool(),
            PrintFinalAnswerTool(),
        ]
        prefix = (
            """%sBegin!
Question: {input}
{agent_scratchpad}"""
            % OCTOPUS_FUNCTION_SYSTEM
        )
        system_message = SystemMessage(content=prefix)
        agent = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            agent_kwargs={"system_message": system_message},
            handle_parsing_errors=True,
            verbose=self.verbose,
            max_iterations=config.get("max_iterations", 5),
        )
        self.agents[request.key] = {
            "sdk": sdk,
            "workspace": request.workspace,
            "agent": agent,
        }
        return agent_server_pb2.AddKernelResponse(code=0, msg="ok")

    async def send_task(
        self, request: agent_server_pb2.SendTaskRequest, context: ServicerContext
    ) -> AsyncIterable[agent_server_pb2.TaskRespond]:
        logger.debug("receive the task %s ", request.task)
        metadata = dict(context.invocation_metadata())
        if (
            "api_key" not in metadata
            or metadata["api_key"] not in self.agents
            or not self.agents[metadata["api_key"]]
        ):
            logger.debug("invalid api key")
            await context.abort(10, "invalid api key")
        agent = self.agents[metadata["api_key"]]["agent"]
        queue = asyncio.Queue()
        handler = AgentAsyncHandler(queue)

        async def worker(task, agent, handler):
            try:
                return await agent.arun(task, callbacks=[handler])
            except Exception as ex:
                logger.error("fail to run agent for %s", ex)

        logger.debug("create the agent task")
        task = asyncio.create_task(worker(request.task, agent, handler))
        token_usage = 0
        while True:
            logger.debug("start wait the queue message")
            respond = await queue.get()
            if not respond:
                logger.debug("exit the queue")
                break
            logger.debug(f"respond {respond}")
            queue.task_done()
            yield respond
        await task
        respond = agent_server_pb2.TaskRespond(
            token_usage=handler.token_usage,
            model_name=handler.model_name,
            iteration=handler.iteration,
            final_respond=agent_server_pb2.FinalRespond(answer=task.result()),
        )
        logger.debug(f"respond {respond}")
        yield respond

    async def download(
        self, request: agent_server_pb2.DownloadRequest, context: ServicerContext
    ) -> AsyncIterable[agent_server_pb2.FileChunk]:
        """
        download file
        """
        metadata = dict(context.invocation_metadata())
        if (
            "api_key" not in metadata
            or metadata["api_key"] not in self.agents
            or not self.agents[metadata["api_key"]]
        ):
            await context.abort(10, "invalid api key")
        agent = self.agents[metadata["api_key"]]
        target_filename = "%s/%s" % (agent["workspace"], request.filename)
        if not await aio_os.path.exists(target_filename):
            await context.abort(10, "%s filename do not exist" % request.filename)
        async with aiofiles.open(target_filename, "rb") as afp:
            while True:
                chunk = await afp.read(1024 * 128)
                if not chunk:
                    break
                yield agent_server_pb2.FileChunk(
                    buffer=chunk, filename=request.filename
                )

    async def upload(
        self,
        request: AsyncIterable[agent_server_pb2.FileChunk],
        context: ServicerContext,
    ) -> agent_server_pb2.FileUploaded:
        """
        upload file
        """
        metadata = dict(context.invocation_metadata())
        if (
            "api_key" not in metadata
            or metadata["api_key"] not in self.agents
            or not self.agents[metadata["api_key"]]
        ):
            await context.abort(10, "invalid arguments")
        agent = self.agents[metadata["api_key"]]
        tmp_filename = Path(gettempdir()) / "".join(
            random.choices(string.ascii_lowercase, k=16)
        )
        target_filename = None
        logger.info(f"upload file to temp file {tmp_filename}")
        length = 0
        async with aiofiles.open(tmp_filename, "wb+") as afp:
            async for chunk in request:
                if length + len(chunk.buffer) > self.max_file_size:
                    await context.abort(10, "exceed the max file limit")
                length = length + await afp.write(chunk.buffer)
                if not target_filename:
                    target_filename = "%s/%s" % (agent["workspace"], chunk.filename)
        logging.info(f"move file from {tmp_filename} to  {target_filename}")
        await aio_os.rename(tmp_filename, target_filename)
        return agent_server_pb2.FileUploaded(length=length)


async def serve() -> None:
    logger.info(
        "start agent rpc server with host %s and port %s",
        config["rpc_host"],
        config["rpc_port"],
    )
    serv = server()
    add_AgentServerServicer_to_server(AgentRpcServer(), serv)
    listen_addr = "%s:%s" % (config["rpc_host"], config["rpc_port"])
    serv.add_insecure_port(listen_addr)
    await serv.start()
    await serv.wait_for_termination()


def server_main():
    asyncio.run(serve())
