# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from azureml.rai.utils.llm_eval_benchmark.benchmarkutils.constants import CL100K_BASE
module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.INFO)
tiktoken_installed = False
try:
    import tiktoken
    tiktoken_installed = True
except ImportError:
    module_logger.debug(
        'Could not import tiktoken, required if using tokenizer.')


class Tokenizer:
    """Handle LLM tokenizing using the tiktoken library."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.encoder_name = CL100K_BASE

    def count_tokens(self, input_str: str) -> int:
        # Count tokens, including special tokens like <|endofprompt|>
        if tiktoken_installed:
            return len(tiktoken.get_encoding(self.encoder_name).encode(input_str, allowed_special="all"))
        else:
            return 0
