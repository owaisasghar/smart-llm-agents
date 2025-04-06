from typing import Any, List, Dict
from pydantic import Field
from llm_agents.tools.base import ToolInterface
import requests
import json


ENDPOINT = "https://hn.algolia.com/api/v1/search_by_date"


def extract_text_from(url, max_len: int = 2000):
    html = requests.get(url).text
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text()

    lines = (line.strip() for line in text.splitlines())
    return '\n'.join(line for line in lines if line)[:max_len]


def search_hn(query: str, crawl_urls: bool) -> str:
    params = {
        "query": query,
        "tags": "story",
        "numericFilters": "points>100"
    }

    response = requests.get(ENDPOINT, params=params)

    hits = response.json()["hits"]

    result = ""
    for hit in hits[:5]:
        title = hit["title"]
        url = hit["url"]
        result += f"Title: {title}\n"
        
        if url is not None and crawl_urls:
            result += f"\tExcerpt: {extract_text_from(url)}\n"
        else:
            objectID = hit["objectID"]
            comments_url = f"{ENDPOINT}?tags=comment,story_{objectID}&hitsPerPage=1"
            comments_response = requests.get(comments_url)
            comment = comments_response.json()["hits"][0]['comment_text']
            
            result += f"\tComment: {comment}\n"
    return result


class HackerNewsSearchTool(ToolInterface):
    name: str = Field(default="HackerNewsSearchTool", description="Tool for searching Hacker News")
    description: str = "A tool for searching Hacker News stories. Input should be a search query."
    base_url: str = "https://hn.algolia.com/api/v1"

    async def use(self, query: str) -> str:
        """Search Hacker News and return the results."""
        try:
            # Search stories
            response = requests.get(
                f"{self.base_url}/search",
                params={
                    "query": query,
                    "tags": "story",
                    "hitsPerPage": 5
                }
            )
            response.raise_for_status()
            
            results = response.json()
            if not results.get("hits"):
                return "No results found."
            
            formatted_results = []
            for hit in results["hits"]:
                formatted_results.append(
                    f"Title: {hit.get('title', 'N/A')}\n"
                    f"URL: {hit.get('url', 'N/A')}\n"
                    f"Points: {hit.get('points', 0)}\n"
                    f"Comments: {hit.get('num_comments', 0)}\n"
                )
            
            return "\n".join(formatted_results)
            
        except requests.exceptions.RequestException as e:
            return f"Error performing search: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"


if __name__ == '__main__':
    hn = HackerNewsSearchTool()
    res = hn.use('GPT-4')
    print(res)
