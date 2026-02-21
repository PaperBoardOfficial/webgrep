# webgrep

Metasearch CLI — query multiple search engines in parallel with browser impersonation.

Like `grep` for the web. Searches Google, Bing, DuckDuckGo, Brave, Yahoo, Yandex, Mojeek, Startpage, and Presearch simultaneously, deduplicates results, and returns clean JSON.

## Why webgrep?

Existing tools like `ddgs` get rate-limited and blocked because they use standard HTTP libraries. webgrep uses [curl_cffi](https://github.com/lexiforest/curl_cffi) to impersonate real browsers (Chrome TLS/JA3 fingerprints), making requests indistinguishable from a human browsing.

- **9 search engines** queried in parallel
- **Browser impersonation** via curl_cffi — bypasses bot detection
- **Fault tolerant** — if one engine fails, others still return results
- **SearXNG-compatible JSON** output format
- **No API keys** — scrapes search engine HTML directly
- **Fast** — parallel async requests, typically completes in 2-5s

## Install

```bash
pip install webgrep
```

## Usage

```bash
# Search all engines
webgrep "how to deploy docker containers"

# Search specific engines
webgrep "python async tutorial" --engines google,brave,bing

# Limit results per engine
webgrep "rust vs go" --max-results 5

# Show which engines succeeded/failed
webgrep "test query" --verbose

# Use a proxy
webgrep "query" --proxy "socks5://127.0.0.1:1080"
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

google, bing, duckduckgo, brave, yahoo, yandex, mojeek, startpage, presearch

## License

MIT
