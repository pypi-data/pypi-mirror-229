# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum


AUTOML_MLIMAGES_MLFLOW_MODEL_IDENTIFIER = (
    "azureml.automl.dnn.vision.common.mlflow.mlflow_model_wrapper."
    "MLFlowImagesModelWrapper'>"
)


class ModelTypes:
    FASTAI = "fastai"
    PYTORCH = "pytorch"
    PYFUNC = "pyfunc"
    HFTRANSFORMERS = "hftransformers"


class TaskType:
    TEXT_CLASSIFICATION = "text_classification"
    MULTILABEL_TEXT_CLASSIFICATION = "multilabel_text_classification"


class CredentialType(str, Enum):
    AZUREML_ON_BEHALF_OF_CREDENTIAL = "AzureMLOnBehalfOfCredential"
    DEFAULT_AZURE_CREDENTIAL = "DefaultAzureCredential"
    MANAGED_IDENTITY_CREDENTIAL = "ManagedIdentityCredential"
