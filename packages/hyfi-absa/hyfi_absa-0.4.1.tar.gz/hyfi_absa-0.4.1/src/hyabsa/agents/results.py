import datetime
import json
from typing import Any, List

from hyfi.composer import BaseModel

from hyabsa import HyFI
from hyabsa.llms import ChatCompletionResponse

logger = HyFI.getLogger(__name__)


class AgentResult(BaseModel):
    timestamp: str = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
    id: str
    parsed: str
    usage: dict
    response: List[Any]

    @classmethod
    def from_chat_reponse(
        cls,
        id: str,
        response: ChatCompletionResponse,
    ) -> "AgentResult":
        parsed = "success"
        try:
            content = json.loads(response.content)
            if isinstance(content, dict):
                parsed = "failed"
                content = [content]
        except json.decoder.JSONDecodeError:
            content = [response.content]
            parsed = "failed"

        return cls(
            id=id,
            parsed=parsed,
            usage=response.usage,
            response=content,
        )
