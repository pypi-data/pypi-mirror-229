# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.rai.utils.llm_eval_benchmark.common.model.prompt_data import PromptData


class Job:
    """Job state for prompts submitted to model engines."""

    def __init__(
        self,
        job_idx: int,
        prompt_data: PromptData,
        request_params: dict,
        retries_attempted: int = 0,
        response_data: dict = None,
        status: str = None,
    ):
        self.job_idx = job_idx
        self.prompt_data = prompt_data
        self.request_params = request_params
        self.retries_attempted = retries_attempted
        self.response_data = response_data or {}
        self.status = status
