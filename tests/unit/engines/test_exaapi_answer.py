# SPDX-License-Identifier: AGPL-3.0-or-later
# pylint: disable=missing-module-docstring,missing-class-docstring

from unittest import mock

from searx.engines import exaapi_answer
from searx.result_types import Answer, MainResult
from tests import SearxTestCase


class TestExaAnswer(SearxTestCase):

    def test_response(self):
        resp = mock.Mock()
        resp.json.return_value = {
            "answer": " Tokio is the most widely used async runtime. ",
            "citations": [
                {"url": "https://tokio.rs", "title": "Tokio", "publishedDate": "2025-01-02T00:00:00Z"},
                {"title": "no url"},
                {"url": "https://docs.rs/tokio"},
            ],
        }
        results = list(exaapi_answer.response(resp))
        answers = [r for r in results if isinstance(r, Answer)]
        mains = [r for r in results if isinstance(r, MainResult)]
        self.assertEqual(len(answers), 1)
        self.assertEqual(answers[0].answer, "Tokio is the most widely used async runtime.")
        self.assertEqual(answers[0].url, "https://tokio.rs")
        self.assertEqual([m.url for m in mains], ["https://tokio.rs", "https://docs.rs/tokio"])
        self.assertEqual(mains[1].title, "https://docs.rs/tokio")

    def test_response_no_answer(self):
        resp = mock.Mock()
        resp.json.return_value = {"answer": "", "citations": []}
        self.assertEqual(list(exaapi_answer.response(resp)), [])
