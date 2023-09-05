from typing import Dict

from hyfi.composer import BaseModel

from hyabsa import HyFI

logger = HyFI.getLogger(__name__)


class Prompts(BaseModel):
    _config_group_: str = "/prompts"
    _config_name_: str = "__init__"

    tasks: Dict[str, str] = {}
    prompts: Dict[str, Dict[str, str]] = {}

    def _get_prompt(self, task: str, prompt_name: str) -> str:
        if prompt := self.prompts.get(task, {}).get(prompt_name, ""):
            return prompt
        else:
            raise ValueError(f"Prompt for task {task} is not defined.")

    def build(self, text: str, task: str, prompt_name: str) -> str:
        prompt = self._get_prompt(task, prompt_name)
        prompt += f'\nInput text:\n"{text}"\nAnswer:\n'
        return prompt
