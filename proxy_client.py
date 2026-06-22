"""Heidi proxy client — single source of truth for proxy URL, timeout, and HTTP transport.

All modules that call the Heidi AI proxy must import from here rather than defining
their own constants. This prevents drift if the proxy URL or timeout ever changes.
"""
from __future__ import annotations
import json
import urllib.request

PROXY_URL = "https://heidi-ai-proxy.vercel.app/api/proxy"
PROXY_TIMEOUT_SEC = 30


def call_proxy(body: dict) -> str:
    """POST a pre-built request body to the Heidi proxy and return the first content text.

    Args:
        body: Complete Anthropic messages API request dict (model, messages, system, etc.).
              Caller is responsible for setting temperature=0 and cache_control.

    Returns:
        The text of the first content block in the response.

    Raises:
        urllib.error.URLError: on network failure (caller should catch and handle).
        KeyError / IndexError: if the response shape is unexpected.
    """
    req = urllib.request.Request(
        PROXY_URL,
        data=json.dumps(body).encode(),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=PROXY_TIMEOUT_SEC) as resp:
        return json.loads(resp.read())["content"][0]["text"]
