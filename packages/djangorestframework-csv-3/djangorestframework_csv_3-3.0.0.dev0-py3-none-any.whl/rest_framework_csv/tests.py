from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from types import GeneratorType

from django.test import TestCase

from .parsers import CSVParser
from .renderers import CSVRenderer, CSVStreamingRenderer, PaginatedCSVRenderer, _CSVWriterOpts


class TestCSVRenderer(TestCase):
    def test_tablize_a_list_with_no_elements(self):
        renderer = CSVRenderer()

        flat_gen = renderer.tablize([])
        flat = list(flat_gen)
        assert flat == []

    def test_tablize_a_list_with_atomic_elements(self):
        renderer = CSVRenderer()

        flat_gen = renderer.tablize([1, 2, "hello"])
        flat = list(flat_gen)
        assert flat == [[""], [1], [2], ["hello"]]

    def test_tablize_a_list_with_list_elements(self):
        renderer = CSVRenderer()

        flat_gen = renderer.tablize([[1, 2, 3], [4, 5], [6, 7, [8, 9]]])
        flat = list(flat_gen)
        assert flat == [
            ["0", "1", "2", "2.0", "2.1"],
            [1, 2, 3, None, None],
            [4, 5, None, None, None],
            [6, 7, None, 8, 9],
        ]

    def test_tablize_a_list_with_dictionary_elements(self):
        renderer = CSVRenderer()

        flat_gen = renderer.tablize([{"a": 1, "b": 2}, {"b": 3, "c": {"x": 4, "y": 5}}])
        flat = list(flat_gen)
        assert flat == [["a", "b", "c.x", "c.y"], [1, 2, None, None], [None, 3, 4, 5]]

    def test_tablize_a_list_with_mixed_elements(self):
        renderer = CSVRenderer()

        flat_gen = renderer.tablize([{"a": 1, "b": 2}, {"b": 3, "c": [4, 5]}, 6])
        flat = list(flat_gen)
        assert flat == [
            ["", "a", "b", "c.0", "c.1"],
            [None, 1, 2, None, None],
            [None, None, 3, 4, 5],
            [6, None, None, None, None],
        ]

    def test_tablize_a_list_with_unicode_elements(self):
        renderer = CSVRenderer()

        flat_gen = renderer.tablize([{"a": 1, "b": "hello\u2014goodbye"}])
        flat = list(flat_gen)
        assert flat == [["a", "b"], [1, "hello—goodbye"]]

    def test_tablize_with_labels(self):
        renderer = CSVRenderer()

        flat_gen = renderer.tablize([{"a": 1, "b": 2}, {"b": 3, "c": [4, 5]}, 6], labels={"a": "A", "c.0": "0c"})
        flat = list(flat_gen)
        assert flat == [
            ["", "A", "b", "0c", "c.1"],
            [None, 1, 2, None, None],
            [None, None, 3, 4, 5],
            [6, None, None, None, None],
        ]

    def test_render_a_list_with_unicode_elements(self):
        renderer = CSVRenderer()

        dump = renderer.render([{"a": 1, "b": "hello\u2014goodbye", "c": "https://example.com/"}])
        assert dump == "a,b,c\r\n1,hello—goodbye,https://example.com/\r\n"

    def test_render_ordered_rows(self):
        parser = CSVParser()
        csv_file = "v1,v2,v3\r\na,1,2.3\r\nb,4,5.6\r\n"
        data = parser.parse(StringIO(initial_value=csv_file))
        renderer = CSVRenderer()

        dump = renderer.render(data)
        assert dump == csv_file  # field order should be maintained

        dump = renderer.render(data, renderer_context={"header": ["v3", "v1", "v2"]})
        self.assertTrue(
            dump.startswith("v3,v1,v2\r\n"),  # field order should be overrideable
            'Failed to override the header. Should be "v3,v1,v2". ' f"Was {dump.split()[0]}",
        )

    def test_render_subset_of_fields(self):
        renderer = CSVRenderer()
        renderer.header = ["a", "c.x"]

        data = [{"a": 1, "b": 2}, {"b": 3, "c": {"x": 4, "y": 5}}]
        dump = renderer.render(data)
        assert dump == "a,c.x\r\n1,\r\n,4\r\n"

    def test_dynamic_render_subset_of_fields_with_labels(self):
        renderer = CSVRenderer()

        data = [{"a": 1, "b": 2}, {"b": 3, "c": {"x": 4, "y": 5}}]
        dump = renderer.render(data, renderer_context={"header": ["a", "c.x"], "labels": {"c.x": "x"}})
        assert dump == "a,x\r\n1,\r\n,4\r\n"

    def test_render_data_with_writer_opts_set_via_CSVRenderer(self):
        renderer = CSVRenderer()
        renderer.header = ["a", "b"]
        data = [{"a": "test", "b": "hello"}, {"a": "foo", "b": "bar"}]
        writer_opts: _CSVWriterOpts = {
            "quoting": csv.QUOTE_ALL,
            "quotechar": "|",
            "delimiter": ";",
        }
        renderer.writer_opts = writer_opts
        dump = renderer.render(data)
        assert dump.count(";") == 3
        assert "|test|" in dump
        assert "|hello|" in dump

    def test_render_data_with_writer_opts_set_via_renderer_context(self):
        renderer = CSVRenderer()
        renderer.header = ["a", "b"]
        data = [{"a": "test", "b": "hello"}, {"a": "foo", "b": "bar"}]
        writer_opts: _CSVWriterOpts = {
            "quoting": csv.QUOTE_ALL,
            "quotechar": "|",
            "delimiter": ";",
        }
        dump = renderer.render(data, renderer_context={"writer_opts": writer_opts})
        assert dump.count(";") == 3
        assert "|test|" in dump
        assert "|hello|" in dump


class TestCSVStreamingRenderer(TestCase):
    def setUp(self):
        self.header = ["a", "b"]
        self.data = [{"a": 1, "b": 2}]

    def test_renderer_return_type(self):
        renderer = CSVStreamingRenderer()
        renderer.header = self.header
        dump = renderer.render(self.data)
        assert isinstance(dump, GeneratorType)

    def test_renderer_value(self):
        renderer = CSVRenderer()
        renderer.header = self.header

        streaming_renderer = CSVStreamingRenderer()
        streaming_renderer.header = self.header

        renderer_data = renderer.render(self.data)
        streaming_renderer_data = "".join(streaming_renderer.render(self.data))
        assert renderer_data == streaming_renderer_data

    def test_renderer_generator_data(self):
        renderer = CSVStreamingRenderer()
        renderer.header = self.header

        def _generator():
            yield from self.data

        renderer_generator_dump = renderer.render(_generator())
        renderer_list_dump = renderer.render(self.data)
        assert isinstance(renderer_generator_dump, GeneratorType)
        assert isinstance(renderer_list_dump, GeneratorType)
        assert list(renderer_generator_dump) == list(renderer_list_dump)


class TestPaginatedCSVRenderer(TestCase):
    def setUp(self):
        self.header = ["a", "b"]
        self.data = [{"results": {"a": 1, "b": 2}}]

    def test_renderer_value(self):
        renderer = PaginatedCSVRenderer()
        renderer.header = ["a", "b"]

        data = {"results": [{"a": 1, "b": 2}]}
        dump = renderer.render(data)
        assert dump == "a,b\r\n1,2\r\n"


class TestCSVParser(TestCase):
    def test_parse_two_lines_flat_csv(self):
        parser = CSVParser()
        csv_file = "v1,v2,v3\r\na,1,2.3\r\nb,4,5.6\r\n"

        data = parser.parse(StringIO(csv_file))

        assert data == [{"v1": "a", "v2": "1", "v3": "2.3"}, {"v1": "b", "v2": "4", "v3": "5.6"}]

    def test_semi_colon_delimiter(self):
        parser = CSVParser()
        csv_file = "v1;v2;v3\r\na;1;2.3\r\nb;4;5.6\r\n"

        delimiter = ";"
        data = parser.parse(StringIO(csv_file), parser_context={"delimiter": delimiter})

        assert data == [{"v1": "a", "v2": "1", "v3": "2.3"}, {"v1": "b", "v2": "4", "v3": "5.6"}]

    def test_parse_stream_with_only_carriage_returns(self):
        parser = CSVParser()
        csv_file = "Name,ID,Country\rKathryn Miller,67,United States\rJen Mark,78,Canada"

        data = parser.parse(StringIO(csv_file))
        assert data == [
            {"Name": "Kathryn Miller", "ID": "67", "Country": "United States"},
            {"Name": "Jen Mark", "ID": "78", "Country": "Canada"},
        ]

    def test_parse_file_with_only_carriage_returns(self):
        CURDIR = Path(__file__).parent
        CSVFILE = CURDIR / "testfixtures" / "nonewlines.csv"

        parser = CSVParser()

        with CSVFILE.open("r") as csv_file:
            data = parser.parse(csv_file)
            assert data == [
                {"Name": "Kathryn Miller", "ID": "67", "Country": "United States"},
                {"Name": "Jen Mark", "ID": "78", "Country": "Canada"},
            ]

    def test_unicode_parsing(self):
        parser = CSVParser()
        csv_file = "col1,col2\r\nhello—goodbye,here—there"

        data = parser.parse(StringIO(csv_file))
        assert data == [{"col1": "hello—goodbye", "col2": "here—there"}]

    def test_shift_jis_parsing(self):
        # FIXME reading different encoding is a regression
        parser = CSVParser()
        csv_file = "col1,col2\r\nシフトジス,シフトジス2"

        data = parser.parse(StringIO(csv_file), parser_context={"encoding": "SHIFT_JIS"})
        assert data == [{"col1": "シフトジス", "col2": "シフトジス2"}]
