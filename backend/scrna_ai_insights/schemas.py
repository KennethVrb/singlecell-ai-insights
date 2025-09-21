"""Data transfer schemas for the public API."""
from __future__ import annotations

from typing import List, Literal, Optional

from ninja import Schema
from pydantic import AnyHttpUrl, Field


class ReportSummary(Schema):
    """Summary metadata describing an nf-core/singlecell report."""

    id: str
    title: str
    description: str
    available_artifacts: List[str]


class ArtifactReference(Schema):
    """Reference to an artifact associated with a report."""

    type: str
    label: str
    url: AnyHttpUrl


class ChatMessage(Schema):
    """Represents a single message in an ongoing chat session."""

    role: Literal["user", "assistant"]
    content: str


class ChatQueryRequest(Schema):
    """Payload accepted by the chat endpoint."""

    report_id: str
    user_query: str
    conversation_context: List[ChatMessage] = Field(default_factory=list)


class ChatQueryResponse(Schema):
    """Model returned for a chat answer request."""

    answer: str
    citations: List[ArtifactReference] = Field(default_factory=list)
    follow_up_questions: Optional[List[str]] = None
