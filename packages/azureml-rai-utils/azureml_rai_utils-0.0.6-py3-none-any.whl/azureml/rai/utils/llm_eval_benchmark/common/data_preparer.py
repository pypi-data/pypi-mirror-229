# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import mltable
from azureml.rai.utils.llm_eval_benchmark.benchmarkutils.azure_connector import AzureConnector
from azureml.rai.utils.llm_eval_benchmark.benchmarkutils.constants import LABEL_TRUE


class DataPreparer:
    """DataPreparer is responsible for fetching data from aml and doing data preparation related work"""
    def __init__(self, azure_connector: AzureConnector):
        self.ml_client = azure_connector.ml_client

    def fetch_data(self, dataset_name, mode, n_samples):
        """Fetches dataset from aml using registered name. Also makes sure label_true is int type

        :param dataset_name: name of dataset
        :type dataset_name: str
        :param mode: train/eval/test
        :type mode: str
        :param n_samples: number of samples to take from this dataset, default value -1 means
        taking full dataset. This is deterministic, the data is already randomly shuffled and
        taking k samples means fetching first k rows
        :type n_samples: int
        :return: a pandas dataframe of specified size (or full train/eval/test set)
        :rtype: dataframe
        """
        dataset_fullname = f"{dataset_name}-{mode}"
        data_asset = self.ml_client.data.get(name=dataset_fullname, label="latest")
        # the table from the data asset id
        tbl = mltable.load(f"azureml:/{data_asset.id}")
        # load into pandas
        df = tbl.to_pandas_dataframe()
        df[LABEL_TRUE] = df[LABEL_TRUE].astype(int)
        if n_samples > 0:
            return df.iloc[:n_samples]
        return df

    def get_min_score(self, df):
        """
        Get minimum score for a given dataframe, as defined in "label_true" column

        :param df: input dataframe, label_true column is already converted to integer type
        :type df: dataframe
        :return: min score
        :rtype: int
        """
        return df[LABEL_TRUE].min()

    def get_max_score(self, df):
        """
        Get maximum score for a given dataframe, as defined in "label_true" column

        :param df: input dataframe, label_true column is already converted to integer type
        :type df: dataframe
        :return: max score
        :rtype: int
        """
        return df[LABEL_TRUE].max()
