"""Yahoo search engine."""

from urllib.parse import unquote

from lxml import html

from .base import Engine, RequestSpec, Result


class Yahoo(Engine):
    name = "yahoo"

    def build_request(self, query: str, max_results: int = 10) -> RequestSpec:
        return RequestSpec(
            url="https://search.yahoo.com/search",
            params={
                "p": query,
                "n": str(max_results),
            },
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )

    def parse_response(self, text: str) -> list[Result]:
        results = []
        tree = html.fromstring(text)

        for el in tree.xpath('//div[contains(@class, "algo") and contains(@class, "algo-sr")]'):
            # First link is the main result link
            link = el.xpath('.//a[@href]')
            if not link:
                continue

            href = link[0].get("href", "")
            if not href:
                continue

            # Extract actual URL from Yahoo redirect
            if "/RU=" in href:
                parts = href.split("/RU=")
                if len(parts) > 1:
                    raw = parts[1].split("/RK=")[0].split("/RS=")[0]
                    decoded = unquote(raw)
                    if decoded.startswith("http"):
                        href = decoded

            if not href.startswith("http"):
                continue

            # Title - prefer h3.title, then compTitle, then first link text
            title_el = el.xpath('.//h3[contains(@class, "title")]')
            if not title_el:
                title_el = el.xpath('.//*[contains(@class, "compTitle")]//a')
            if title_el:
                title = title_el[0].text_content().strip()
            else:
                title = link[0].text_content().strip()

            if not title:
                continue

            # Snippet
            snippet_el = el.xpath('.//div[contains(@class, "compText")]')
            if not snippet_el:
                snippet_el = el.xpath('.//p')
            content = snippet_el[0].text_content().strip() if snippet_el else ""

            results.append(Result(title=title, url=href, content=content, engine=self.name))

        return results
