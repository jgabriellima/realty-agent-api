from pydantic import BaseModel, Field


class WebSearchRequest(BaseModel):
    query: str = Field(
        ...,
        description="The search query to be performed on the web. Make sure to include the search terms and filters.",
    )


class WebSearchData(BaseModel):
    title: str = Field(..., description="The title of the search result.")
    url: str = Field(..., description="The URL of the search result.")
    content: str = Field(..., description="The content of the search result.")
    score: float = Field(..., description="The relevance score of the search result.")
    raw_content: None


class WebSearchResponse(WebSearchRequest):
    results: list[WebSearchData] = Field(..., description="The list of search results.")
