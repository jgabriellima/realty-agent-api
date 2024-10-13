import os

from api_template.external.core.base import BaseHandler
from api_template.external.core.manager import APIManager


class TavilyHandler(BaseHandler):
    def __init__(self, api_manager: APIManager):
        super().__init__(api_manager)

        self.service_name = "tavily_service"
        self.base_url = "https://api.tavily.com"
        self.spec_path = os.path.join(os.path.dirname(__file__), "openapi.yaml")
        self.service_description = (
            "Tavily Search API is a search engine optimized for LLMs, aimed at efficient, quick "
            "and persistent search results. Unlike other search APIs such as Serp or Google, "
            "Tavily focuses on optimizing search for AI developers and autonomous AI agents."
        )
        self.required_headers = []

        # Required to register the API
        self.register_api()

    def search_internet(self, query: str):
        """
        Search the internet for a specific query.

        Data Parameters:
        search_depth (int): The depth of the search. Default is 1.
        topic (str): The topic of the search. Default is "general" and "news".

        :param query:
        :return:
        """
        return self.execute_operation(
            operation_id="search",
            data={"query": query, "api_key": self.get_env_vars("TAVILY_API_KEY")},
        )
