"""Compatibility shim while the server package is normalized to src layout."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC_PATH = Path(__file__).resolve().parent / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

from agentspine_server.app import app, create_app  # noqa: E402

__all__ = ["app", "create_app"]
