import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from api_template.api.v1.schemas.websearch_schema import (
    WebSearchData,
    WebSearchRequest,
    WebSearchResponse,
)
from api_template.config.settings import settings
from api_template.external.core.setup import APISetup

router = APIRouter(prefix="/tools")

logger = logging.getLogger()


@router.post("/", response_model=WebSearchResponse)
async def websearch(request: WebSearchRequest, external: APISetup = Depends(APISetup)):
    """
    Create a new user.

    This endpoint allows creating a new user with the provided information.
    Only authenticated users can create new users.
    """
    try:
        api_adapter = external.get_api_manager().get_api("tavily_service")

        response = api_adapter.execute_operation(
            operation_id="search", data={"api_key": settings.TAVILY_API_KEY, "query": request.query}
        )
        return WebSearchResponse(
            query=request.query, results=[WebSearchData(**r) for r in response.get("results")]
        )

    except ValueError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
