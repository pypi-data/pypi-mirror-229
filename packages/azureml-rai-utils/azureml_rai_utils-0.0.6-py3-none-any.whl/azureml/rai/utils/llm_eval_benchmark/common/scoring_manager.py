# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.rai.utils.llm_eval_benchmark.common.prompt_formatter import PromptFormatter
from azureml.rai.utils.llm_eval_benchmark.common.response_parser import ResponseParser
from azureml.rai.utils.llm_eval_benchmark.common.request_manager import RequestManager
from azureml.rai.utils.llm_eval_benchmark.common.model.job import Job
from typing import List
import pandas as pd
from pathlib import Path
from pandas import DataFrame


class ScoringManager:
    """
    ScoringManager is in charge of the whole evaluation process from input dataframe to output dataframe
    Takes care of job batching, checkpointing, etc.
    """
    def __init__(self,
                 checkpoint_fp: str,
                 prompt_formatter: PromptFormatter,
                 response_parser: ResponseParser,
                 request_manager: RequestManager,
                 min_score: int,
                 max_score: int,
                 request_args: dict,
                 endpoint_args: dict,
                 max_inputs_per_batch: int,
                 n_jobs_per_batch: int = 5):
        self.prompt_formatter = prompt_formatter
        self.response_parser = response_parser
        self.request_manager = request_manager
        self.checkpoint_fp = checkpoint_fp
        self.min_score = min_score
        self.max_score = max_score
        self.request_args = request_args
        self.endpoint_args = endpoint_args
        self.max_inputs_per_batch = max_inputs_per_batch
        self.n_jobs_per_batch = n_jobs_per_batch
        self.job_idx = 0

    def make_job(self, **job_params) -> Job:
        """Make job, tracking job_idx internally."""
        new_job = Job(job_idx=self.job_idx, **job_params)
        self.job_idx += 1
        return new_job

    def create_request_jobs(self, input_df):
        """Given input dataframe, generate prompts and batch them to create a list of jobs

        :param input_df: input dataframe, per row is an input
        :type input_df: DataFrame
        :return: jobs: a list of jobs, per job has a batch of prompts with the batch of input encoded
        :rtype: List[Job]
        """
        prompts = self.prompt_formatter.generate_prompts(
            input_df,
            max_inputs=self.max_inputs_per_batch
        )
        jobs = [
            self.make_job(prompt_data=prompt_data, request_params=self.request_args)
            for prompt_data in prompts
        ]
        return jobs

    def checkpoint_df(self, df: DataFrame):
        """Checkpoint a dataframe to checkpoint path, append in csv

        :param df: dataframe to be checkpointed
        :type df: DataFrame
        """
        output_file_path = Path(self.checkpoint_fp)
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.checkpoint_fp, mode='a', header=False)

    def get_jobs_output(self, jobs: List[Job]) -> pd.DataFrame:
        """Run inference over jobs, which includes batch submission and parsing results.
        Each job is one API call with n prompts concatenated together into a string separated by ##TASK #i
        We parse output and write to file every self.n_jobs_per_batch jobs. Note that there is job-level batching
        (for checkpointing), which is independent of the prompt batching.

        :param jobs: a list of jobs with request and prompt data
        :type jobs: List[Job]
        :return: final_df: the full dataframe with both input and output data, one dataframe for all jobs
        :rtype: DataFrame
        """
        start_idx = 0
        final_df = pd.DataFrame()

        while start_idx < len(jobs):
            end_idx = min(start_idx + self.n_jobs_per_batch, len(jobs))
            cur_batch = jobs[start_idx:end_idx]

            jobs_with_responses = self.request_manager.get_job_batch_response(
                jobs=cur_batch, token=self.endpoint_args["token"], endpoint_url=self.endpoint_args["endpoint_url"]
            )

            # Parse responses for this batch of jobs
            parsed_dfs = self.response_parser.parse_jobs_response_to_df(self.prompt_formatter, jobs_with_responses)
            batch_df = pd.DataFrame()
            for parsed_df in parsed_dfs:
                batch_df = pd.concat([batch_df, parsed_df], axis=0)

            # checkpoint current batch
            self.checkpoint_df(batch_df)

            # append to overall result
            final_df = pd.concat([final_df, batch_df], axis=0).reset_index(drop=True)
            start_idx += self.n_jobs_per_batch

            if start_idx % 50 == 0:
                print(f"Finished {start_idx} out of {len(jobs)} jobs")

        return final_df

    def score_input(self, input_df: DataFrame) -> DataFrame:
        """Given input dataframe, create jobs, call API, obtain output dataframe

        :param input_df: input dataframe
        :type input_df: DataFrame
        :return: output_df: output dataframe with GPT scores
        :rtype: DataFrame
        """
        jobs = self.create_request_jobs(input_df)
        output_df = self.get_jobs_output(jobs)
        return output_df
