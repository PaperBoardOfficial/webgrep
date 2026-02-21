"""Bing search engine."""

import base64
import re
from urllib.parse import unquote

from lxml import html

from .base import Engine, RequestSpec, Result


class Bing(Engine):
    name = "bing"

    def build_request(self, query: str, max_results: int = 10) -> RequestSpec:
        return RequestSpec(
            url="https://www.bing.com/search",
            params={
                "q": query,
                "count": str(max_results),
                "setlang": "en",
                "cc": "US",
                "mkt": "en-US",
            },
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
            cookies={
                "SRCHHPGUSR": "SRCHLANG=en&BRW=XW&BRH=S&CW=800&CH=600&DPR=1&UTC=-300&DM=0",
                "MKTLANG": "en-US",
            },
        )

    @staticmethod
    def _decode_url(href: str) -> str:
        """Decode Bing's wrapped /ck/a? redirect URLs."""
        if "/ck/a?" not in href:
            return href
        match = re.search(r'[&?]u=a1(.+?)(&|$)', href)
        if match:
            try:
                decoded = base64.b64decode(match.group(1) + "==").decode("utf-8", errors="ignore")
                if decoded.startswith("http"):
                    return decoded
            except Exception:
                pass
        return href

    def parse_response(self, text: str) -> list[Result]:
        results = []
        tree = html.fromstring(text)

        for el in tree.xpath('//ol[@id="b_results"]/li[contains(@class, "b_algo")]'):
            link = el.xpath('.//h2/a')
            if not link:
                continue
            href = self._decode_url(link[0].get("href", ""))
            title = link[0].text_content().strip()

            snippet_el = el.xpath('.//p')
            if not snippet_el:
                snippet_el = el.xpath('.//div[@class="b_caption"]/p')
            content = snippet_el[0].text_content().strip() if snippet_el else ""

            if title and href and href.startswith("http"):
                results.append(Result(title=title, url=href, content=content, engine=self.name))

        return results
