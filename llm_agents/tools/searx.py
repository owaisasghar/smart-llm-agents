import os
from typing import Any, List, Dict
from pydantic import Field
from llm_agents.tools.base import ToolInterface
import requests
import json

"""
Wrapper for the Searx Search API

Note that this uses the JSON query parameter, which is disabled by default in SearXNG instances.
You must manually enable JSON output by adding the JSON key to the settings.yml file:
https://github.com/searxng/searxng/blob/934249dd05142cde3461c8c4aae2c6d5804b0409/searx/settings.yml#L63

See the API documentation for details on supported parameters:
https://searx.github.io/searx/dev/search_api.html

Set the URL of the Searx instance to the environment variable SEARX_INSTANCE_URL.
"""


def _searx_search_results(params) -> list[dict[str, Any]]:
    search_params = {
        "q": params['q'],
        "safesearch": 0,
        "format": "json",
    }

    if params['safesearch']:
        search_params['safesearch'] = 1

    res = requests.post(params['instance_url'], data=search_params)
    json_results = json.loads(res.content)
    return json_results


def search(query: str) -> str:
    params: dict = {
        "q": query,
        "instance_url": os.environ["SEARX_INSTANCE_URL"],
        "method": "POST",
        "safesearch": False,
        "max_results": 10
    }

    res = _searx_search_results(params)

    if (len(res) == 0 or (len(res['answers']) == 0 and len(res['infoboxes']) == 0 and len(res['results']) == 0)):
        return "No good Searx Search Result was found"

    toret = []

    if len(res['answers']) > 0:
        for result in res['answers']:
            if "content" in result:
                toret.append(result["content"])

    elif len(res['infoboxes']) > 0:
        for result in res['infoboxes']:
            if "content" in result:
                toret.append(result["content"])

    elif len(res['results']) > 0:
        for result in res['results'][:params['max_results']]:
            if "content" in result:
                toret.append(result["content"])

    for result in res:
        if "content" in result:
            toret.append(result["content"])

    return " ".join(toret)


class SearxTool(ToolInterface):
    name: str = Field(default="SearxTool", description="Tool for performing Searx searches")
    description: str = "A tool for performing Searx searches. Input should be a search query."
    base_url: str = "https://searx.example.com"  # Replace with your Searx instance URL

    async def use(self, query: str) -> str:
        """Perform a Searx search and return the results."""
        try:
            # This is a placeholder implementation
            # You would need to replace this with actual Searx API implementation
            return f"Searx results for: {query}\nThis is a placeholder implementation. Please configure a real Searx instance."
            
        except Exception as e:
            return f"Error performing search: {str(e)}"


if __name__ == '__main__':
    s = SearxTool()
    res = s.use("Who was the pope in 2023?")
    print(res)
