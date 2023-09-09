# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import mlflow
import os
import json
from os.path import dirname
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


class AzureConnector:
    def __init__(self):
        self.aml_workspace_config_path = os.path.join(dirname(dirname(__file__)), os.path.join("configs", "aml_workspace_config.json"))
        self.ml_client = self.get_ml_client()

    def get_secret(self, keyvault_url, secret_name):
        """Gets secret from keyvault
        
        :param keyvault_url: url of keyvault
        :type keyvault_url: str
        :param secret_name: name of secret
        :type secret_name: str
        :return: secret value
        :rtype: str
        """
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=keyvault_url, credential=credential)
        secret = secret_client.get_secret(secret_name)
        return secret.value

    def get_ml_client(self):
        """Gets ml client from aml workspace config
        
        :return: ml client
        :rtype: MLClient"""
        f = open(self.aml_workspace_config_path)
        config_from_file = json.load(f)
        f.close()
        ml_client = MLClient(
            DefaultAzureCredential(),
            config_from_file["subscription_id"],
            config_from_file["resource_group"],
            config_from_file["workspace_name"]
        )
        return ml_client

    def start_mlflow_experiment(self, exp_name):
        """Starts mlflow experiment
        
        :param exp_name: name of experiment
        :type exp_name: str
        """
        ml_client = self.get_ml_client()
        mlflow_tracking_uri = ml_client.workspaces.get(ml_client.workspace_name).mlflow_tracking_uri
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        mlflow.set_experiment(exp_name)
        mlflow.start_run()

    def end_mlflow_experiment(self):

        """Ends mlflow experiment"""
        mlflow.end_run()
