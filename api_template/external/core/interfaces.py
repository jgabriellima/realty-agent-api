from abc import ABC, abstractmethod


class ExternalAPIClient(ABC):
    @abstractmethod
    def execute_operation(self, operation_id: str, params: dict = None, data: dict = None) -> dict:
        """
        Execute a specific operation based on the OpenAPI spec.
        """
        pass
