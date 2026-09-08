"""ISO 20022 Parser — Strictly-Schemaed Stub.

Scope of this module (per directive):
    * Establish the typed structure and the function signatures the rest of
      the pipeline can import and call.
    * Do NOT implement final validation logic. Payload validation (XSD,
      business-rule checks, CBPR+ constraints, etc.) will be filled in
      during a later compliance sweep.

Anything returned by this stub must be treated as *structurally parsed
only* — not validated.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ISO20022ParseError(ValueError):
    """Raised when a payload cannot be structurally interpreted."""


class ISO20022Message(BaseModel):
    """Minimal structural envelope for an ISO 20022 message.

    Fields intentionally cover only the outer shape. Concrete message
    families (pain.*, pacs.*, camt.*) will be modelled later.
    """

    message_id: Optional[str] = Field(
        default=None,
        description="Group Header / Message Identification (GrpHdr.MsgId).",
    )
    message_type: Optional[str] = Field(
        default=None,
        description="ISO 20022 message identifier, e.g. 'pacs.008.001.08'.",
    )
    creation_datetime: Optional[str] = Field(
        default=None,
        description="Creation date/time (GrpHdr.CreDtTm), ISO 8601 string.",
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Raw decoded body. Contents are NOT yet validated.",
    )


class ISO20022Parser:
    """Structural parser stub for ISO 20022 messaging payloads.

    The parser accepts either a `dict` (already-decoded JSON-ish payload)
    or a `str` containing XML/JSON text. No schema validation is performed
    in this stub; callers must not rely on semantic correctness of the
    returned object.
    """

    SUPPORTED_FORMATS = ("dict", "json", "xml")

    def __init__(self, strict: bool = False) -> None:
        self.strict = strict

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def parse(self, payload: Any) -> ISO20022Message:
        """Return a structural :class:`ISO20022Message`.

        Raises:
            ISO20022ParseError: if the payload is not a recognised shape.
        """
        if payload is None:
            raise ISO20022ParseError("Payload is empty.")

        try:
            if isinstance(payload, dict):
                return self._from_dict(payload)
            if isinstance(payload, (bytes, bytearray)):
                payload = payload.decode("utf-8", errors="replace")
            if isinstance(payload, str):
                return self._from_text(payload)
        except ISO20022ParseError:
            raise
        except Exception as exc:  # pragma: no cover - defensive catch
            raise ISO20022ParseError(f"Unable to parse payload: {exc}") from exc

        raise ISO20022ParseError(
            f"Unsupported payload type: {type(payload).__name__}"
        )

    def validate(self, message: ISO20022Message) -> bool:
        """Placeholder validator.

        Always returns True in this stub. Real schema / business-rule
        validation will be added in a later sweep. If ``strict`` is set
        the method still returns True but is the hook point where future
        XSD checks will raise.
        """
        _ = message  # schema enforcement deferred
        return True

    # ------------------------------------------------------------------ #
    # Internals (stubbed)
    # ------------------------------------------------------------------ #
    def _from_dict(self, data: Dict[str, Any]) -> ISO20022Message:
        return ISO20022Message(
            message_id=data.get("message_id") or data.get("MsgId"),
            message_type=data.get("message_type") or data.get("MsgDefIdr"),
            creation_datetime=data.get("creation_datetime") or data.get("CreDtTm"),
            payload=data,
        )

    def _from_text(self, text: str) -> ISO20022Message:
        stripped = text.strip()
        if not stripped:
            raise ISO20022ParseError("Payload text is blank.")

        # JSON branch — cheap structural decode, no schema enforcement.
        if stripped.startswith("{"):
            import json

            try:
                decoded = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ISO20022ParseError(f"Invalid JSON payload: {exc}") from exc
            if not isinstance(decoded, dict):
                raise ISO20022ParseError("JSON payload must be an object.")
            return self._from_dict(decoded)

        # XML branch — deferred. Record raw body so downstream code can
        # still identify the message exists without pretending we parsed it.
        if stripped.startswith("<"):
            return ISO20022Message(payload={"_raw_xml": stripped})

        raise ISO20022ParseError("Payload is neither JSON nor XML.")


__all__ = ["ISO20022Parser", "ISO20022Message", "ISO20022ParseError"]
