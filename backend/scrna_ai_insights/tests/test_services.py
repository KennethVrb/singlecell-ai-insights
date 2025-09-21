"""Unit tests for the service-layer utilities."""
from __future__ import annotations

from django.test import SimpleTestCase

from scrna_ai_insights import services
from scrna_ai_insights.schemas import ChatQueryRequest


class ServiceUtilitiesTests(SimpleTestCase):
    """Validate the behavior of service helper functions."""

    def test_list_reports_returns_all_reports(self) -> None:
        reports = services.list_reports()

        self.assertGreaterEqual(len(reports), 2)
        self.assertEqual(reports[0].id, "report-001")
        self.assertEqual(reports[0].title, "Patient A – Baseline")
        self.assertIn("html", reports[0].available_artifacts)

    def test_list_artifacts_requires_known_report(self) -> None:
        artifacts = services.list_artifacts("report-001")

        self.assertGreaterEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].type, "html")

        with self.assertRaises(services.ReportNotFoundError):
            services.list_artifacts("unknown-report")

    def test_answer_chat_query_includes_placeholder_details(self) -> None:
        payload = ChatQueryRequest(
            report_id="report-001",
            user_query="Summarize the findings",
            conversation_context=[],
        )

        response = services.answer_chat_query(payload)

        self.assertIn("placeholder answer", response.answer)
        self.assertEqual(len(response.citations), 1)
        self.assertEqual(response.citations[0].type, "html")
        self.assertEqual(response.follow_up_questions, [
            "Would you like a breakdown of the QC filtering thresholds?",
            "Should I summarize differential expression highlights?",
        ])

        with self.assertRaises(services.ReportNotFoundError):
            services.answer_chat_query(
                ChatQueryRequest(
                    report_id="unknown-report",
                    user_query="hello",
                )
            )
