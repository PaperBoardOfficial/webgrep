# webserp

Metasearch CLI — query multiple search engines in parallel with browser impersonation.

Like `grep` for the web. Searches Google, Bing, DuckDuckGo, Brave, Yahoo, Mojeek, Startpage, and Presearch simultaneously, deduplicates results, and returns clean JSON.

## Why webserp?

Existing tools like `ddgs` get rate-limited and blocked because they use standard HTTP libraries. webserp uses [curl_cffi](https://github.com/lexiforest/curl_cffi) to impersonate real browsers (Chrome TLS/JA3 fingerprints), making requests indistinguishable from a human browsing.

- **8 search engines** queried in parallel
- **Browser impersonation** via curl_cffi — bypasses bot detection
- **Fault tolerant** — if one engine fails, others still return results
- **SearXNG-compatible JSON** output format
- **No API keys** — scrapes search engine HTML directly
- **Fast** — parallel async requests, typically completes in 2-5s

## Install

```bash
pip install webserp
```

## Usage

```bash
# Search all engines
webserp "how to deploy docker containers"

# Search specific engines
webserp "python async tutorial" --engines google,brave,bing

# Limit results per engine
webserp "rust vs go" --max-results 5

# Show which engines succeeded/failed
webserp "test query" --verbose

# Use a proxy
webserp "query" --proxy "socks5://127.0.0.1:1080"
```

## Output Format

JSON output matching SearXNG's format:

```json
{
  "query": "deployment issue",
  "number_of_results": 42,
  "results": [
    {
      "title": "How to fix Docker deployment issues",
      "url": "https://example.com/docker-fix",
      "content": "Common Docker deployment problems and solutions...",
      "engine": "google"
    }
  ],
  "suggestions": [],
  "unresponsive_engines": []
}
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `-e, --engines` | Comma-separated engine list | all |
| `-n, --max-results` | Max results per engine | 10 |
| `--timeout` | Per-engine timeout (seconds) | 10 |
| `--proxy` | Proxy URL for all requests | none |
| `--verbose` | Show engine status in stderr | false |
| `--version` | Print version | |

## Engines

google, bing, duckduckgo, brave, yahoo, mojeek, startpage, presearch

## Use with AI Agents

webserp outputs structured JSON to stdout, making it easy for AI agents to call it as a shell tool for web search. Any agent that can execute shell commands can use webserp — no API keys, no SDKs, no configuration.

### OpenClaw

[OpenClaw](https://github.com/openclaw/openclaw) agents can use webserp as a skill or via the `system.run` tool:

```bash
# Install webserp on the machine running the OpenClaw Gateway
pip install webserp
```

The agent can then search the web by executing a shell command:

```bash
webserp "latest python release" --max-results 5
```

The JSON output is parsed directly by the agent — the `results` array contains `title`, `url`, `content`, and `engine` fields, giving the agent structured context to answer questions, cite sources, or follow up on links.

### Any Agent / Framework

webserp works with any agent that can run shell commands and parse JSON — LangChain, CrewAI, AutoGPT, Claude Code, or custom agents:

```python
import subprocess
import json

result = subprocess.run(
    ["webserp", "how to fix docker networking", "--max-results", "5"],
    capture_output=True, text=True
)
data = json.loads(result.stdout)

for r in data["results"]:
    print(f"{r['title']}: {r['url']}")
```

Since webserp queries 8 engines in parallel with browser impersonation, agents get more diverse and reliable results compared to single-engine tools like `ddgs` that are easily rate-limited.

## License

MIT
