"""Google search engine using async/arc endpoint with CONSENT cookie."""

import random
import string
from urllib.parse import unquote

from lxml import html

from .base import Engine, RequestSpec, Result


def _random_arc_id() -> str:
    """Generate a random arc_id like srp_<23 random chars>_1."""
    chars = string.ascii_letters + string.digits
    rand = "".join(random.choices(chars, k=23))
    return f"srp_{rand}_1"


class Google(Engine):
    name = "google"

    def build_request(self, query: str, max_results: int = 10) -> RequestSpec:
        arc_id = _random_arc_id()
        return RequestSpec(
            url="https://www.google.com/search",
            params={
                "q": query,
                "num": str(max_results),
                "hl": "en",
                "asearch": "arc",
                "async": f"arc_id:{arc_id},use_ac:true,_fmt:prog",
            },
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
            cookies={
                "CONSENT": "YES+cb.20210720-07-p0.en+FX+410",
            },
        )

    def parse_response(self, text: str) -> list[Result]:
        results = []
        tree = html.fromstring(text)

        # Primary: MjjYud containers (modern Google HTML)
        containers = tree.xpath('.//div[contains(@class, "MjjYud")]')

        # Fallback: classic div.g containers
        if not containers:
            containers = tree.xpath(
                '//div[@class="g" or contains(@class, " g ") or starts-with(@class, "g ")]'
            )

        for el in containers:
            # Extract URL
            href = self._extract_url(el)
            if not href:
                continue

            # Extract title
            title = self._extract_title(el)
            if not title:
                continue

            # Extract snippet
            content = self._extract_snippet(el)

            results.append(Result(title=title, url=href, content=content, engine=self.name))

        return results

    def _extract_url(self, el) -> str | None:
        """Extract and clean URL from a result container."""
        links = el.xpath('.//a/@href')
        for raw in links:
            if not raw or raw.startswith("#") or raw.startswith("javascript:"):
                continue
            # Google /url?q= redirect prefix
            if raw.startswith("/url?q="):
                url = unquote(raw[7:].split("&sa=")[0].split("&ved=")[0])
                if url.startswith("http"):
                    return url
            elif raw.startswith("http"):
                return raw
        return None

    def _extract_title(self, el) -> str:
        """Extract title from result container."""
        # Try role="link" divs (arc/async format)
        for t in el.xpath('.//div[contains(@role, "link")]'):
            text = t.text_content().strip()
            if text:
                return text
        # Try h3 (classic format)
        for t in el.xpath('.//h3'):
            text = t.text_content().strip()
            if text:
                return text
        return ""

    def _extract_snippet(self, el) -> str:
        """Extract snippet/description from result container."""
        # Try data-sncf attribute (arc/async format)
        for s in el.xpath('.//div[contains(@data-sncf, "1")]'):
            text = s.text_content().strip()
            if text:
                return text
        # Try VwiC3b class (classic format)
        for s in el.xpath('.//div[contains(@class, "VwiC3b")]'):
            text = s.text_content().strip()
            if text:
                return text
        # Try span.st (older format)
        for s in el.xpath('.//span[@class="st"]'):
            text = s.text_content().strip()
            if text:
                return text
        # Generic data-sncf fallback
        for s in el.xpath('.//div[@data-sncf]'):
            text = s.text_content().strip()
            if text:
                return text
        return ""
