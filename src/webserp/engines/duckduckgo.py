"""DuckDuckGo search engine."""

import re

from lxml import html

from .base import Engine, RequestSpec, Result


class DuckDuckGo(Engine):
    name = "duckduckgo"

    def build_request(self, query: str, max_results: int = 10) -> list[RequestSpec]:
        # Step 1: Get vqd token from main page
        token_req = RequestSpec(
            url="https://duckduckgo.com/",
            params={"q": query},
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        # Step 2: Search using HTML endpoint (built dynamically after token fetch)
        search_req = RequestSpec(
            url="https://html.duckduckgo.com/html/",
            method="POST",
            data={"q": query, "b": ""},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://html.duckduckgo.com/",
            },
        )
        return [token_req, search_req]

    def parse_response(self, text: str) -> list[Result]:
        results = []
        tree = html.fromstring(text)

        for el in tree.xpath('//div[contains(@class, "web-result")]'):
            link = el.xpath('.//a[@class="result__a"]')
            if not link:
                continue
            href = link[0].get("href", "")
            title = link[0].text_content().strip()

            snippet_el = el.xpath('.//a[@class="result__snippet"]')
            content = snippet_el[0].text_content().strip() if snippet_el else ""

            # DDG sometimes wraps URLs in a redirect
            if "//duckduckgo.com/l/?uddg=" in href:
                match = re.search(r'uddg=([^&]+)', href)
                if match:
                    from urllib.parse import unquote
                    href = unquote(match.group(1))

            if title and href and href.startswith("http"):
                results.append(Result(title=title, url=href, content=content, engine=self.name))

        return results
