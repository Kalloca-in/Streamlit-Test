"""Debrief shapes returned to the frontend.

The debrief is computed once at session end. Its content is derived from
the live session state still in Redis, not from any persistent store.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.session import SessionStatus


class DebriefSummary(BaseModel):
    """Part 1 — honest summary."""

    status: SessionStatus
    turns: int
    duration_seconds: float
    headline: str  # short adaptive line, never humiliating


class TranscriptAnnotation(BaseModel):
    """Annotation attached to a transcript turn for Part 3."""

    turn_index: int
    label: str
    note: str


class DebriefBundle(BaseModel):
    """Full debrief payload."""

    summary: DebriefSummary
    confession: str = Field(
        description="Part 2 — first-person attacker confession. Literary tone."
    )
    annotations: list[TranscriptAnnotation] = Field(default_factory=list)
    can_replay: bool = False
    mirror_prompt: str | None = Field(
        default=None,
        description="Part 5 — single reflective question. No response captured.",
    )
    deletion_manifest: list[str] = Field(
        default_factory=list,
        description="Human-readable list of artefacts that will be wiped.",
    )
