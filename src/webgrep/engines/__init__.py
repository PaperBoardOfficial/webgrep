"""Engine registry."""

from .base import Engine, Result
from .google import Google
from .bing import Bing
from .duckduckgo import DuckDuckGo
from .brave import Brave
from .yahoo import Yahoo
from .mojeek import Mojeek
from .startpage import Startpage
from .presearch import Presearch

ALL_ENGINES: dict[str, Engine] = {
    "google": Google(),
    "bing": Bing(),
    "duckduckgo": DuckDuckGo(),
    "brave": Brave(),
    "yahoo": Yahoo(),
    "mojeek": Mojeek(),
    "startpage": Startpage(),
    "presearch": Presearch(),
}

__all__ = ["ALL_ENGINES", "Engine", "Result"]
