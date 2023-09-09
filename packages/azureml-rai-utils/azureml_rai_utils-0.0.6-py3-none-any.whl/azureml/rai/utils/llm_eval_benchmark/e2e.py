# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import click
import shutil
from os import mkdir
import logging
from azureml.rai.utils.llm_eval_benchmark.groundedness.groundedness_benchmark_runner import GroundednessBenchmarkRunner

# command line args
# argv[1] area (groundedness / contentharm/ ...)
# argv[2] number of samples per benchmark
# argv[3] name of experiment
# argv[4] name of txt containing prompt
# argv[5] name of model

# we do not enable repeated sampling and CI in local mode
# because the expected sample size in this mode is not large and CI is likely to be large and uninformative
# for now, not enabling selective datasets - always run on all datasets
# for now, not enabling user-input batch size bc this can have negative effect on results
# for now, fixing boilerplate for batching

# if experiment for any benchmark crashes, skip and keep running others. All results are periodically saved in csv
# upon failure direct user to the csv, but still emit metrics of the good benchmarks to aml

# locally will create an experiment folder with 2 subdirectories: datasets and results. datasets will be downloaded from
# adls for experiments and results serve as a checkpoint, storing every sample's true label and gpt label incrementally
# inside results, each experiment has a folder with name exp_<guid>, so that it will not be overwritten by later experiments

@click.command()
@click.option('--area', type=str, help='groundedness/contentharm/...')
@click.option('--mode', type=str, help='train/eval/test')
@click.option('--samples_per_benchmark', type=int, help='number of samples per benchmark', default=-1, required=False)
@click.option('--experiment_name', type=str, help='name of experiment')
@click.option('--prompt_path', type=str, help='file path of prompt')
@click.option('--endpoint_config_path', type=str, help='file path of endpoint config including model name, url, token')
def main(area, mode, samples_per_benchmark, experiment_name, prompt_path, endpoint_config_path):
    # logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("azureml").setLevel(logging.WARNING)

    # clear output folder
    try:
        shutil.rmtree('./outputs')
    except Exception:
        pass
    mkdir('./outputs')

    if area == "groundedness":
        groundedness_benchmark_runner = GroundednessBenchmarkRunner(mode=mode, exp_name=experiment_name, endpoint_config_path=endpoint_config_path, prompt_path=prompt_path)
        groundedness_benchmark_runner.exp_all_groundedness_benchmarks(samples_per_benchmark)


if __name__ == '__main__':
    main()
