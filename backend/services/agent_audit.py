"""Agent Audit — recursive documentation of agentic actions.

Implements PHASE 2.3 of the QGTNL alignment protocol:
    "Every agentic action performed in any space must generate a JSON log
    entry pushed automatically to the Librarian's RAG for continuous
    learning."

Design notes
------------
* Pure best-effort. Audit logging must never block or fail a real action.
* Always writes a JSON Lines file locally at ``AGENT_AUDIT_PATH`` (default:
  ``encyclopedia/agent_audit.jsonl``) so the audit trail survives even when
  the Librarian Hub is unreachable.
* Optionally forwards each entry to ``MAPPING_HUB_URL`` ``/v1/ingest`` in
  the background. Network failures are swallowed and logged at WARN.
* No PII or secrets are recorded by design. Callers are responsible for
  passing non-sensitive ``payload`` dicts.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

DEFAULT_AUDIT_PATH = os.path.join("encyclopedia", "agent_audit.jsonl")
DEFAULT_HUB_URL = "https://dj-goana-coding-mapping-and-inventory.hf.space"
DEFAULT_HUB_TIMEOUT = 10.0
NODE_NAME = os.environ.get("NODE_NAME", "pioneer-trader")


class AgentAudit:
    """Best-effort agentic-action audit trail."""

    def __init__(
        self,
        audit_path: Optional[str] = None,
        hub_url: Optional[str] = None,
        forward_to_hub: Optional[bool] = None,
    ) -> None:
        self.audit_path = Path(
            audit_path or os.environ.get("AGENT_AUDIT_PATH", DEFAULT_AUDIT_PATH)
        )
        self.hub_url = (
            hub_url
            or os.environ.get("MAPPING_HUB_URL", DEFAULT_HUB_URL)
        ).rstrip("/")
        if forward_to_hub is None:
            forward_to_hub = os.environ.get(
                "AGENT_AUDIT_FORWARD", "True"
            ).lower() == "true"
        self.forward_to_hub = forward_to_hub
        try:
            self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:  # pragma: no cover - filesystem failure
            logger.warning("AgentAudit: cannot create %s: %s", self.audit_path.parent, exc)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def record(
        self,
        action: str,
        payload: Optional[Dict[str, Any]] = None,
        actor: str = "system",
        status: str = "ok",
    ) -> Dict[str, Any]:
        """Record an audit entry. Returns the entry that was written."""
        entry: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "node": NODE_NAME,
            "actor": actor,
            "action": action,
            "status": status,
            "payload": payload or {},
        }
        self._append_local(entry)
        if self.forward_to_hub:
            self._forward_async(entry)
        return entry

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    def _append_local(self, entry: Dict[str, Any]) -> None:
        try:
            with open(self.audit_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
        except OSError as exc:  # pragma: no cover - filesystem failure
            logger.warning("AgentAudit: local write failed: %s", exc)

    def _forward_async(self, entry: Dict[str, Any]) -> None:
        """Schedule a fire-and-forget POST to the Librarian Hub.

        Falls back to a synchronous attempt only if no event loop is
        running (e.g. unit tests / CLI scripts). Errors are logged and
        suppressed.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop — skip remote forward to avoid blocking.
            return
        loop.create_task(self._post_to_hub(entry))

    async def _post_to_hub(self, entry: Dict[str, Any]) -> None:
        url = f"{self.hub_url}/v1/ingest"
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_HUB_TIMEOUT) as client:
                resp = await client.post(url, json={"entry": entry})
            if resp.status_code >= 400:
                logger.warning(
                    "AgentAudit: hub %s responded %s", url, resp.status_code
                )
        except httpx.HTTPError as exc:
            logger.warning("AgentAudit: hub forward failed: %s", exc)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("AgentAudit: unexpected hub error: %s", exc)


# Singleton — cheap and shareable.
agent_audit = AgentAudit()


__all__ = ["AgentAudit", "agent_audit"]
