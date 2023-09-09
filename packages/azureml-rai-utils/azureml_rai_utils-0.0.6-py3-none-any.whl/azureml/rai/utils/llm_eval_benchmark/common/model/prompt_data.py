# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Dict


class PromptData:
    """Class for storing prompt information."""

    def __init__(
        self,
        input_idx: List[int],
        input_examples: List[dict],
        prompt: str,
        n_tokens_estimate: int,
    ):
        """for now prompt is a fixed input message for all input samples, later this should be a function depends on input"""
        self.input_idx = input_idx
        self.input_examples = input_examples
        self.prompt = prompt
        self.n_tokens_estimate = n_tokens_estimate