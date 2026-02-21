"""Search orchestrator: parallel search across engines, merge, dedupe."""

import asyncio
import sys

from curl_cffi.requests import AsyncSession

from .client import fetch, random_impersonate
from .engines import ALL_ENGINES, Result
from .engines.base import RequestSpec
from .engines.duckduckgo import DuckDuckGo
from .engines.startpage import Startpage
from .engines.presearch import Presearch


async def _fetch_engine(
    engine,
    query: str,
    max_results: int,
    timeout: int,
    proxy: str | None,
    session: AsyncSession,
) -> tuple[str, list[Result], str | None]:
    """Fetch results from a single engine. Returns (engine_name, results, error)."""
    try:
        spec = engine.build_request(query, max_results)

        # Multi-step engines (DDG, Startpage, Presearch)
        if isinstance(spec, list):
            text = await _fetch_multistep(engine, spec, timeout, proxy, session)
        else:
            text = await _do_fetch(spec, timeout, proxy, session)

        results = engine.parse_response(text)
        return engine.name, results[:max_results], None

    except Exception as e:
        return engine.name, [], str(e)


async def _do_fetch(
    spec: RequestSpec,
    timeout: int,
    proxy: str | None,
    session: AsyncSession,
) -> str:
    return await fetch(
        spec.url,
        method=spec.method,
        params=spec.params or None,
        data=spec.data or None,
        headers=spec.headers or None,
        cookies=spec.cookies or None,
        timeout=timeout,
        proxy=proxy,
        session=session,
    )


async def _fetch_multistep(
    engine,
    specs: list[RequestSpec],
    timeout: int,
    proxy: str | None,
    session: AsyncSession,
) -> str:
    if isinstance(engine, DuckDuckGo):
        # Step 1: just POST directly, DDG HTML endpoint works without vqd for basic queries
        return await _do_fetch(specs[1], timeout, proxy, session)

    elif isinstance(engine, Startpage):
        # Step 1: Get sc token
        homepage = await _do_fetch(specs[0], timeout, proxy, session)
        sc = Startpage.extract_sc_token(homepage)
        if sc:
            specs[1].data["sc"] = sc
        # Step 2: Search
        return await _do_fetch(specs[1], timeout, proxy, session)

    elif isinstance(engine, Presearch):
        # Step 1: Get search ID
        init_html = await _do_fetch(specs[0], timeout, proxy, session)
        search_id = Presearch.extract_search_id(init_html)
        if not search_id:
            raise ValueError("Could not extract Presearch searchId")
        # Step 2: Fetch results
        specs[1].params["id"] = search_id
        return await _do_fetch(specs[1], timeout, proxy, session)

    else:
        # Fallback: just fetch last spec
        return await _do_fetch(specs[-1], timeout, proxy, session)


async def search(
    query: str,
    engine_names: list[str] | None = None,
    max_results: int = 10,
    timeout: int = 10,
    proxy: str | None = None,
) -> dict:
    """Search all engines in parallel and return merged results."""
    engines_to_use = {}
    if engine_names:
        for name in engine_names:
            if name in ALL_ENGINES:
                engines_to_use[name] = ALL_ENGINES[name]
    else:
        engines_to_use = ALL_ENGINES

    succeeded = []
    failed = []
    all_results: list[Result] = []

    async with AsyncSession() as session:
        tasks = [
            _fetch_engine(engine, query, max_results, timeout, proxy, session)
            for engine in engines_to_use.values()
        ]
        outcomes = await asyncio.gather(*tasks)

    for engine_name, results, error in outcomes:
        if error:
            failed.append([engine_name, error])
        else:
            succeeded.append(engine_name)
            all_results.extend(results)

    # Deduplicate by URL (keep first occurrence)
    seen_urls: set[str] = set()
    deduped: list[Result] = []
    for r in all_results:
        normalized = r.url.rstrip("/").lower()
        if normalized not in seen_urls:
            seen_urls.add(normalized)
            deduped.append(r)

    return {
        "query": query,
        "number_of_results": len(deduped),
        "results": [r.as_dict() for r in deduped],
        "suggestions": [],
        "unresponsive_engines": failed,
    }
