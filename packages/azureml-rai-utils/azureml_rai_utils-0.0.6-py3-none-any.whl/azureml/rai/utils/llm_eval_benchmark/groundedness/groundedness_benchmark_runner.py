# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.rai.utils.llm_eval_benchmark.benchmarkutils.constants import LOG_RESULT_PATH, ENDPOINT_CONFIG_PATH, PROMPT_PATH
from azureml.rai.utils.llm_eval_benchmark.benchmarkutils.azure_connector import AzureConnector
from azureml.rai.utils.llm_eval_benchmark.common.experiment_runner import ExperimentRunner
import mlflow
import numpy as np


class GroundednessBenchmarkRunner:
    def __init__(self, mode: str, exp_name: str, endpoint_config_path=ENDPOINT_CONFIG_PATH, prompt_path=PROMPT_PATH, output_dir=LOG_RESULT_PATH):
        self.mode = mode
        self.exp_name = exp_name
        self.endpoint_config_path = endpoint_config_path
        self.prompt_path = prompt_path
        self.output_dir = output_dir
        self.benchmarks = ["groundedness-openai", "groundedness-fever", "groundedness-docnli", "groundedness-mctest", "groundedness-mnli", "groundedness-bing"]
        self.default_prompt_batch_size = 5
        self.azure_connector = AzureConnector()

    def exp_all_groundedness_benchmarks(self, sample_size_per_benchmark=-1):
        experiment_runner = ExperimentRunner(self.output_dir, self.azure_connector, self.endpoint_config_path, self.prompt_path)
        self.azure_connector.start_mlflow_experiment(self.exp_name)
        experiment_runner.log_template()
        acc_list = []
        for benchmark in self.benchmarks:
            print(benchmark)
            if benchmark == "groundedness-openai":
                # batch size 1 due to content filtering
                acc = experiment_runner.test_benchmark(benchmark, 1, self.mode, sample_size_per_benchmark)
                print(acc)
                acc_list.append(acc)
            else:
                acc = experiment_runner.test_benchmark(benchmark, self.default_prompt_batch_size, self.mode, sample_size_per_benchmark)
                print(acc)
                acc_list.append(acc)

        # get average
        groundedness_avg_acc = np.mean(acc_list)
        mlflow.log_metric("groundedness-mean-accuracy", groundedness_avg_acc)
        self.azure_connector.end_mlflow_experiment()
        return groundedness_avg_acc
