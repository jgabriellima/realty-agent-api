import os

from api_template.external.core.manager import APIManager


class BaseHandler:
    def __init__(self, api_manager: APIManager):
        self.api_manager = api_manager
        self.__spec_path = os.path.join(os.path.dirname(__file__), "openapi.yaml")
        self.__service_name = None
        self.__service_description = None
        self.__required_headers = []
        self.__base_url = None
        self.__headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def execute_operation(self, operation_id: str, params: dict = None, data: dict = None):
        """
        Execute any operation by providing the service name, operation_id, and optional parameters and data.
        """
        return self.api_manager.execute_operation(
            self.service_name, operation_id, params=params, data=data
        )

    def get_operation_input(self, service_name: str, operation_id: str):
        """
        Get the input requirements for a specific operation.
        """
        api_adapter = self.api_manager.get_api(service_name)
        return api_adapter.get_operation_input(operation_id)

    def check_headers(self, headers):
        for header in self.required_headers:
            if header not in headers:
                raise ValueError(f"Header {header} is required for this operation.")

    def register_api(self, spec_path=None):
        if not self.api_manager:
            raise ValueError("API Manager is not set.")

        self.api_manager.register_api(
            service_name=self.service_name,
            base_url=self.__base_url,
            spec_path=spec_path or self.__spec_path,
            headers=self.headers,
        )
        self.check_headers(self.headers)

    def setup_env_var(self, env_var=None, default_value=None):
        """
        Setup the environment variable or return the default value.
        :param env_var:
        :param default_value:
        :return:
        """
        if env_var and env_var not in os.environ:
            os.environ[env_var] = default_value
        return os.environ[env_var]

    def get_env_vars(self, env_var=None, default_value=None):
        """
        Get the required environment variable or return the default value.
        :param env_var:
        :param default_value:
        :return:
        """
        if env_var and env_var not in os.environ:
            if not default_value:
                raise ValueError(f"Environment variable {env_var} is required.")
            return default_value
        return os.environ[env_var]

    @property
    def service_name(self):
        return self.__service_name

    @service_name.setter
    def service_name(self, value):
        self.__service_name = value

    @property
    def service_description(self):
        return self.__service_description

    @service_description.setter
    def service_description(self, value):
        self.__service_description = value

    @property
    def required_headers(self):
        return self.__required_headers

    @required_headers.setter
    def required_headers(self, value):
        self.__required_headers = value

    @property
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self, value):
        self.__headers = value

    @property
    def spec_path(self):
        return self.__spec_path

    @spec_path.setter
    def spec_path(self, value):
        self.__spec_path = value

    @property
    def base_url(self):
        return self.__base_url

    @base_url.setter
    def base_url(self, value):
        self.__base_url = value
