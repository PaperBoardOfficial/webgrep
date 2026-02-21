# webserp

Metasearch CLI — query multiple search engines in parallel with browser impersonation.

Like `grep` for the web. Searches Google, DuckDuckGo, Brave, Yahoo, Mojeek, Startpage, and Presearch simultaneously, deduplicates results, and returns clean JSON.

## Why webserp?

Most search scraping tools get rate-limited and blocked because they use standard HTTP libraries. webserp uses [curl_cffi](https://github.com/lexiforest/curl_cffi) to impersonate real browsers (Chrome TLS/JA3 fingerprints), making requests indistinguishable from a human browsing.

- **7 search engines** queried in parallel
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
webserp "python async tutorial" --engines google,brave,duckduckgo

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

google, duckduckgo, brave, yahoo, mojeek, startpage, presearch

## For OpenClaw and AI agents

**Built for AI agents.** Tools like [OpenClaw](https://github.com/openclaw/openclaw) and other AI agents need reliable web search without API keys or rate limits. webserp uses [curl_cffi](https://github.com/lexiforest/curl_cffi) to mimic real browser fingerprints — results like a browser, speed like an API. It queries 7 engines in parallel, so even if one gets rate-limited, results still come back.

### Why a CLI tool instead of a Python library?

A CLI tool keeps web search out of the agent's process. The agent calls `webserp`, gets JSON back, and the process exits — no persistent HTTP sessions, no in-process state, no import overhead. Agents that never need web search pay zero cost.

### Example agent use cases

- **Research** — searching the web for current information before answering user questions
- **Fact checking** — verifying claims against multiple search engines
- **Link discovery** — finding relevant URLs, documentation, or source code
- **News monitoring** — checking for recent events or updates on a topic

```bash
# Agent searching for current information
webserp "latest python 3.14 release date" --max-results 5

# Searching multiple engines for diverse results
webserp "docker networking troubleshooting" --engines google,brave,duckduckgo --max-results 3

# Quick search with verbose to see which engines responded
webserp "CVE-2024 critical vulnerabilities" --verbose --max-results 5
```


## License

MIT
