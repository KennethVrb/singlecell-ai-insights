"""Public HTTP API powered by Django Ninja."""
from __future__ import annotations

from typing import List

from ninja import NinjaAPI
from ninja.errors import HttpError

from .schemas import ArtifactReference, ChatQueryRequest, ChatQueryResponse, ReportSummary
from .services import ReportNotFoundError, answer_chat_query, list_artifacts, list_reports

api = NinjaAPI(title="SingleCell AI Insights", version="0.1.0")


@api.get("/reports", response=List[ReportSummary])
def get_reports(request):
    """Return the catalog of curated nf-core/singlecell reports."""

    return [report.model_dump(mode="json") for report in list_reports()]



@api.get("/reports/{report_id}/artifacts", response=List[ArtifactReference])
def get_report_artifacts(request, report_id: str):
    """Return artifact references tied to a single report."""

    try:
        return [artifact.model_dump(mode="json") for artifact in list_artifacts(report_id)]
    except ReportNotFoundError as exc:  # pragma: no cover - defensive branch
        raise HttpError(404, str(exc)) from exc


@api.post("/chat/query", response=ChatQueryResponse)
def post_chat_query(request, payload: ChatQueryRequest):
    """Return a placeholder chat response for the requested report."""

    try:
        return answer_chat_query(payload).model_dump(mode="json")
    except ReportNotFoundError as exc:
        raise HttpError(404, str(exc)) from exc
