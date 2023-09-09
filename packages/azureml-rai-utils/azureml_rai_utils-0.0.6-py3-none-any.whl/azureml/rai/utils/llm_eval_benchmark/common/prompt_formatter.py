# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.rai.utils.llm_eval_benchmark.benchmarkutils.tokenizer import Tokenizer
from azureml.rai.utils.llm_eval_benchmark.common.model.prompt_data import PromptData
from azureml.rai.utils.llm_eval_benchmark.common.model.input_sample import InputSample
from azureml.rai.utils.llm_eval_benchmark.benchmarkutils.constants import CONTEXT, ANSWER, OUTPUT_SPLITTING_REGEX
import pandas as pd
import re
from collections import OrderedDict
from typing import Dict, Generator, List, Optional, Tuple, Union
import logging
module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.INFO)
try:
    import jinja2
except ImportError:
    module_logger.debug(
        'Could not import jinja2, required if using prompt formatter.')
try:
    import json5
except ImportError:
    module_logger.debug(
        'Could not import json5, required if using prompt formatter.')


class PromptFormatter:
    """PromptFormatter is responsible for everything related to prompt batching, encoding input (from dataframe), splitting
    and decoding.
    """
    def __init__(
        self,
        labeling_guidelines: str,
        model_name: str,
        unparsable_default_value: dict,  # e.g. {"rating":-1}
        label_keys: List[str],
        min_score: int,
        max_score: int,
        input_keys: List[str] = [CONTEXT, ANSWER],
        min_input_examples: int = 1,
        max_tokens: int = 4000
    ):
        """Batches prompts according to limits."""
        self.labeling_guidelines = jinja2.Template(
            self.format_batch_template(labeling_guidelines), undefined=jinja2.StrictUndefined
        )
        self.model_name = model_name
        self.max_tokens = max_tokens  # make this dynamic
        self.min_input_examples = min_input_examples
        self.label_keys = label_keys
        self.min_score = min_score
        self.max_score = max_score
        self.input_keys = input_keys
        self.tokenizer = Tokenizer(
            model_name=model_name,
        )
        # check if ill format value has all label keys
        for key in label_keys:
            if key not in unparsable_default_value:
                raise Exception("ill format value should be a dictionary with all label keys, e.g. \"rating\": 0")

        for key in unparsable_default_value.keys():
            if key not in label_keys:
                raise Exception("ill format value should not contain keys not in the label keys")

        self.unparsable_default_output_dict = unparsable_default_value

    @staticmethod
    def format_batch_template(
        custom_prompt: str
    ) -> str:
        """
        Add batching prefix and suffix to generate batch template given guidelines

        :param custom_prompt: the prompt provided by user
        :type custom_prompt: str
        :return: batch prompt based on custom prompt
        :rtype: str
        """
        # if provided prompt includes reminder, put it in the end
        custom_prompt_guideline = custom_prompt
        reminder = ""
        if "Reminder" in custom_prompt:
            custom_prompt_guideline = custom_prompt.split("Reminder")[0]
            reminder = f"Reminder: {custom_prompt.split('Reminder')[1]}"
        
        TASK_INJECTION_JINJA_TEMPLATE = """
        {% for sample in input_samples %}
        ## Task #{{ sample.index }}:
        {{ sample.encoded_json }}
        {% endfor %}
        """

        prompt = "\n\n".join([
            custom_prompt_guideline,
            "## Actual Tasks",
            TASK_INJECTION_JINJA_TEMPLATE,
            reminder,
            "## Actual Task Output:",
            ""
        ])
        return prompt

    @staticmethod
    def encode_example(
        example: Dict[str, Union[int, bool, str]],
        key_order: Optional[List[str]] = None,
        indent: Optional[int] = 2,
    ) -> str:
        """
        Encode examples into JSON.

        :param example: example to encode
        :type example: dict
        :param key_order: ordering of keys printed to string
        :type key_order: Optional[list]
        :param indent: number of spaces indented at each level
        :type indent: Optional[int]
        :return: encoded example in json format
        :rtype: str
        """
        if key_order:
            example = OrderedDict([(key, example[key]) for key in key_order])

        # Dump JSON with keys double-quoted and final comma removed
        return json5.dumps(
            example, indent=indent, quote_keys=True, trailing_commas=False
        )

    def build_prompt(
        self,
        input_examples: List[Dict[str, str]]
    ) -> str:
        """Build prompt from input_examples. Encode examples into JSON format.

        :param input_examples: list of input examples
        :type input_examples: list
        :return: constructed prompt
        :rtype: str
        """
        input_samples = [
            InputSample(
                index=i,
                encoded_json=self.encode_example(input_example, self.input_keys),
            )
            for (i, input_example) in enumerate(input_examples, start=1)
        ]

        return self.labeling_guidelines.render(
            input_samples=input_samples,
            min_score=self.min_score,
            max_score=self.max_score
        )

    def build_prompt_with_limits(
        self,
        input_data: List[Dict[str, str]]
    ) -> Tuple[str, int, int]:
        """Reduces batch examples until the prompt is within token limits

        :param input_data: list of input examples
        :type input_data: list

        return: prompt: constructed prompt, n_tokens: number of tokens within the prompt, input_examples: number of input examples that can be fit
        rtype: tuple[str, int, int]
        """
        # build prompt with all examples
        prompt = self.build_prompt(input_data)
        n_tokens = self.tokenizer.count_tokens(prompt)

        # reduce input examples iteratively until minimum is hit
        while n_tokens > self.max_tokens and len(input_data) > self.min_input_examples:
            input_data = input_data[:-1]
            prompt = self.build_prompt(input_data)
            n_tokens = self.tokenizer.count_tokens(prompt)

        return prompt, n_tokens, len(input_data)

    def generate_prompts(
        self,
        input_data_df: pd.DataFrame,
        max_inputs: int
    ) -> Generator[PromptData, None, None]:
        """Generate prompts from input data. Fitting as many examples as possible into the prompt
        while staying below token limits and below the max_inputs limit. For example, input has 1000
        samples in total but every batch can only fit 3-4 based on token limit, then will return a generator
        with 250-330 elements, each is a batch, based on the exact length of each prompt.

        :param input_data_df: DataFrame of input examples
        :type input_data_df: dataframe
        :param max_inputs: maximum number of input examples to use
        :type max_inputs: int

        :return: prompt_data: list of PromptDatas containing the prompt, the index of input examples, and the number of tokens.
        :rtype: list[PromptData]
        """
        input_data = input_data_df.to_dict(orient="records")
        input_data_length = len(input_data)
        next_index = 0
        stop_index = min(max_inputs, input_data_length)

        while next_index < input_data_length:
            input_idx = list(range(next_index, stop_index))
            input_examples = input_data[next_index:stop_index]

            # Build prompt given input, shot, and token limits
            prompt, n_tokens, n_inputs = self.build_prompt_with_limits(
                input_examples
            )

            # send prompt
            next_index += n_inputs
            stop_index = min(next_index + max_inputs, input_data_length)
            input_idx = input_idx[:n_inputs]
            input_examples = input_examples[:n_inputs]
            yield PromptData(
                input_idx=input_idx,
                input_examples=input_examples,
                prompt=prompt,
                n_tokens_estimate=n_tokens,
            )

    def decode_example(
        self,
        example: str
    ) -> Dict[str, Union[int, bool, str]]:
        """Decode example from an encoding format. Fails if label key does not match the key in prompt formatter
        (which is used to encode). Upon failure, return the default ill format output dict defined in prompt formatter
        
        :param example: example to decode
        :type example: str
        :return: decoded example in dictionary format
        :rtype: dict
        """
        example = example.strip()
        start = example.rfind("{")  # note this wouldn't work if returned result is a dictionary
        end = example.rfind("}")
        if start == -1:
            print(f"Unparsable output: no left curly brace in: {example}")
            return self.unparsable_default_output_dict
        if end == -1:
            print(f"Unparsable output: no right curly brace in: {example}")
            return self.unparsable_default_output_dict

        try:
            decoded = json5.loads(example[start:end + 1])
        except Exception:
            print(f"Unparsable output: cannot load json in: {example}")
            return self.unparsable_default_output_dict

        # check if label keys are in example
        for label_key in self.label_keys:
            if label_key not in decoded:
                print(f"Unparsable output: did not find key {label_key}: {example}")
                return self.unparsable_default_output_dict
        return decoded

    def split_output_examples(self, output_str: str, expected_output_number: int) -> List[str]:
        """Attempt to split the output into a list of examples. If fails, or if number of elements
        does not match expectation, return a list of empty string with expected length

        :param output_str: output examples
        :type output_str: str
        :param expected_output_number: expected number of outputs that we should yield
        :type expected_output_number: int
        :return: output_examples: list of output examples of size expected_output_number
        :rtype: list
        """
        try:
            output_str = output_str.strip()
            output_examples = [
                ex.strip()
                for ex in re.split(OUTPUT_SPLITTING_REGEX, output_str)
                if ex.strip()
            ]
        except Exception:
            print(f"Splitting failed for {output_str}")
            return [""] * expected_output_number

        if len(output_examples) != expected_output_number:
            print(f"Splitting failed - not equal to expected number for {output_str}")
            return [""] * expected_output_number

        return output_examples
