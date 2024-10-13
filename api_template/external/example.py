"""
Example of how to use the API setup to discover handlers and execute operations
"""
from api_template.api.v1.schemas.websearch_schema import WebSearchData, WebSearchResponse
from api_template.external.core.setup import APISetup


def init():
    api_setup = APISetup()

    discovered_handlers = api_setup.list_handlers()
    print("=" * 100)
    print("Handlers descobertos:", discovered_handlers)

    for handler_name in discovered_handlers:
        handler = api_setup.get_handler(handler_name)
        print(handler)
        api_adapter = api_setup.get_api_manager().get_api(handler.service_name)

        operation_ids = api_adapter.list_operation_ids()
        print(f"\nOperações do handler {handler_name}:")

        for operation_id in operation_ids:
            print(f"operation_id: {operation_id}")
            description = api_adapter.get_operation_description(operation_id)
            print(f"- {operation_id}: {description}")

            inputs = api_adapter.get_operation_input(operation_id)
            print(f"  Inputs: {inputs}")
    print("=" * 100)
    return api_setup


def get_operation_details(api_setup):
    api_adapter = api_setup.get_api_manager().get_api("tavily_service")

    operation_id = "search"
    operation_description = api_adapter.get_operation_description(operation_id)
    print(f"Operation description: {operation_description}")

    operation_input = api_adapter.get_operation_input(operation_id)
    print(f"Operation input: {operation_input}")


def tavily_api(api_setup):
    api_key = "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"
    api_adapter = api_setup.get_api_manager().get_api("tavily_service")

    response = api_adapter.execute_operation(
        operation_id="search", data={"api_key": api_key, "query": "o que é o TCE-PA?"}
    )
    return response


if __name__ == "__main__":
    api_setup = init()

    response = tavily_api(api_setup)
    res = WebSearchResponse(
        query="o que é o TCE-PA?", results=[WebSearchData(**r) for r in response.get("results")]
    )
    print(res)

    # get_operation_details(api_setup)
