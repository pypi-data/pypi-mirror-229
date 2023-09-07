from dataclasses import dataclass, field
from datasets import load_dataset, Dataset
from functools import cached_property
from tqdm.auto import tqdm
from typing import Any, Optional, Protocol, Iterable, Callable

from utils import (
    NUMERIC_IN_ZH,
    extract_choice_ans,
    extract_numeric,
    get_answer,
    is_equiv,
)

from evaluate import load

TextGenerationPipeline = Callable[[Iterable[str]], list[str]]


def fake_pipeline(prompts: Iterable[str]) -> list[str]:
    return [prompt for prompt in tqdm(prompts)]


@dataclass
class Task:
    dataset_name: str | tuple[str, str] = ("gsm8k", "main")
    split: str = "test"
    # metrics: list[str] = field(default_factory=list)
    metric_name: str | tuple[str, str] = ("sustech/tlem", "gsm8k")
    input_column: str = "question"
    label_column: str = "answer"
    prompt: Optional[Callable | str] = None

    @cached_property
    def name(self):
        return (
            self.dataset_name
            if isinstance(self.dataset_name, str)
            else self.dataset_name[0]
        ) + f"-{self.split}"

    @cached_property
    def samples(self):
        return self.dataset[self.input_column]

    @cached_property
    def dataset(self):
        ds = load_dataset(
            *self.dataset_name
            if isinstance(self.dataset_name, tuple)
            else self.dataset_name,
            split=self.split,
        )
        if self.prompt is not None:
            ds = ds.map(
                lambda example: {
                    self.input_column: self.prompt.format(
                        input_column=example[self.input_column]
                    )
                }
                if isinstance(self.prompt, str)
                else self.prompt(example),
            )

        return ds

    @cached_property
    def metric(self):
        metric = (
            load(self.metric_name)
            if isinstance(self.metric_name, str)
            else load(*self.metric_name)
        )
        return metric

    def run(self, pipeline: TextGenerationPipeline = fake_pipeline):
        outputs = pipeline(self.samples)
        return self.metric.compute(
            responses=outputs, references=self.dataset[self.label_column]
        )


class Metrics:
    def gsm8k(responses: list[str], answers: list[str | int]):
        scores = []
        for response, answer in zip(responses, answers):
            pred = extract_numeric(response)
            gold = extract_numeric(answer) if isinstance(answer, str) else str(answer)
            scores.append(1.0 * (pred == gold))
        return scores

    def MATH(responses: list[str], answers: list[str]):
        scores = []

        for response, answer in zip(responses, answers):
            indices = [pos for pos, char in enumerate(response) if char == "$"]
            if len(indices) <= 2:
                scores.append(0)
                continue
            else:
                result = response[indices[-2] + 1 : indices[-1]]
                gold = get_answer(answer)
                scores.append(1.0 * is_equiv(result, gold))

        return scores

    def math23k(responses: list[str], answers: list[str]):
        scores = []
        for response, answer in zip(responses, answers):
            pred = extract_numeric(response, pattern=NUMERIC_IN_ZH)
            gold = extract_numeric(answer, pattern=NUMERIC_IN_ZH)
            scores.append(1.0 * (pred == gold))
        return scores

    def gsm8k_zh(responses: list[str], answers: list[str]):
        scores = []
        for response, answer in zip(responses, answers):
            pred = extract_numeric(response, pattern=NUMERIC_IN_ZH)
            gold = extract_numeric(answer)
            scores.append(1.0 * (pred == gold))
        return scores

    def svamp(responses: list[float], answers: list[str]):
        scores = []
        for response, answer in zip(responses, answers):
            pred = extract_numeric(response, pattern=NUMERIC_IN_ZH)
            gold = answer
            scores.append(1.0 * (float(pred) == gold))
        return scores

    def mmlu(responses, answers):
        scores = []
        for response, answer in zip(responses, answers):
            pred = extract_choice_ans(response)
            gold = answer.lower()
            scores.append(1.0 * (pred == gold))
        return scores
