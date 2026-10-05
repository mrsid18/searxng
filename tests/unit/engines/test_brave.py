# SPDX-License-Identifier: AGPL-3.0-or-later
# pylint: disable=missing-module-docstring,missing-class-docstring,protected-access

from searx.engines import brave

from tests import SearxTestCase


def _page(data_js: str) -> str:
    return (
        "<script>\n"
        "kit.start(app, element, {\n"
        "\tnode_ids: [0, 30],\n"
        f"\tdata: {data_js},\n"
        "\tform: null,\n"
        "\terror: null\n"
        "});\n"
        "</script>"
    )


class TestBraveExtractJsonData(SearxTestCase):

    def test_plain_object_literal(self):
        page = _page('[{type:"data",data:{a:1}},{type:"data",data:{body:{response:{x:[1,2,]}},uses:void 0}}]')
        data = brave.extract_json_data(page)
        self.assertEqual(data["data"][0]["data"], {"a": 1})
        self.assertEqual(data["data"][1]["data"], {"body": {"response": {"x": [1, 2]}}, "uses": None})

    def test_devalue_iife(self):
        page = _page(
            '[(function(a,b){return {type:"data",data:{lang:a,x:[a,b],n:null}}}("en",42)),'
            '(function(a){return {type:"data",data:{q:a,ok:true,miss:undefined}}}("lake"))]'
        )
        data = brave.extract_json_data(page)
        self.assertEqual(data["data"][0]["data"], {"lang": "en", "x": ["en", 42], "n": None})
        self.assertEqual(data["data"][1]["data"], {"q": "lake", "ok": True, "miss": None})

    def test_nested_iife_and_shadowing(self):
        page = _page('[(function(a,b){return {o:a,i:(function(a){return [a,b]}("inner"))}}("outer","b"))]')
        data = brave.extract_json_data(page)
        self.assertEqual(data["data"][0], {"o": "outer", "i": ["inner", "b"]})

    def test_string_escapes(self):
        page = _page(r"""[{s:"\u003Cb\u003E \"q\" \ud83d\ude00 \x41",t:'it\'s',k:"a:b,c"}]""")
        data = brave.extract_json_data(page)
        self.assertEqual(data["data"][0], {"s": '<b> "q" \U0001f600 A', "t": "it's", "k": "a:b,c"})

    def test_numbers_and_keys(self):
        page = _page('[{"quoted key":-1.5,0:2e3,key$_:.5}]')
        data = brave.extract_json_data(page)
        self.assertEqual(data["data"][0], {"quoted key": -1.5, "0": 2000.0, "key$_": 0.5})

    def test_unknown_identifier_raises(self):
        with self.assertRaises(ValueError):
            brave.extract_json_data(_page("[{a:someGlobal}]"))
