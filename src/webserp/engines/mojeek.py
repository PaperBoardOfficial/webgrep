"""Mojeek search engine."""

from lxml import html

from .base import Engine, RequestSpec, Result


class Mojeek(Engine):
    name = "mojeek"

    def build_request(self, query: str, max_results: int = 10) -> RequestSpec:
        return RequestSpec(
            url="https://www.mojeek.com/search",
            params={
                "q": query,
            },
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )

    def parse_response(self, text: str) -> list[Result]:
        results = []
        tree = html.fromstring(text)

        for el in tree.xpath('//ul[@class="results-standard"]/li'):
            link = el.xpath('.//a[@class="ob"]')
            if not link:
                continue
            href = link[0].get("href", "")

            title_el = el.xpath('.//h2/a')
            if not title_el:
                title_el = link
            title = title_el[0].text_content().strip()

            snippet_el = el.xpath('.//p[@class="s"]')
            content = snippet_el[0].text_content().strip() if snippet_el else ""

            if title and href and href.startswith("http"):
                results.append(Result(title=title, url=href, content=content, engine=self.name))

        return results
