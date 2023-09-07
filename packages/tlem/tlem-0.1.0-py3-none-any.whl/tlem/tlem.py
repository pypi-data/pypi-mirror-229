# %%

try:
    from ipytorch import logging
except Exception as e:
    import logging

from typing import Any, Optional, Protocol, Iterable, Callable
from tqdm.auto import tqdm
from evaluate.evaluation_suite import EvaluationSuite
import evaluate
import numpy as np
import datasets
from tasks import Task, Metrics
from utils import is_equiv

# %%

# %cd ../tlem

# %load_ext ipytorch
# %ls


# TODO: Add BibTeX citation
_CITATION = """\
@InProceedings{huggingface:module,
title = {A great new module},
authors={huggingface, Inc.},
year={2020}
}
"""

# TODO: Add description of the module here
_DESCRIPTION = """\
A simple measurement that returns the number of elements in dataset.
"""


# TODO: Add description of the arguments of the module here
_KWARGS_DESCRIPTION = """
Calculates number of elements in dataset
Args:
    data: list of elements.
Returns:
    element_count: number of elements in dataset,
Examples:
    >>> measure = evaluate.load("lvwerra/element_count")
    >>> measure.compute(["a", "b", "c")
    {"element_count": 3}
"""

# TODO: Define external resources urls if needed
BAD_WORDS_URL = "http://url/to/external/resource/bad_words.txt"


@evaluate.utils.file_utils.add_start_docstrings(_DESCRIPTION, _KWARGS_DESCRIPTION)
class ReasoningMetric(evaluate.Metric):
    """TODO: Short description of my evaluation module."""

    def _info(self):
        features = datasets.Features(
            {
                "responses": datasets.Value("string"),
                "references": datasets.Value("string"),
            }
        )

        if self.config_name == "svamp":
            features = datasets.Features(
                {
                    "responses": datasets.Value("string"),
                    "references": datasets.Value("float"),
                }
            )

        # TODO: Specifies the evaluate.EvaluationModuleInfo object
        return evaluate.EvaluationModuleInfo(
            # This is the description that will appear on the modules page.
            # module_type="measurement",
            description=_DESCRIPTION,
            citation=_CITATION,
            inputs_description=_KWARGS_DESCRIPTION,
            # This defines the format of each prediction and reference
            features=features,
            # Homepage of the module for documentation
            homepage="http://module.homepage",
            # Additional links to the codebase or references
            codebase_urls=["http://github.com/path/to/codebase/of/new_module"],
            reference_urls=["http://path.to.reference.url/new_module"],
        )

    def _compute(self, responses, references, verbose=False):
        results = {}
        scores = getattr(Metrics, self.config_name)(responses, references)
        acc = np.asarray(scores).mean()
        results = {
            "accuracy": acc,
            "scores": scores,
        }

        if verbose:
            results["references"] = references
            results["answers"] = responses
            # results["scores"] = scores

        return results


class Suite(EvaluationSuite):
    def run(
        self, model_or_pipeline: Any, prompt: str = "{instruction}"
    ) -> dict[str, float]:
        self.assert_suite_nonempty()

        results_all = {}
        for task in tqdm(self.suite, desc="Running tasks"):
            task_name = task.name
            results = task.run(model_or_pipeline)
            results_all[task_name] = results
        return results_all

    def __init__(self, name):
        super().__init__(name)

        self.suite = [
            Task(
                dataset_name=("gsm8k", "main"),
                metric_name=("sustech/tlem", "gsm8k"),
                input_column="question",
                label_column="answer",
            )
            # TASK_REGISTRY["gsm8k"],
            # TASK_REGISTRY["competition_math"],
        ]


# %%

