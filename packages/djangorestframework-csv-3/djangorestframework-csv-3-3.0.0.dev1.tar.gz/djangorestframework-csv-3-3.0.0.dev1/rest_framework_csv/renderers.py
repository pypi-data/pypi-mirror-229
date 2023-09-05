from __future__ import annotations

import codecs
import csv
from io import StringIO
from types import GeneratorType
from typing import Any, Generator, Iterable, Mapping, TypedDict

from rest_framework.renderers import BaseRenderer

from rest_framework_csv.misc import Echo


class _CSVWriterOpts(TypedDict, total=False):
    dialect: csv.Dialect | type[csv.Dialect] | str
    delimiter: str
    quotechar: str
    escapechar: str
    doublequote: bool
    skipinitialspace: bool
    lineterminator: str
    quoting: int
    strict: bool


class _RendererContext(TypedDict, total=False):
    writer_opts: _CSVWriterOpts
    header: list[str]
    labels: dict[str, str]
    bom: bool


class CSVRenderer(BaseRenderer):
    """Renderer which serializes to CSV."""

    media_type: str = "text/csv"
    # XXX(dugab): specify optional parameters chartset and header?
    # https://datatracker.ietf.org/doc/html/rfc4180#section-3

    format: str = "csv"
    level_sep: str = "."
    header: list[str] | None = None
    labels: dict[str, str] | None = None  # {'<field>':'<label>'}
    writer_opts: _CSVWriterOpts | None = None

    def render(
        self,
        data: list[Any] | Mapping[str, list[Any]] | Any | None,
        accepted_media_type: str | None = None,
        renderer_context: _RendererContext | None = None,  # type: ignore[override]
    ) -> str | Any:
        """Renders serialized *data* into CSV."""
        if renderer_context is None:
            renderer_context = _RendererContext()
        if data is None:
            return ""

        if not isinstance(data, list):
            data = [data]

        writer_opts = renderer_context.get("writer_opts", self.writer_opts or _CSVWriterOpts())
        header = renderer_context.get("header", self.header)
        labels = renderer_context.get("labels", self.labels)

        table = self.tablize(data, header=header, labels=labels)
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer, **writer_opts)
        for row in table:
            csv_writer.writerow(row)

        return csv_buffer.getvalue()

    def tablize(
        self,
        data: Any | None,
        header: list[str] | None = None,
        labels: Mapping[str, str] | None = None,
    ) -> Generator[list[Any], None, None]:
        """Convert a list of data into a table.

        If there is a header provided to tablize it will efficiently yield each
        row as needed. If no header is provided, tablize will need to process
        each row in the data in order to construct a complete header. Thus, if
        you have a lot of data and want to stream it, you should probably
        provide a header to the renderer (using the `header` attribute, or via
        the `renderer_context`).
        """
        # Try to pull the header off of the data, if it's not passed in as an
        # argument.
        if not header and hasattr(data, "header"):
            header = data.header

        if data:
            # First, flatten the data (i.e., convert it to a list of
            # dictionaries that are each exactly one level deep).  The key for
            # each item designates the name of the column that the item will
            # fall into.
            data = self.flatten_data(data)

            # Get the set of all unique headers, and sort them (unless already provided).
            data, header = self.get_headers(data, header)

            # Return your "table", with the headers as the first row.
            if labels:
                yield [labels.get(x, x) for x in header]
            else:
                yield header

            # Create a row for each dictionary, filling in columns for which the
            # item has no data with None values.
            for item in data:
                row = [item.get(key, None) for key in header]
                yield row

        elif header:
            # If there's no data but a header was supplied, yield the header.
            if labels:
                yield [labels.get(x, x) for x in header]
            else:
                yield header

        else:
            # Generator will yield nothing if there's no data and no header
            pass

    def get_headers(
        self, data: Iterable[Mapping[str, Any]], header: None | list[str]
    ) -> tuple[Iterable[Mapping[str, Any]], list[str]]:
        """Get the set of all unique headers, and sort them (unless already provided)."""
        if header:
            return data, header

        # We don't have to materialize the data generator unless we
        # have to build a header.
        data = tuple(data)
        header_fields: set[str] = set()
        for item in data:
            header_fields.update(list(item.keys()))
        header = sorted(header_fields)
        return data, header

    def flatten_data(self, data: Iterable[Any]) -> Generator[dict[str, Any], None, None]:
        """Convert the given data collection to a list of dictionaries that are
        each exactly one level deep. The key for each value in the dictionaries
        designates the name of the column that the value will fall into.
        """
        for item in data:
            flat_item = self.flatten_item(item)
            yield flat_item

    def flatten_item(self, item: Any) -> dict[str, Any]:
        if isinstance(item, list):
            flat_item = self.flatten_list(item)
        elif isinstance(item, dict):
            flat_item = self.flatten_dict(item)
        else:
            flat_item = {"": item}

        return flat_item

    def nest_flat_item(self, flat_item: dict[str, Any], prefix: str) -> dict[str, Any]:
        """Given a "flat item" (a dictionary exactly one level deep), nest all of
        the column headers in a namespace designated by prefix.  For example:

         header... | with prefix... | becomes...
        -----------|----------------|----------------
         'lat'     | 'location'     | 'location.lat'
         ''        | '0'            | '0'
         'votes.1' | 'user'         | 'user.votes.1'

        """
        nested_item = {}
        for header, val in flat_item.items():
            nested_header = self.level_sep.join([prefix, header]) if header else prefix
            nested_item[nested_header] = val
        return nested_item

    def flatten_list(self, l: list[Any]) -> dict[str, Any]:  # noqa: E741
        flat_list = {}
        for index, item in enumerate(l):
            index_str = str(index)
            flat_item = self.flatten_item(item)
            nested_item = self.nest_flat_item(flat_item, index_str)
            flat_list.update(nested_item)
        return flat_list

    def flatten_dict(self, d: dict[str, Any]) -> dict[str, Any]:
        flat_dict = {}
        for key, item in d.items():
            key = str(key)
            flat_item = self.flatten_item(item)
            nested_item = self.nest_flat_item(flat_item, key)
            flat_dict.update(nested_item)
        return flat_dict


class CSVRendererWithUnderscores(CSVRenderer):
    level_sep: str = "_"


class CSVStreamingRenderer(CSVRenderer):
    def render(
        self,
        data: Any | None,
        media_type: str | None = None,
        renderer_context: _RendererContext | None = None,  # type: ignore[override]
    ) -> Generator[str, None, None]:
        """Renders serialized *data* into CSV to be used with Django
        StreamingHttpResponse. We need to return a generator here, so Django
        can iterate over it, rendering and returning each line.

        >>> renderer = CSVStreamingRenderer()
        >>> renderer.header = ['a', 'b']
        >>> data = [{'a': 1, 'b': 2}]
        >>> from django.http import StreamingHttpResponse
        >>> response = StreamingHttpResponse(renderer.render(data),
                                             content_type='text/csv')
        >>> response['Content-Disposition'] = 'attachment; filename="f.csv"'
        >>> # return response

        """
        if renderer_context is None:
            renderer_context = {}
        if data is None:
            yield ""

        self.labels = renderer_context.get("labels", self.labels)

        if not isinstance(data, GeneratorType) and not isinstance(data, list):
            data = [data]

        writer_opts = renderer_context.get("writer_opts", self.writer_opts or {})
        header = renderer_context.get("header", self.header)
        labels = renderer_context.get("labels", self.labels)
        bom = renderer_context.get("bom", False)

        if bom:
            yield str(codecs.BOM_UTF8)

        table = self.tablize(data, header=header, labels=labels)
        csv_buffer = Echo[str]()
        csv_writer = csv.writer(csv_buffer, **writer_opts)
        for row in table:
            yield csv_writer.writerow(row)


class PaginatedCSVRenderer(CSVRenderer):
    """Paginated renderer (when pagination is turned on for DRF)."""

    results_field: str = "results"

    def render(self, data: list[Any] | Mapping[str, list[Any] | Any | None] | Any | None, *args: Any, **kwargs: Any):
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        return super().render(data, *args, **kwargs)


class TSVRenderer(CSVRenderer):
    """Renderer which serializes to TSV."""

    media_type = "text/tab-separated-values"
    format = "tsv"
    writer_opts: _CSVWriterOpts = {  # noqa: RUF012
        "dialect": "excel-tab",
    }
