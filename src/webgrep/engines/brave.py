"""Brave search engine."""

from lxml import html

from .base import Engine, RequestSpec, Result


class Brave(Engine):
    name = "brave"

    def build_request(self, query: str, max_results: int = 10) -> RequestSpec:
        return RequestSpec(
            url="https://search.brave.com/search",
            params={
                "q": query,
                "source": "web",
            },
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "identity",
            },
            cookies={"safesearch": "off", "useLocation": "0"},
        )

    def parse_response(self, text: str) -> list[Result]:
        results = []
        tree = html.fromstring(text)

        for el in tree.xpath('//div[contains(@class, "snippet") and @data-type="web"]'):
            # URL from the first link
            links = el.xpath('.//a[@href]')
            if not links:
                continue
            href = links[0].get("href", "")
            if not href or not href.startswith("http"):
                continue

            # Title
            title_el = el.xpath('.//*[contains(@class, "snippet-title")]')
            if not title_el:
                title_el = el.xpath('.//div[contains(@class, "title")]')
            if not title_el:
                continue
            title = title_el[0].text_content().strip()
            if not title:
                continue

            # Description from generic-snippet or content div
            desc_el = el.xpath('.//div[contains(@class, "generic-snippet")]')
            if not desc_el:
                desc_el = el.xpath('.//div[contains(@class, "content") and contains(@class, "t-primary")]')
            content = desc_el[0].text_content().strip() if desc_el else ""

            results.append(Result(title=title, url=href, content=content, engine=self.name))

        return results
