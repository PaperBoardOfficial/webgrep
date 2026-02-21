"""Presearch search engine."""

import json
import re
from html import unescape

from .base import Engine, RequestSpec, Result


def _clean(text: str) -> str:
    """Unescape HTML entities and strip tags."""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


class Presearch(Engine):
    name = "presearch"

    def build_request(self, query: str, max_results: int = 10) -> list[RequestSpec]:
        # Step 1: Get searchId
        init_req = RequestSpec(
            url="https://presearch.com/search",
            params={"q": query},
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        # Step 2: Fetch results JSON (URL built dynamically after step 1)
        results_req = RequestSpec(
            url="https://presearch.com/results",
            params={},  # id= param added dynamically
            headers={
                "Accept": "application/json,text/html,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        return [init_req, results_req]

    @staticmethod
    def extract_search_id(html_text: str) -> str | None:
        """Extract searchId from Presearch HTML."""
        match = re.search(r'window\.searchId\s*=\s*["\']([^"\']+)["\']', html_text)
        return match.group(1) if match else None

    def parse_response(self, text: str) -> list[Result]:
        results = []
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return results

        # Results are nested: data["results"]["standardResults"]
        std_results = data.get("results", {})
        if isinstance(std_results, dict):
            std_results = std_results.get("standardResults", [])
        if not isinstance(std_results, list):
            return results

        for item in std_results:
            title = _clean(item.get("title", ""))
            url = item.get("link", item.get("url", "")).strip()
            content = _clean(item.get("description", item.get("snippet", "")))

            if title and url:
                results.append(Result(title=title, url=url, content=content, engine=self.name))

        return results
