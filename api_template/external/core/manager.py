from api_template.external.core.adapters import GenericAPIAdapter


class APIManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(APIManager, cls).__new__(cls)
            cls._instance._apis = {}
        return cls._instance

    def register_api(self, service_name: str, base_url: str, spec_path: str, headers: dict = None):
        if service_name not in self._apis:
            spec = GenericAPIAdapter.load_spec(spec_path)
            self._apis[service_name] = GenericAPIAdapter(
                base_url=base_url, spec=spec, headers=headers
            )
            print(f"self._apis[{service_name}]: {self._apis[service_name]}")

    def get_api(self, service_name: str) -> GenericAPIAdapter:
        if service_name not in self._apis:
            raise ValueError(f"API {service_name} is not registered.")
        return self._apis[service_name]

    def list_apis(self):
        return list(self._apis.keys())

    def execute_operation(
        self, service_name: str, operation_id: str, params: dict = None, data: dict = None
    ):
        api = self.get_api(service_name)
        return api.execute_operation(operation_id, params=params, data=data)
