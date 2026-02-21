"""CLI entry point for webgrep."""

import argparse
import asyncio
import json
import sys

from . import __version__
from .engines import ALL_ENGINES
from .search import search


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="webgrep",
        description="Metasearch CLI — query multiple search engines in parallel.",
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "-e", "--engines",
        default=None,
        help=f"Comma-separated engine list (default: all). Available: {','.join(ALL_ENGINES.keys())}",
    )
    parser.add_argument("-n", "--max-results", type=int, default=10, help="Max results per engine (default: 10)")
    parser.add_argument("--timeout", type=int, default=10, help="Per-engine timeout in seconds (default: 10)")
    parser.add_argument("--proxy", default=None, help="Proxy URL for all requests")
    parser.add_argument("--verbose", action="store_true", help="Show engine success/failure in stderr")
    parser.add_argument("--version", action="version", version=f"webgrep {__version__}")

    args = parser.parse_args(argv)

    engine_names = None
    if args.engines:
        engine_names = [e.strip() for e in args.engines.split(",")]
        invalid = [e for e in engine_names if e not in ALL_ENGINES]
        if invalid:
            print(f"webgrep: unknown engines: {', '.join(invalid)}", file=sys.stderr)
            print(f"Available: {', '.join(ALL_ENGINES.keys())}", file=sys.stderr)
            return 1

    result = asyncio.run(
        search(
            query=args.query,
            engine_names=engine_names,
            max_results=args.max_results,
            timeout=args.timeout,
            proxy=args.proxy,
        )
    )

    if args.verbose:
        succeeded = [e for e in (engine_names or ALL_ENGINES.keys()) if e not in [u[0] for u in result["unresponsive_engines"]]]
        print(f"Succeeded: {', '.join(succeeded)}", file=sys.stderr)
        for engine_name, error in result["unresponsive_engines"]:
            print(f"Failed: {engine_name} ({error})", file=sys.stderr)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
