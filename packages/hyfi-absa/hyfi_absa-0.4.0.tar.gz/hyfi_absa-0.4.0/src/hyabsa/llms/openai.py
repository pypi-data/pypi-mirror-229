import time
from typing import Any, Dict, List, Optional

import backoff
import openai
from hyfi.composer import BaseModel, Field, SecretStr
from hyfi.env import Env
from openai.error import (
    APIConnectionError,
    APIError,
    InvalidRequestError,
    RateLimitError,
    ServiceUnavailableError,
)

from hyabsa import HyFI
from hyabsa.contexts import ChatMessage

logger = HyFI.getLogger(__name__)


class ChatCompletionConfig(BaseModel):
    model: str
    temperature: float
    messages: List[ChatMessage]


class ChatCompletionResponse(BaseModel):
    content: str
    usage: Dict[str, Any] = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }


class ChatCompletionEnv(Env):
    OPENAI_API_KEY: Optional[SecretStr] = Field(exclude=True, default="")


class OpenAIChatCompletion(BaseModel):
    _config_group_: str = "/llm"
    _config_name_: str = "openai"

    api_key: Optional[str] = None
    model: str = "gpt-3.5-turbo-0301"
    rate_limit_per_minute: int = 3500
    temperature: float = 0.0
    env: ChatCompletionEnv = ChatCompletionEnv()

    _engine_: Optional[openai.ChatCompletion] = None

    @property
    def engine(self):
        if self._engine_ is None:
            self.initialize()
        return self._engine_

    def initialize(self, api_key: Optional[str] = None):
        api_key = api_key or self.api_key
        if not api_key and self.env.OPENAI_API_KEY:
            api_key = self.env.OPENAI_API_KEY.get_secret_value()
        if not api_key:
            raise ValueError("OpenAI API Key is required.")
        openai.api_key = api_key
        logger.info("OpenAI API Key is set successfully.")
        self._engine_ = openai.ChatCompletion()
        logger.info("OpenAI ChatCompletion API is initialized.")

    def build_config(self, message: ChatMessage) -> Dict[str, Any]:
        return ChatCompletionConfig(
            model=self.model,
            temperature=self.temperature,
            messages=[message],
        ).model_dump()

    def request(self, message: ChatMessage) -> ChatCompletionResponse:
        delay = 60.0 / self.rate_limit_per_minute
        return call_api(
            self.engine,
            self.build_config(message),
            delay_in_seconds=delay,
        )


@backoff.on_exception(
    backoff.expo,
    (
        RateLimitError,
        APIConnectionError,
        APIError,
        ServiceUnavailableError,
    ),
)
def request_api(engine, args, delay_in_seconds: float = 1):
    time.sleep(delay_in_seconds)
    return engine.create(**args)


def call_api(engine, args, delay_in_seconds: float = 1) -> ChatCompletionResponse:
    time.sleep(delay_in_seconds)
    try:
        response = request_api(engine, args, delay_in_seconds=delay_in_seconds)
        message = response["choices"][0]["message"]
        content = message["content"].strip().strip("\n")
        usage = response["usage"]
        return ChatCompletionResponse(content=content, usage=usage)
    except InvalidRequestError as e:
        logger.error(e)
        return ChatCompletionResponse(content=e.user_message)
    except Exception as e:
        logger.error(e)
        return ChatCompletionResponse(content=str(e))
