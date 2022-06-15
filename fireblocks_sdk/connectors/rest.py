import json
from typing import Dict, Union

import requests

from fireblocks_sdk import FireblocksApiException
from fireblocks_sdk.entities.api_response import ApiResponse
from fireblocks_sdk.sdk_token_provider import SdkTokenProvider


class RestConnector:
    def __init__(self, token_provider: SdkTokenProvider, base_url: str, api_key: str, timeout: int) -> None:
        self.token_provider = token_provider
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout

    def _generate_headers(self, path, body: Union[Dict, None] = None, idempotency_key: str = None):
        token = self.token_provider.sign_jwt(path, json.dumps(body) if body else json.dumps({}))
        headers = {
            "X-API-Key": self.api_key,
            "Authorization": f"Bearer {token}"
        }

        if idempotency_key:
            headers.update({"Idempotency-Key": idempotency_key})

        return headers

    def get(self, path) -> ApiResponse:
        response = requests.get(self.base_url + path,
                                headers=self._generate_headers(path), timeout=self.timeout)
        return self.handle_response(response)

    def delete(self, path) -> ApiResponse:
        response = requests.delete(
            self.base_url + path, headers=self._generate_headers(path), timeout=self.timeout)
        return self.handle_response(response)

    def post(self, path, body=Union[Dict, None], idempotency_key=None) -> ApiResponse:
        response = requests.post(self.base_url + path, headers=self._generate_headers(path, body, idempotency_key),
                                 json=body or {}, timeout=self.timeout)
        return self.handle_response(response)

    def put(self, path, body: Union[Dict, None] = None) -> ApiResponse:
        headers = self._generate_headers(path, body)
        headers.update({"Content-Type": "application/json"})
        response = requests.put(self.base_url + path, headers=headers,
                                data=json.dumps(body), timeout=self.timeout)
        return self.handle_response(response)

    @staticmethod
    def handle_response(response) -> ApiResponse:
        if response.status_code >= 300:
            raise FireblocksApiException(
                f"Got an error from fireblocks server: {response.content}")

        return ApiResponse(response.status_code, response.json(), response.headers)
