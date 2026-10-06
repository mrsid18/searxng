# SPDX-License-Identifier: AGPL-3.0-or-later
"""Engine for the `Exa Answer API`_: an LLM-written answer to the query, grounded
in web search, with the cited pages as results.

.. _Exa Answer API: https://exa.ai/docs/reference/answer

Answers are slower and pricier than searches, so this engine is meant to be
used by its bang only (``disabled: true``) and given a longer ``timeout``.

Configuration
=============

The engine has the following mandatory setting:

- :py:obj:`api_key`

Optional settings are:

- :py:obj:`model`

.. code:: yaml

  - name: exa answer
    engine: exaapi_answer
    shortcut: exaa
    api_key: "..."
    model: exa
    timeout: 15
    disabled: true
"""

import typing as t

from dateutil import parser

from searx.exceptions import SearxEngineAPIException
from searx.result_types import EngineResults

if t.TYPE_CHECKING:
    from searx.extended_types import SXNG_Response
    from searx.search.processors import OnlineParams

about = {
    "website": "https://exa.ai",
    "wikidata_id": None,
    "official_api_documentation": "https://exa.ai/docs/reference/answer",
    "use_official_api": True,
    "require_api_key": True,
    "results": "JSON",
}

api_key: str = ""
"""API key for Exa (required)."""

categories = ["general", "web"]

base_url = "https://api.exa.ai/answer"

ModelType = t.Literal["exa", "exa-pro", "exa-fast"]
model: ModelType = "exa"
"""Answer model: ``exa`` (default), ``exa-pro`` or ``exa-fast``."""


def setup(_: dict[str, t.Any]) -> bool | None:
    if not api_key:
        raise SearxEngineAPIException("No API key provided")
    if model not in t.get_args(ModelType):
        raise ValueError(f"Unsupported model: {model}")


def request(query: str, params: "OnlineParams") -> None:
    body: dict[str, t.Any] = {"query": query, "model": model, "text": False}

    locale_parts = params["searxng_locale"].split("-")
    if len(locale_parts) > 1:
        body["userLocation"] = locale_parts[-1].upper()

    params["url"] = base_url
    params["method"] = "POST"
    params["headers"]["x-api-key"] = api_key
    params["json"] = body


def _published_date(value: str | None):
    if not value:
        return None
    try:
        return parser.parse(value)
    except (parser.ParserError, TypeError, OverflowError):
        return None


def response(resp: "SXNG_Response") -> EngineResults:
    res = EngineResults()
    data = resp.json()

    citations = [c for c in data.get("citations") or [] if c.get("url")]
    answer = data.get("answer")
    if isinstance(answer, str) and answer.strip():
        res.add(res.types.Answer(answer=answer.strip(), url=citations[0]["url"] if citations else None))

    for c in citations:
        res.add(
            res.types.MainResult(
                url=c["url"],
                title=c.get("title") or c["url"],
                thumbnail=c.get("image") or "",
                publishedDate=_published_date(c.get("publishedDate")),
                author=c.get("author") or "",
            )
        )

    return res
