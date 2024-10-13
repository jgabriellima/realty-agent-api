import os

from api_template.external.core.autodiscovery import autodiscover_handlers
from api_template.external.core.manager import APIManager
from api_template.utils.semantic_search import SemanticSearch


class APISetup:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APISetup, cls).__new__(cls)
            cls._instance.api_manager = APIManager()
            cls._instance.handlers = cls._instance._initialize_handlers()
            cls._instance.semantic_search = SemanticSearch(
                collection_name="api_descriptions",
                cache_path=os.path.join(os.path.dirname(__file__), "data"),
            )
            cls._instance._index_api_descriptions()
        return cls._instance

    def _initialize_handlers(self):
        handler_directory = os.path.dirname(__file__) + "/../handlers"
        discovered_handlers = autodiscover_handlers(handler_directory)

        handlers_instances = {}
        for handler_class in discovered_handlers:
            handler_instance = handler_class(self.api_manager)
            handlers_instances[handler_class.__name__] = handler_instance

        return handlers_instances

    def get_handler(self, handler_name: str):
        if handler_name in self.handlers:
            return self.handlers[handler_name]
        raise ValueError(f"Handler {handler_name} not found.")

    def list_handlers(self):
        return list(self.handlers.keys())

    def get_api_manager(self):
        return self.api_manager

    def _index_api_descriptions(self):
        """
        Indexes the descriptions of the APIs in the semantic search engine.
        """
        specs = {}
        for handler_name, handler in self.handlers.items():
            api_adapter = self.api_manager.get_api(handler.service_name)
            operation_ids = api_adapter.list_operation_ids()
            for operation_id in operation_ids:
                description = api_adapter.get_operation_description(operation_id)
                specs[operation_id] = description

        self.semantic_search.index_specs(specs)

    def search(self, query):
        """
        Makes a search in the semantic search engine.
        :param query: Texto da query.
        :return: List of the most relevant APIs.
        """
        return self.semantic_search.search(query)
