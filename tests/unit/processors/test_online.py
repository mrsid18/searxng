# SPDX-License-Identifier: AGPL-3.0-or-later
# pylint: disable=missing-module-docstring,disable=missing-class-docstring,invalid-name

from searx.search.models import EngineRef, SearchQuery
from searx.search.processors import online
from searx import engines

from tests import SearxTestCase

TEST_ENGINE_NAME = "dummy engine"  # from the ./settings/test_settings.yml


class TestOnlineProcessor(SearxTestCase):

    def _get_params(self, online_processor, search_query, engine_category):
        params = online_processor.get_params(search_query, engine_category)
        self.assertIsNotNone(params)
        assert params is not None
        return params

    def test_get_params_default_params(self):
        engine = engines.engines[TEST_ENGINE_NAME]
        online_processor = online.OnlineProcessor(engine)
        search_query = SearchQuery('test', [EngineRef(TEST_ENGINE_NAME, 'general')], 'all', 0, 1, None, None, None)
        params = self._get_params(online_processor, search_query, 'general')
        self.assertIn('method', params)
        self.assertIn('headers', params)
        self.assertIn('data', params)
        self.assertIn('url', params)
        self.assertIn('cookies', params)
        self.assertIn('auth', params)

    def test_get_params_useragent(self):
        engine = engines.engines[TEST_ENGINE_NAME]
        online_processor = online.OnlineProcessor(engine)
        search_query = SearchQuery('test', [EngineRef(TEST_ENGINE_NAME, 'general')], 'all', 0, 1, None, None, None)
        params = self._get_params(online_processor, search_query, 'general')
        self.assertNotIn('User-Agent', params['headers'])

    def test_get_params_min_query_words(self):
        engine = engines.engines[TEST_ENGINE_NAME]
        online_processor = online.OnlineProcessor(engine)
        engine.min_query_words = 3
        try:

            def query(q, category):
                sq = SearchQuery(q, [EngineRef(TEST_ENGINE_NAME, category)], 'all', 0, 1, None, None, None)
                return online_processor.get_params(sq, category)

            self.assertIsNone(query('two words', 'general'))
            self.assertIsNotNone(query('three whole words', 'general'))
            # selected by its bang
            self.assertIsNotNone(query('two words', 'none'))
        finally:
            engine.min_query_words = 0
