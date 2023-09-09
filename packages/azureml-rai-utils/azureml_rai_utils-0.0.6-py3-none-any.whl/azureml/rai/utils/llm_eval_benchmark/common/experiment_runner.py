# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.rai.utils.llm_eval_benchmark.common.data_preparer import DataPreparer
from azureml.rai.utils.llm_eval_benchmark.common.metrics_generator import MetricsGenerator
from azureml.rai.utils.llm_eval_benchmark.common.prompt_formatter import PromptFormatter
from azureml.rai.utils.llm_eval_benchmark.common.response_parser import ResponseParser
from azureml.rai.utils.llm_eval_benchmark.common.request_manager import RequestManager
from azureml.rai.utils.llm_eval_benchmark.common.scoring_manager import ScoringManager
from azureml.rai.utils.llm_eval_benchmark.benchmarkutils.azure_connector import AzureConnector
from azureml.rai.utils.llm_eval_benchmark.benchmarkutils.constants import ENDPOINT_CONFIG_PATH, LOG_TEMPLATE_PATH, PROMPT_PATH, SCORE_LABEL
import json
import os
from pandas import DataFrame
import mlflow
from os.path import dirname


class ExperimentRunner:
    """ExperimentRunner calls all the other components and runs experiments end to end"""
    def __init__(self, output_dir: str, azure_connector: AzureConnector, endpoint_config_path=ENDPOINT_CONFIG_PATH, prompt_path=PROMPT_PATH, log_template_path=LOG_TEMPLATE_PATH, score_label=SCORE_LABEL):
        self.output_dir = output_dir
        self.azure_connector = azure_connector
        self.endpoint_config_path = endpoint_config_path
        self.prompt_path = prompt_path
        self.request_config_path = os.path.join(dirname(dirname(__file__)), os.path.join("configs", "request_config.json"))
        self.log_template_path = log_template_path
        self.score_label = score_label
        self.data_preparer = DataPreparer(azure_connector)
        self.metrics_generator = MetricsGenerator()

    @staticmethod
    def _get_json_from_config(fp):
        """Loads json file as a dictionary

        :param fp: path of json file
        :type fp: str
        :return: dictionary
        :rtype: dict
        """
        f = open(fp)
        args = json.load(f)
        f.close()
        return args

    def get_endpoint_args_from_config(self):
        """Gets endpoint arguments from provided path of config file, and connects to keyvault to retrieve token

        :return: a dictionary of endpoint configs, including endpoint_url, model, and token
        :rtype: dict
        """
        endpoint_config = self._get_json_from_config(self.endpoint_config_path)
        token = self.azure_connector.get_secret(endpoint_config["keyvault_url"], endpoint_config["token_name"])
        try:
            return {"endpoint_url": endpoint_config["endpoint_url"],
                    "model": endpoint_config["model"],
                    "token": token}
        except Exception:
            raise Exception("endpoint config json should contain endpoint_url, model")

    def get_prompt(self):
        """Gets prompt from prompt template file path.

        :return: string of prompt template
        :rtype: str
        """
        with open(self.prompt_path) as f:
            prompt = "\n".join(f.readlines())
        return prompt

    def log_template(self):
        """Logs the annotation template both on mlflow and in outputs folder
        """
        template = self.get_prompt()
        f = open(self.log_template_path, "a")
        f.write(template)
        f.close()
        mlflow.log_param("template", template[:500])
        return

    def score_input_df(self, annotation_template: str, input_df: DataFrame, experiment_output_path: str, max_inputs_per_batch: int):
        """Calls all other components to complete scoring of an input dataframe, given annotation template.
        Also logs results to a checkpoint path. Note that one experiment runner can run multiple benchmarks that have
        different configurations. Thus these configs are passed to method as arguments.

        :param annotation_template: the prompt template string
        :type annotation_template: str
        :param input_df: input dataframe
        :type input_df: dataframe
        :param experiment_output_path: file path to checkpoint results
        :type experiment_output_path: str
        :param max_inputs_per_batch: max number of prompts to be batched into one API call
        :type max_inputs_per_batch: int
        :return output_df: a dataframe with a label column provided by AOAI
        :rtype: dataframe
        """
        request_args = self._get_json_from_config(self.request_config_path)
        endpoint_args = self.get_endpoint_args_from_config()

        # get min score, max score
        min_score = self.data_preparer.get_min_score(input_df)
        max_score = self.data_preparer.get_max_score(input_df)

        prompt_formatter = PromptFormatter(annotation_template,
                                           endpoint_args["model"],
                                           {self.score_label: -1},
                                           [self.score_label],
                                           min_score,
                                           max_score)
        response_parser = ResponseParser()
        request_manager = RequestManager()
        scoring_manager = ScoringManager(experiment_output_path,
                                         prompt_formatter,
                                         response_parser,
                                         request_manager,
                                         min_score,
                                         max_score,
                                         request_args,
                                         endpoint_args,
                                         max_inputs_per_batch)

        return scoring_manager.score_input(input_df)

    def test_benchmark(self, benchmark_name, n_prompts_per_call, mode, n_samples):
        """Tests a benchmark using the annotation template associated with this class, including fetching prompt,
        fetching data, batching, submitting jobs and processing response, as well as logging to mlflow and logging both
        results and confusion matrix to an outputs folder. Also prints out confusion matrix to terminal

        :param benchmark_name: name of benchmark
        :type benchmark_name: str
        :param n_prompts_per_call: number of prompts per API call
        :type n_prompts_per_call: int
        :param mode: train/eval/test
        :type mode: str
        :param n_samples: total number of samples used for this benchmark (this is deterministic, [:n_samples] of data)
        :type n_samples: int
        :return: accuracy on this benchmark
        :rtype: float
        """
        benchmark_dir = f"{self.output_dir}/{benchmark_name}"
        output_fp = f"{benchmark_dir}/result.csv"
        confusion_matrix_fp = f"{benchmark_dir}/confusion.csv"

        # fetch annotation template
        annotation_template = self.get_prompt()

        # fetch dataset
        df = self.data_preparer.fetch_data(benchmark_name, mode, n_samples)

        # score prompt
        results = self.score_input_df(annotation_template, df, output_fp, n_prompts_per_call)

        # evaluate
        acc = self.metrics_generator.eval(results, confusion_matrix_fp)

        # log in mlflow
        mlflow.log_metric(f"{benchmark_name}-accuracy", acc)
        return acc
