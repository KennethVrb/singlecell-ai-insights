"""Integration tests for the public Django Ninja API."""
from __future__ import annotations

import json

from django.test import SimpleTestCase


class ApiEndpointTests(SimpleTestCase):
    """Exercise the HTTP endpoints exposed by the backend."""

    def test_get_reports_returns_catalog(self) -> None:
        response = self.client.get("/api/reports")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsInstance(payload, list)
        self.assertGreaterEqual(len(payload), 2)
        first_report = payload[0]
        self.assertEqual(first_report["id"], "report-001")
        self.assertIn("title", first_report)
        self.assertIn("available_artifacts", first_report)

    def test_get_report_artifacts_success(self) -> None:
        response = self.client.get("/api/reports/report-001/artifacts")

        self.assertEqual(response.status_code, 200)
        artifacts = response.json()
        self.assertIsInstance(artifacts, list)
        self.assertGreaterEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0]["type"], "html")
        self.assertIn("url", artifacts[0])

    def test_get_report_artifacts_missing_report(self) -> None:
        response = self.client.get("/api/reports/unknown-report/artifacts")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Report 'unknown-report' was not found."})

    def test_post_chat_query_returns_answer(self) -> None:
        payload = {
            "report_id": "report-001",
            "user_query": "Summarize the findings",
            "conversation_context": [],
        }

        response = self.client.post(
            "/api/chat/query",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("placeholder answer", data["answer"])
        self.assertIn("citations", data)
        self.assertEqual(len(data["citations"]), 1)
        self.assertIn("follow_up_questions", data)
        self.assertEqual(len(data["follow_up_questions"]), 2)

    def test_post_chat_query_missing_report(self) -> None:
        payload = {
            "report_id": "unknown-report",
            "user_query": "Summarize the findings",
        }

        response = self.client.post(
            "/api/chat/query",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Report 'unknown-report' was not found."})
