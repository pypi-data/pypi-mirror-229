# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

ANSWER = "answer"
CONTEXT = "context"
SCORE_LABEL = "rating"
IGNORE_FAILED_REQUESTS_COUNT = 10
MIN_REQUEST_COUNT = 3
ENDPOINT_CONFIG_PATH = "endpoint_config.json"
REQUEST_CONFIG_PATH = "./configs/request_config.json"
PROMPT_PATH = "prompt.txt"
LABEL_KEYS = ["rating"]
OUTPUT_SPLITTING_REGEX = r"[# ]*Task #*\d+:?"
LABEL_TRUE = "label_true"
CL100K_BASE = "cl100k_base"

LOG_TEMPLATE_PATH = "./outputs/prompt_template.txt"
LOG_RESULT_PATH = "./outputs/results"