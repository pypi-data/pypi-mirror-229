from typing import List, Optional, Union

from datasets import Dataset
from hyfi.run import Run
from hyfi.runner import Runner

from hyabsa import HyFI
from hyabsa.agents import AbsaAgent

logger = HyFI.getLogger(__name__)


class AbsaRunner(Runner):
    _config_name_: str = "absa"
    _auto_populate_: bool = True

    task_name: str = "absa"
    agent: AbsaAgent = AbsaAgent()
    tasks: Optional[List[str]] = []
    data_load: Run = Run(_config_name_="load_dataset")
    data_save: Run = Run(_config_name_="save_dataset_to_disk")

    id_col: str = "id"
    text_col: str = "text"
    batch_size: int = 1000
    num_workers: int = 1
    remove_columns: Optional[Union[List[str], str]] = None
    load_from_cache_file: bool = True
    top_n: Optional[int] = None

    _dataset: Optional[Dataset] = None

    @property
    def dataset(self) -> Dataset:
        if self._dataset is None:
            self._dataset = self.load_dataset()
        return self._dataset

    def load_dataset(self) -> Dataset:
        return HyFI.partial(self.data_load.config)()

    def save_dataset(self, dataset: Dataset) -> None:
        HyFI.partial(self.data_save.config)(dataset)

    def run(self):
        dataset = self.load_dataset()
        if self.top_n is not None:
            logger.info("Selecting top %s rows...", self.top_n)
            dataset = dataset.select(range(self.top_n))

        tasks = self.tasks or ["QUAD"]
        for task in tasks:
            logger.info(
                "Predicting %s with a batch size of %s and %s workers...",
                task,
                self.batch_size,
                self.num_workers,
            )
            dataset = dataset.map(
                batch_run,
                batched=True,
                batch_size=self.batch_size,
                num_proc=self.num_workers,
                fn_kwargs={
                    "task": task,
                    "agent": self.agent.model_copy(),
                    "id_col": self.id_col,
                    "text_col": self.text_col,
                },
                remove_columns=self.remove_columns,
                load_from_cache_file=self.load_from_cache_file,
            )
        if self.verbose:
            logger.info("Dataset shape: %s", dataset.shape)
            logger.info("Dataset columns: %s", dataset.column_names)
            print(dataset[0])
        self.save_dataset(dataset)


def batch_run(
    batch,
    task: str = "QUAD",
    agent: Optional[AbsaAgent] = None,
    id_col: str = "id",
    text_col: str = "text",
) -> dict:
    if agent is None:
        raise ValueError("Agent must be provided")
    agent.task = task
    if agent.verbose:
        HyFI.print(agent.model_dump())

    res = [
        execute_each(id, text, agent)
        for id, text in zip(batch[id_col], batch[text_col])
    ]
    return {f"{task}_pred": res}


def execute_each(
    id: str,
    text: str,
    agent: AbsaAgent,
) -> str:
    response = agent.execute(id, text)
    if agent.verbose:
        # logger.info("Text: %s", text)
        logger.info("Response: %s", response)

    return response
