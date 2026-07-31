"""Small GitHub API fetch helper shared by commands."""

import os
import urllib.request


def fetch(url, raw=False):
    """Fetch a GitHub API URL, using GITHUB_TOKEN/GH_TOKEN when available."""
    accept = "application/vnd.github.raw" if raw else "application/vnd.github+json"
    headers = {"Accept": accept, "User-Agent": "helper-cli"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()
