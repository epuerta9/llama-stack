# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
from faststream.nats.fastapi import NatsRouter, Logger
from fastapi import Depends, FastAPI
from faststream import FastStream
import asyncio
from pydantic import BaseModel, ValidationError
from faststream.nats import NatsBroker
from typing import Any
from typing import List, Optional
import json

router = NatsRouter("nats://localhost:4222")

@router.after_startup
async def after_startup(app: FastAPI):
    key_value = await router.broker.key_value(bucket="hackathon-bucket")


class CompletionMessage(BaseModel):
    role: str
    content: str
    stop_reason: Optional[str]
    tool_calls: List  # List of tool calls (could be further defined if it has structure)

class ResponseModel(BaseModel):
    completion_message: CompletionMessage
    logprobs: Optional[dict]  #
def call():
    return True

@router.subscriber("alpha.inference.chat-completion.out")
@router.publisher("alpha.inference.chat-completion.kv")
async def inference_out(m: ResponseModel, logger: Logger, d=Depends(call)):
    """Listen for all chat complettions and add them to the KV store. eventually it should have a better key"""
    logger.info(m)
    key_value = await router.broker.key_value(bucket="hackathon-bucket")
    await key_value.put("result", m.model_dump_json().encode())

    return m



@router.subscriber("alpha.inference.chat-completion.kv")
async def inference_out_kv(result: ResponseModel, logger: Logger):
    """Pick this up and do something special with it"""
    logger.info("in the inference out kv. After chat completion has been added to the KV")
    logger.info(result)


@router.get("/")
async def hello_http():
    return "Hello, HTTP!"