"""Startpage search engine."""

import re

from lxml import html

from .base import Engine, RequestSpec, Result


class Startpage(Engine):
    name = "startpage"

    def build_request(self, query: str, max_results: int = 10) -> list[RequestSpec]:
        # Step 1: Get the sc token from homepage
        token_req = RequestSpec(
            url="https://www.startpage.com/",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        # Step 2: POST search (sc token injected dynamically)
        search_req = RequestSpec(
            url="https://www.startpage.com/sp/search",
            method="POST",
            data={"query": query, "cat": "web", "language": "english"},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Origin": "https://www.startpage.com",
                "Referer": "https://www.startpage.com/",
            },
        )
        return [token_req, search_req]

    @staticmethod
    def extract_sc_token(homepage_html: str) -> str | None:
        """Extract the sc token from Startpage's homepage."""
        match = re.search(r'name="sc"\s+value="([^"]+)"', homepage_html)
        return match.group(1) if match else None

    def parse_response(self, text: str) -> list[Result]:
        results = []
        tree = html.fromstring(text)

        # Try current class names then legacy ones
        containers = tree.xpath('//div[contains(@class, "result") and not(contains(@class, "ad-hdr"))]')
        if not containers:
            containers = tree.xpath('//div[contains(@class, "w-gl__result")]')

        for el in containers:
            # Find result link
            link = el.xpath('.//a[contains(@class, "result-title") or contains(@class, "result-link")]')
            if not link:
                link = el.xpath('.//a[contains(@class, "w-gl__result-title")]')
            if not link:
                continue

            href = link[0].get("href", "")
            title = link[0].text_content().strip()

            # Clean CSS artifacts from title (lxml sometimes includes style text)
            if title.startswith(".css-"):
                # Extract readable part after CSS noise
                parts = title.split("}")
                title = parts[-1].strip() if parts else title

            if not title or not href or not href.startswith("http"):
                continue

            # Snippet
            snippet_el = el.xpath('.//p[contains(@class, "description")]')
            if not snippet_el:
                snippet_el = el.xpath('.//p[contains(@class, "w-gl__description")]')
            if not snippet_el:
                snippet_el = el.xpath('.//p')
            content = snippet_el[0].text_content().strip() if snippet_el else ""

            results.append(Result(title=title, url=href, content=content, engine=self.name))

        return results
