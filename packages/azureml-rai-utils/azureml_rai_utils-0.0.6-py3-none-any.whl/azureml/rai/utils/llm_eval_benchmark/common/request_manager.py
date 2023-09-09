# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List
from azureml.rai.utils.llm_eval_benchmark.common.model.job import Job
from azureml.rai.utils.llm_eval_benchmark.benchmarkutils.http_client import HTTPClientWithRetry
from requests import Session
import time


class RequestManager:
    """RequestManager is responsible for everything related to the API call, handles different response failures (e.g. 400)"""

    def __init__(self):
        self.job_idx = 0

    @staticmethod
    def unpack_api_response_to_dict(response) -> dict:
        """Unpacks the response object from api to a dictionaty containing relevant info, discard header/session info etc.
        Currently only processes 200ok and 400 content filtering, raise exception for all other error codes

        :param response: requests Response object from post
        :type response: Response
        :return: parsed_response: a dictionary, if 200ok, contains samples (a list) and finish_reason (a list, one per sample).
        If 400 content filtering, return empty dictionary
        :rtype: dict
        """
        if response.status_code == 200:
            response_data = response.json()

            # check error
            for r in response_data["choices"]:
                if r["finish_reason"] == "error":
                    raise Exception(f"Encountered error in http response, although return code is 200: {response_data}")

            parsed_response = {
                "samples": [r["message"]["content"] for r in response_data["choices"]],
                "finish_reason": [r["finish_reason"] for r in response_data["choices"]],
            }

            return parsed_response

        elif response.status_code == 400:  # content moderation filtered out
            return {}
        else:
            raise Exception(f"Received unexpected HTTP status: {response.status_code} {response.text}")

    @staticmethod
    def send_post_request_for_job(job: Job, session: Session, endpoint_url: str, token: str):
        """Given a job, unpack request params and data, send to AOAI endpoint and get a response object back

        :param job: Job object containing prompt data and request parameters
        :type job: Job
        :param session: http session
        :type session: Session
        :param endpoint_url: url of AOAI endpoint
        :type endpoint_url: str
        :param token: token for AOAI
        :type token: str
        :return: response: a requests.Response object which is the result of post request
        :rtype: requests.Response
        """
        headers = {
            "Content-Type": "application/json",
            "api-key": token,
            "timeout_ms": "90000"
        }

        request_data = {
            "temperature": job.request_params["temperature"],
            "top_p": job.request_params["top_p"],
            "n": job.request_params["num_samples"],
            "max_tokens": job.request_params["max_tokens"],
            "frequency_penalty": job.request_params["frequency_penalty"],
            "presence_penalty": job.request_params["presence_penalty"],
            "messages": [{"role": "user", "content": job.prompt_data.prompt}],
        }

        return session.post(endpoint_url, headers=headers, json=request_data, timeout=300)

    def set_job_response(self, job: Job, session: Session, endpoint_url: str, token: str):
        """Given a job with request parameters and data, send a post request to AOAI and populate
        the response_data field

        :param job: Job object with request parameters
        :type job: Job
        :param session: http session
        :type session: Session
        :param endpoint_url: AOAI endpoint url
        :type endpoint_url: str
        :param token: AOAI token
        :type token: str
        :return: job: Job object with populated response_data field
        :rtype: Job
        """
        time_start = time.time()
        raw_response = self.send_post_request_for_job(job, session, endpoint_url, token)
        response_dict = self.unpack_api_response_to_dict(raw_response)
        time_taken = time.time() - time_start
        response_dict["response_time_sec"] = time_taken
        job.response_data = response_dict
        return job

    def get_job_batch_response(
        self,
        jobs: List[Job],
        token: str,
        endpoint_url: str,
        api_call_delay_sec: float = 0.5,
        api_call_retry_backoff_factor: int = 0.1,
        api_call_retry_max_count: int = 10
    ) -> List[Job]:
        """Given a list of jobs, schedule API calls with appropriate delay and populate each job with response

        :param jobs: a list of jobs
        :type jobs: list
        :param token: AOAI token
        :type token: str
        :param endpoint_url: url to the endpoint
        :type endpoint_url: str
        :param api_call_delay_sec: delay time for api call
        :type api_call_delay_sec: float
        :param api_call_retry_backoff_factor: backoff factor for api call delay
        :type api_call_retry_backoff_factor: int
        :param api_call_retry_max_count: max number of counts per API call
        :type api_call_retry_max_count: int
        :return: jobs: a list of jobs with response_data populated
        :rtype: list
        """

        outputs = []
        if len(jobs) == 0:
            return outputs

        httpClient = HTTPClientWithRetry(
            n_retry=api_call_retry_max_count,
            backoff_factor=api_call_retry_backoff_factor,
        )

        with httpClient.client as session:
            for job in jobs:
                outputs.append(self.set_job_response(job, session, endpoint_url, token))
                # Sleep between consecutive requests to avoid rate limit
                time.sleep(api_call_delay_sec)
        return outputs
