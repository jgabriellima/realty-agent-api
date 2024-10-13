import json
import logging

import requests
import yaml
from cachetools import TTLCache
from requests.exceptions import HTTPError

from api_template.external.core.interfaces import ExternalAPIClient
from api_template.external.util import deep_freeze_args

logger = logging.getLogger(__name__)


def generate_description_from_data(data: dict) -> str:
    """
    Generate a description based on the data provided.
    :param data:
    :return:
    """
    try:
        import marvin

        @marvin.fn
        def generate_description(input: str) -> str:
            """
            Generate a concise and objective description for this endpoint based on the {input} provided.
            <what this endpoint does>
            <summary of what it returns>
            <what it requires>
            :param input:
            :return:
            """

        return generate_description(json.dumps(data))

    except ImportError:
        return data.get("description", "summary")


class GenericAPIAdapter(ExternalAPIClient):
    def __init__(self, base_url: str, spec: dict, headers: dict = None):
        self.base_url = base_url
        self.spec = spec
        self.headers = headers or {}
        self.cache = TTLCache(maxsize=100, ttl=300)

    @deep_freeze_args
    def execute_operation(self, operation_id: str, params: dict = None, data: dict = None):
        """
        Execute a specific operation based on the OpenAPI spec.
        :param operation_id:
        :param params:
        :param data:
        :return:
        """
        try:
            method, path = operation_id.split(" ", 1)
        except ValueError:
            method, path = self.get_method_path_by_operation_id(operation_id)

        operation = self.spec["paths"].get(path)
        if not operation:
            logger.error(f"Path {path} not found in the API spec.")
            raise ValueError(f"Path {path} not found in the API spec.")

        method = method.lower()
        operation_data = operation.get(method)
        if not operation_data:
            logger.error(f"Method {method.upper()} not found for path {path}.")
            raise ValueError(f"Method {method.upper()} not found for path {path}.")

        url = f"{self.base_url}{path}"

        try:
            response = self._make_request(method, url, params=params, data=data)
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logger.error(f"Other error occurred: {err}")
            raise

    def _make_request(self, method, url, params=None, data=None):
        """
        Make a request to the specified URL using the given method.
        :param method:
        :param url:
        :param params:
        :param data:
        :return:
        """
        request_method = {
            "get": requests.get,
            "post": requests.post,
            "put": requests.put,
            "delete": requests.delete,
        }.get(method)

        if not request_method:
            raise ValueError(f"Unsupported method {method} for operation {url}")

        return request_method(url, headers=self.headers, params=params, json=data)

    @staticmethod
    def load_spec(spec_path: str) -> dict:
        """
        Load the OpenAPI spec from the specified file path.
        :param spec_path:
        :return:
        """
        with open(spec_path, "r") as spec_file:
            return yaml.safe_load(spec_file)

    def get_method_path_by_operation_id(self, operation_id: str) -> tuple:
        for path, operations in self.spec.get("paths", {}).items():
            for method, operation_data in operations.items():
                # Fallback handling
                potential_operation_id = operation_data.get(
                    "operationId", f"{method.upper()} {path}"
                )
                if potential_operation_id == operation_id:
                    return method, path

    def get_operation_input(self, operation_id: str) -> dict:
        """
        Returns the expected input parameters and request body schema for the specified operation_id.
        Uses method + path as fallback if operationId is not present.
        """
        for path, operations in self.spec.get("paths", {}).items():
            for method, operation_data in operations.items():
                # Fallback handling
                potential_operation_id = operation_data.get(
                    "operationId", f"{method.upper()} {path}"
                )
                if potential_operation_id == operation_id:
                    # Get the parameters (path, query, header, etc.)
                    parameters = operation_data.get("parameters", [])

                    # Get the request body (if it's a POST, PUT, etc.)
                    request_body = operation_data.get("requestBody", {})

                    # Extract relevant details for each type of input
                    inputs = {
                        "parameters": [
                            {
                                "name": param.get("name"),
                                "in": param.get("in"),  # path, query, header, etc.
                                "required": param.get("required", False),
                                "schema": param.get("schema", {}),
                            }
                            for param in parameters
                        ],
                        "requestBody": request_body.get("content", {})
                        .get("application/json", {})
                        .get("schema", {}),
                    }
                    return inputs

        raise ValueError(f"Operation {operation_id} not found in the API spec.")

    def list_operation_ids(self) -> list:
        """
        Returns a list of available operations. If 'operationId' is missing, fallback to using 'method' and 'path'.
        """
        operation_ids = []
        for path, operations in self.spec.get("paths", {}).items():
            for method, operation_data in operations.items():
                operation_id = operation_data.get("operationId")
                if not operation_id:
                    # Fallback: use method and path as the operation identifier
                    operation_id = f"{method.upper()} {path}"
                operation_ids.append(operation_id)
        return operation_ids

    def get_operation_description(self, operation_id: str) -> str:
        """
        Returns the description for a specific operation based on the operation_id or fallback identifier.
        """
        for path, operations in self.spec.get("paths", {}).items():
            for method, operation_data in operations.items():
                # Fallback handling
                potential_operation_id = operation_data.get(
                    "operationId", f"{method.upper()} {path}"
                )
                if potential_operation_id == operation_id:
                    return operation_data.get(
                        "description", generate_description_from_data(operation_data)
                    )
        raise ValueError(f"Operation {operation_id} not found in the API spec.")
