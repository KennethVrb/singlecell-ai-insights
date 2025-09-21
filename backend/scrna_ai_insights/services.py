"""Service-layer utilities powering the API endpoints."""
from __future__ import annotations

from typing import Dict, Iterable, List

from .schemas import ArtifactReference, ChatQueryRequest, ChatQueryResponse, ReportSummary


class ReportNotFoundError(LookupError):
    """Raised when a report identifier cannot be resolved."""


_REPORTS: List[ReportSummary] = [
    ReportSummary(
        id="report-001",
        title="Patient A – Baseline",
        description="nf-core/singlecell run 2024-01-15",
        available_artifacts=["html", "csv_summary", "umap_png"],
    ),
    ReportSummary(
        id="report-002",
        title="Patient A – Post Treatment",
        description="nf-core/singlecell run 2024-02-20",
        available_artifacts=["html", "csv_summary", "umap_png"],
    ),
]

_ARTIFACTS: Dict[str, List[ArtifactReference]] = {
    "report-001": [
        ArtifactReference(
            type="html",
            label="Interactive report",
            url="https://example.com/reports/report-001/index.html",
        ),
        ArtifactReference(
            type="csv_summary",
            label="QC metrics",
            url="https://example.com/reports/report-001/qc_metrics.csv",
        ),
        ArtifactReference(
            type="umap_png",
            label="UMAP overview",
            url="https://example.com/reports/report-001/umap.png",
        ),
    ],
    "report-002": [
        ArtifactReference(
            type="html",
            label="Interactive report",
            url="https://example.com/reports/report-002/index.html",
        ),
        ArtifactReference(
            type="csv_summary",
            label="QC metrics",
            url="https://example.com/reports/report-002/qc_metrics.csv",
        ),
        ArtifactReference(
            type="umap_png",
            label="UMAP overview",
            url="https://example.com/reports/report-002/umap.png",
        ),
    ],
}


def _require_report(report_id: str) -> None:
    if report_id not in {report.id for report in _REPORTS}:
        raise ReportNotFoundError(f"Report '{report_id}' was not found.")


def list_reports() -> Iterable[ReportSummary]:
    """Return metadata for all curated POC reports."""

    return list(_REPORTS)


def list_artifacts(report_id: str) -> Iterable[ArtifactReference]:
    """Return artifact references for a single report."""

    _require_report(report_id)
    return list(_ARTIFACTS.get(report_id, []))


def answer_chat_query(payload: ChatQueryRequest) -> ChatQueryResponse:
    """Produce a placeholder answer for a chat query.

    The implementation is intentionally simple—it demonstrates how LangChain
    orchestration, Bedrock calls, and retrieval outputs will eventually be wired
    in while still giving the frontend a predictable contract to work against.
    """

    _require_report(payload.report_id)

    sample_answer = (
        "This is a placeholder answer describing insights drawn from the "
        "selected single-cell report. The production implementation will "
        "reference retrieved context chunks and include citations."
    )

    citations = list(_ARTIFACTS[payload.report_id][:1])
    follow_ups = [
        "Would you like a breakdown of the QC filtering thresholds?",
        "Should I summarize differential expression highlights?",
    ]

    return ChatQueryResponse(answer=sample_answer, citations=citations, follow_up_questions=follow_ups)
