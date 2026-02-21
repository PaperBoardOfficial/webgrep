"""Base engine class for all search engines."""

from dataclasses import dataclass, field


@dataclass
class Result:
    title: str
    url: str
    content: str
    engine: str

    def as_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "content": self.content,
            "engine": self.engine,
        }


@dataclass
class RequestSpec:
    url: str
    method: str = "GET"
    params: dict = field(default_factory=dict)
    data: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    cookies: dict = field(default_factory=dict)


class Engine:
    name: str = ""

    def build_request(self, query: str, max_results: int = 10) -> RequestSpec | list[RequestSpec]:
        """Build the HTTP request spec(s) for this engine."""
        raise NotImplementedError

    def parse_response(self, text: str) -> list[Result]:
        """Parse HTTP response text into results."""
        raise NotImplementedError
