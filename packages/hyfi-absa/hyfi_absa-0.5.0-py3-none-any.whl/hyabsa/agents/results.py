import datetime
import json
import logging
from typing import Any, Dict, List

from hyfi.composer import BaseModel

from hyabsa import HyFI
from hyabsa.llms import ChatCompletionResponse

logger = logging.getLogger(__name__)


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

    @classmethod
    def convert_absa_output_to_results(
        cls,
        output_file: str,
        skip_failed: bool = False,
        value_for_failed: Any = None,
    ) -> List[Dict]:
        """Converts a jsonl output file into AgentResult objects

        Args:
            output_file (str): path to jsonl file
            skip_failed (bool, optional): If True, skips failed responses. Defaults to False.
            value_for_failed (Any, optional): If skip_failed is False, this value is used for the response. Defaults to None.

        Returns:
            List[Dict]: List of AgentResult objects
        """
        results = []
        for line in HyFI.load_jsonl(output_file):
            if line["parsed"] == "failed":
                if skip_failed:
                    continue
                else:
                    line["response"] = value_for_failed
            results.append(line)
        logger.info("Converted %s to %s AgentResult objects", output_file, len(results))
        return results
