# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from abc import abstractmethod, ABC
import numpy as np
import pandas as pd

from functools import partial

from azureml.rai.utils.constants import TaskType

try:
    import azureml.evaluate.mlflow as aml_mlflow
    aml_mlflow_installed = True
except ImportError:
    aml_mlflow_installed = False


_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def get_predictor(task):
    """Get predictor.

    :param task: model task type
    :type task: TaskType
    :return: model wrapper with predict and predict_proba methods
    :rtype: mlflow model wrapper
    """
    predictor_map = {
        TaskType.TEXT_CLASSIFICATION: TextClassifier,
        TaskType.MULTILABEL_TEXT_CLASSIFICATION: TextClassifier
    }
    return predictor_map.get(task)


class BasePredictor(ABC):
    """Abstract Class for Predictors."""

    def __init__(self, mlflow_model):
        """__init__.

        :param mlflow_model: input mlflow model with different flavors
        :type mlflow_model: mlflow model
        """
        self.is_torch = False
        self.is_hf = False
        if mlflow_model.metadata.flavors.get(aml_mlflow.pytorch.FLAVOR_NAME):
            self.is_torch = True
        if mlflow_model.metadata.flavors.get(
                aml_mlflow.hftransformers.FLAVOR_NAME):
            self.is_hf = True
        if mlflow_model.metadata.flavors.get(
                aml_mlflow.hftransformers.FLAVOR_NAME_MLMODEL_LOGGING):
            self.is_hf = True

        if self.is_torch:
            self.model = mlflow_model._model_impl
        else:
            self.model = mlflow_model
        super().__init__()

    def _ensure_base_model_input_schema(self, X_test):
        input_schema = self.model.metadata.get_input_schema()
        if self.is_hf and input_schema is not None:
            if input_schema.has_input_names():
                # make sure there are no missing columns
                input_names = input_schema.input_names()
                expected_cols = set(input_names)
                # Hard coding logic for converting data to input string
                # for base models
                if len(expected_cols) == 1 and \
                        input_names[0] == "input_string":
                    if isinstance(X_test, np.ndarray):
                        X_test = {input_names[0]: X_test}
                    elif isinstance(X_test, pd.DataFrame) and \
                            len(X_test.columns) == 1:
                        X_test.columns = input_names
                    elif isinstance(X_test, dict) and len(X_test.keys()) == 1:
                        key = list(X_test.keys())[0]
                        X_test[input_names[0]] = X_test[key]
                        X_test.pop(key)

    def _ensure_model_on_cpu(self):
        """Ensure model is on cpu.

        :param model: input model
        :type model: mlflow model
        """
        if self.is_hf:
            if hasattr(self.model._model_impl, "hf_model"):
                self.model._model_impl.hf_model.to("cpu")
            else:
                _logger.info("hf_model not found in mlflow model")
        elif self.is_torch:
            import torch
            if isinstance(self.model._model_impl, torch.nn.Module):
                self.model._model_impl.to("cpu")
            else:
                _logger.info("Torch model is not of type nn.Module")


class PredictWrapper(BasePredictor):
    """Abstract class for predict based models."""

    @abstractmethod
    def predict(self, X_test, **kwargs):
        """Abstract predict.

        :param X_test: test data
        :type X_test: pandas.DataFrame or numpy.ndarray
        """
        pass


class PredictProbaWrapper(BasePredictor):
    """Abstract class for predict_proba based models."""

    @abstractmethod
    def predict_proba(self, X_test, **kwargs):
        """Abstract Predict proba.

        :param X_test: test data
        :type X_test: pandas.DataFrame or numpy.ndarray
        """
        pass


class TextClassifier(PredictWrapper, PredictProbaWrapper):
    """Model wrapper for text classification models or
    multilabel text classification model."""

    def predict(self, X_test, **kwargs):
        """Predict labels.

        :param X_test: test data
        :type: pandas.DataFrame or numpy.ndarray
        :return: model predicted values
        :rtype: numpy.ndarray
        """

        # The HF flavor does not support List or Dict input types as of now.
        # Convert List or Dict input to a pandas.DataFrame or a numpy.ndarray
        X_test_type = type(X_test)
        if X_test_type == list or X_test_type == dict:
            X_test = pd.DataFrame(X_test)

        predict_fn, _ = self._extract_predict_fn()
        try:
            y_pred = predict_fn(X_test, **kwargs)
        except TypeError:
            y_pred = predict_fn(X_test)
        except RuntimeError as re:
            device = kwargs.get("device", -1)
            if device != -1:
                _logger.warning("Predict failed on GPU. Falling back to CPU")
                self._ensure_model_on_cpu()
                kwargs["device"] = -1
                y_pred = predict_fn(X_test, **kwargs)
            else:
                raise re

        y_transformer = kwargs.get("y_transformer", None)
        if y_transformer is not None:
            y_pred = y_transformer.transform(y_pred).toarray()

        return np.array(y_pred[0])

    def predict_proba(self, X_test, **kwargs):
        """Get prediction probabilities.

        :param X_test: test data
        :type X_test: pandas.DataFrame or numpy.ndarray
        :return: model predicted probabilities
        :rtype: numpy.array
        """

        # The HF flavor does not support List or Dict input types as of now.
        # Convert List or Dict input to a pandas.DataFrame or a numpy.ndarray
        X_test_type = type(X_test)
        if X_test_type == list or X_test_type == dict:
            X_test = pd.DataFrame(X_test)

        _, pred_proba_fn = self._extract_predict_fn()
        if self.is_torch or self.is_hf:
            try:
                y_pred_proba = pred_proba_fn(X_test, **kwargs)
            except RuntimeError as re:
                device = kwargs.get("device", -1)
                if device != -1:
                    _logger.warning("Predict Proba failed on GPU. \
                                    Falling back to CPU")
                    self._ensure_model_on_cpu()
                    kwargs["device"] = -1
                    y_pred_proba = pred_proba_fn(X_test, **kwargs)
                else:
                    raise re
        else:
            y_pred_proba = pred_proba_fn(X_test)
        return np.array(y_pred_proba)

    def _alternate_predict(self, X_test, **kwargs):
        device = kwargs.get("device", -1)
        multilabel = kwargs.get("multilabel", False)
        if self.is_torch or self.is_hf:
            preds = self.model.predict(X_test, device)
        else:
            preds = self.model.predict(X_test)
        if len(preds.shape) > 1:
            if multilabel:
                preds = np.where(preds > 0.5, 1, 0)
            preds = np.argmax(preds, axis=1)
        else:
            preds = (preds >= 0.5).all(1)
        return preds

    def _extract_predict_fn(self):
        if self.is_torch:
            return self._alternate_predict, self.model.predict

        predict_fn = self.model.predict
        predict_proba_fn = None

        raw_model = self.model._model_impl
        if raw_model is not None:
            predict_fn = raw_model.predict
            predict_proba_fn = getattr(raw_model, "predict_proba", None)

            try:
                import xgboost

                if isinstance(raw_model, xgboost.XGBModel):
                    predict_fn = partial(predict_fn, validate_features=False)
                    if predict_proba_fn is not None:
                        predict_proba_fn = partial(predict_proba_fn,
                                                   validate_features=False)
            except Exception:
                pass

        if predict_proba_fn is None:
            predict_fn = self._alternate_predict
            predict_proba_fn = raw_model.predict

        return predict_fn, predict_proba_fn
