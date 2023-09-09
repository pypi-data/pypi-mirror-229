# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests


class HTTPClientWithRetry:
    def __init__(self, n_retry, backoff_factor):
        self.attempts = n_retry

        retry_strategy = Retry(
            total=n_retry,
            status_forcelist=[104, 408, 409, 424, 429, 500, 502, 503, 504],
            backoff_factor=backoff_factor,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.client = requests.Session()
        self.client.mount("https://", adapter)
