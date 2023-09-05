import datetime
import json
from typing import Optional

from hyfi.composer import BaseModel

from hyabsa import HyFI
from hyabsa.contexts import ChatMessage
from hyabsa.llms import OpenAIChatCompletion
from hyabsa.prompts import Prompts

from .results import AgentResult

logger = HyFI.getLogger(__name__)


class BaseAgent(BaseModel):
    _config_group_: str = "/agent"
    _config_name_: str = "__init__"

    llm: OpenAIChatCompletion = OpenAIChatCompletion()
    prompts: Prompts = Prompts()
    task: str = "AE"
    prompt: str = "base"
    output_dir: str = "outputs/preds"
    output_filename: Optional[str] = None
    verbose: bool = False

    @property
    def model(self) -> str:
        return self.llm.model.replace(".", "")

    @property
    def output_filepath(self) -> str:
        ouput_filename = (
            self.output_filename
            or f"{self.task}_{self.prompt}_{self.model}_{datetime.datetime.now().strftime('%Y%m%d')}.jsonl"
        )
        HyFI.mkdir(self.output_dir)
        return f"{self.output_dir}/{ouput_filename}"

    def build_message(self, text: str) -> ChatMessage:
        return ChatMessage(content=self.prompts.build(text, self.task, self.prompt))

    def execute(self, text: str) -> str:
        result = AgentResult.from_chat_reponse(
            self.llm.request(self.build_message(text)),
        )
        if self.output_filepath:
            HyFI.append_to_jsonl(result.model_dump(), self.output_filepath)
        return json.dumps(result.model_dump(), ensure_ascii=False)
