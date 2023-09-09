# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.rai.utils.llm_eval_benchmark.common.prompt_formatter import PromptFormatter
from azureml.rai.utils.llm_eval_benchmark.common.model.job import Job
import itertools
from typing import Generator, List
import pandas as pd
from pandas import DataFrame


class ResponseParser:
    """
    ResponseParser is responsible for parsing openai api response. It is one layer above PromptFormatter - it calls
    PromptFormatter to parse anything related to in-prompt custom batching. It is one layer below RequestManager which
    handles http failures etc.
    """
    def __init__(self):
        return

    @staticmethod
    def generate_result_df(input_examples: List[dict], df_output: DataFrame):
        """Combine input and output df to construct one dataframe.

        :param input_examples: a list of dictionaries containing inputs for current job
        :type input_examples: List[dict]
        :param df_output: the dataframe of output for current job
        :type df_output: DataFrame
        :return: dataframe with combined input and output columns
        :rtype: DataFrame
        """
        df_input = pd.DataFrame(input_examples)
        if df_input.shape[0] != df_output.shape[0]:
            raise Exception("shouldn't reach here, output df and input df not of same size")
        df = pd.concat([df_input, df_output], axis=1)
        return df

    def parse_job_response(self, prompt_formatter: PromptFormatter, response_data: dict, expected_output_number: int):
        """Parse response in one api response, given a prompt formatter. Expected_output_number is how many responses
        we expect to get out of this job's response

        :param prompt_formatter: the prompt formatter used to create prompt batching
        :type prompt_formatter: PromptFormatter
        :param response_data: the processed response from api
        :type response_data: dict
        :return: a dataframe of parsed output
        :rtype: DataFrame
        """
        output_examples = []
        # if response data contains error, we return "" of expected number
        try:
            for sample in response_data["samples"]:
                # split the output into {expected_output_number} examples, return "" of expected number if fail
                sample_examples = prompt_formatter.split_output_examples(sample, expected_output_number)
        except Exception:
            sample_examples = [""] * expected_output_number

        sample_examples_parsed = []
        for example in sample_examples:
            decoded = prompt_formatter.decode_example(example)  # if not parsable will return a failure dict value defined in formatter
            sample_examples_parsed.append(decoded)
        output_examples.append(sample_examples_parsed)

        # merge all samples (in our case we only have 1 sample)
        all_output = list(itertools.chain.from_iterable(output_examples))
        df_output = pd.DataFrame({key: [res[key] for res in all_output] for key in prompt_formatter.label_keys})
        return df_output

    def parse_job_response_to_df(self, prompt_formatter: PromptFormatter, job: Job):
        """Generate combined input-output dataframe for a given Job with response data populated

        :param prompt_formatter: prompt formatter used for prompt batching
        :type prompt_formatter: PromptFormatter
        :param job: job object with input data and response
        :type job: Job
        :return: a dataframe combining job input and parsed output
        :rtype: DataFrame
        """
        output_df = self.parse_job_response(prompt_formatter, job.response_data, len(job.prompt_data.input_examples))
        result = self.generate_result_df(job.prompt_data.input_examples, output_df)
        return result

    def parse_jobs_response_to_df(self, prompt_formatter: PromptFormatter, jobs_with_response: List[Job]) -> Generator[DataFrame, None, None]:
        """Given a stream of job responses, parse them and generate a combined input-output dataframe per job

        :param prompt_formatter: prompt formatter used for prompt batching
        :type prompt_formatter: PromptFormatter
        :param jobs_with_response: job objects with response populated
        :type jobs_with_response: List[Job]
        :return: a generator of dataframes
        :rtype: Generator[DataFrame, None, None]
        """
        for job in jobs_with_response:
            yield self.parse_job_response_to_df(prompt_formatter, job)
