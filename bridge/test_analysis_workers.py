"""Local analysis worker ceiling: status, validated edits and persistence."""

import json
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from conversation_selection import ConversationSelectionStore
from real_backend import Backend
from real_http import make_handler


class StubSource:
    def __init__(self, workdir):
        self.workdir = workdir
        self.account = "wxid_real_a_abcd"

    def verified_identity(self, *, messages=False):
        return self.account, self.workdir

    def sessions(self):
        return {"account": self.account, "sessions": [], "messagesReady": False}


class StubAnalyzer:
    model = {"state": "ready"}


class AnalysisWorkerSettingsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        with mock.patch("backend_service.save_worker_settings"):
            self.backend = Backend(StubSource(root / "snapshot"), StubAnalyzer(),
                                   selection_store=ConversationSelectionStore(root / "results"))
        self.addCleanup(self.backend.shutdown)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.backend))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.thread.join, 2)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def request(self, method, body=None):
        payload = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"} if body is not None else {}
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            connection.request(method, "/api/analysis-workers", body=payload, headers=headers)
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_status_reports_the_configured_ceiling_and_limit(self):
        status, data = self.request("GET")
        self.assertEqual(status, 200)
        self.assertEqual(data["workers"], 1)
        self.assertEqual(data["max"], 4)
        self.assertFalse(data["elastic"])
        self.assertEqual(data["limit"], 1)
        self.assertIn("gpu", data)

    def test_edits_are_validated_and_the_choice_is_persisted(self):
        for body in ({"workers": 0}, {"workers": 9}, {"workers": "2"},
                     {"workers": True}, {"elastic": "yes"}):
            with self.subTest(body=body):
                self.assertEqual(self.request("POST", body)[0], 400)
        with mock.patch("backend_service.save_worker_settings") as saved:
            status, data = self.request("POST", {"workers": 1, "elastic": False})
            self.assertEqual(status, 200)
            self.assertEqual(data["workers"], 1)
            saved.assert_called_once_with(1, False)


if __name__ == "__main__":
    unittest.main()
