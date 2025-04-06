# Based on https://raw.githubusercontent.com/hwchase17/langchain/master/langchain/utilities/google_search.py

import os
from typing import Any, Optional, Dict
from llm_agents.tools.base import ToolInterface
from googleapiclient.discovery import build
from pydantic import BaseModel, Field
import requests
from dotenv import load_dotenv

load_dotenv()


"""Wrapper for Google Search API.

Adapted from: Instructions adapted from https://stackoverflow.com/questions/
37083058/
programmatically-searching-google-in-python-using-custom-search

1. Install google-api-python-client
- If you don't already have a Google account, sign up.
- If you have never created a Google APIs Console project,
read the Managing Projects page and create a project in the Google API Console.
- Install the library using pip install google-api-python-client
The current version of the library is 2.70.0 at this time

2. To create an API key:
- Navigate to the APIs & Services→Credentials panel in Cloud Console.
- Select Create credentials, then select API key from the drop-down menu.
- The API key created dialog box displays your newly created key.
- You now have an API_KEY

3. Setup Custom Search Engine so you can search the entire web
- Create a custom search engine in this link.
- In Sites to search, add any valid URL (i.e. www.stackoverflow.com).
- That's all you have to fill up, the rest doesn't matter.
In the left-side menu, click Edit search engine → {your search engine name}
→ Setup Set Search the entire web to ON. Remove the URL you added from
  the list of Sites to search.
- Under Search engine ID you'll find the search-engine-ID.

4. Enable the Custom Search API
- Navigate to the APIs & Services→Dashboard panel in Cloud Console.
- Click Enable APIs and Services.
- Search for Custom Search API and click on it.
- Click Enable.
URL for it: https://console.cloud.google.com/apis/library/customsearch.googleapis
.com
"""


def _google_search_results(params) -> list[dict[str, Any]]:
    service = build("customsearch", "v1", developerKey=params['api_key'])
    res = service.cse().list(
        q=params['q'], cx=params['cse_id'], num=params['max_results']).execute()
    return res.get('items', [])


def search(query: str) -> str:
    params: dict = {
        "q": query,
        "cse_id": os.environ["GOOGLE_CSE_ID"],
        "api_key": os.environ["GOOGLE_API_KEY"],
        "max_results": 10
    }

    res = _google_search_results(params)
    snippets = []
    if len(res) == 0:
        return "No good Google Search Result was found"
    for result in res:
        if "snippet" in result:
            snippets.append(result["snippet"])

    return " ".join(snippets)


class GoogleSearchTool(ToolInterface):
    """Tool for Google search results."""

    name: str = Field(default="GoogleSearchTool", description="Tool for performing Google searches")
    description: str = "A tool for performing Google searches. Input should be a search query."
    api_key: Optional[str] = Field(default=None, description="Google Search API key")
    search_engine_id: Optional[str] = Field(default=None, description="Google Search Engine ID")

    def __init__(self, **data):
        super().__init__(**data)
        self.api_key = self.api_key or os.getenv("GOOGLE_API_KEY")
        self.search_engine_id = self.search_engine_id or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        if not self.api_key or not self.search_engine_id:
            raise ValueError("Google API key and Search Engine ID must be provided either directly or through environment variables")

    async def use(self, query: str) -> str:
        """Perform a Google search and return the results."""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            results = response.json()
            if "items" not in results:
                return "No results found."
            
            formatted_results = []
            for item in results["items"][:5]:  # Limit to top 5 results
                formatted_results.append(
                    f"Title: {item.get('title', 'N/A')}\n"
                    f"Link: {item.get('link', 'N/A')}\n"
                    f"Snippet: {item.get('snippet', 'N/A')}\n"
                )
            
            return "\n".join(formatted_results)
            
        except requests.exceptions.RequestException as e:
            return f"Error performing search: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"


if __name__ == '__main__':
    s = GoogleSearchTool()
    res = s.use("Who was the pope in 2023?")
    print(res)

# Alias for backward compatibility
SerpAPITool = GoogleSearchTool
