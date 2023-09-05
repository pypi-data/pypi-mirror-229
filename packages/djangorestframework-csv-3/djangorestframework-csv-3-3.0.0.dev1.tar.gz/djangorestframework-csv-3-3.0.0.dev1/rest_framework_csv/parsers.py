from __future__ import annotations

import csv
from typing import IO, Any, Generator, Generic, Iterable, Mapping, TypeVar

from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser

_Data = TypeVar("_Data")
_Files = TypeVar("_Files")


class _DataAndFiles(Generic[_Data, _Files]):
    data: _Data
    files: _Files

    def __init__(self, data: _Data, files: _Files) -> None:
        ...


def unicode_csv_reader(
    csv_data: Iterable[str],
    dialect: csv._DialectLike = csv.excel,
    **kwargs,
) -> Generator[list[str], None, None]:
    csv_reader = csv.reader(csv_data, dialect=dialect, **kwargs)
    yield from csv_reader


def universal_newlines(stream) -> Generator[str, None, None]:
    # It's possible that the stream was not opened in universal
    # newline mode. If not, we may have a single "row" that has a
    # bunch of carriage return (\r) characters that should act as
    # newlines. For that case, let's call splitlines on the row. If
    # it doesn't have any newlines, it will return a list of just
    # the row itself.
    yield from stream.splitlines()


class CSVParser(BaseParser):
    """Parses CSV serialized data.

    The parser assumes the first line contains the column names.
    """

    media_type: str = "text/csv"

    def parse(
        self,
        stream: IO[Any],
        media_type: str | None = None,
        parser_context: Mapping[str, Any] | None = None,
    ) -> Mapping[Any, Any] | _DataAndFiles:
        parser_context = parser_context or {}
        delimiter: str = parser_context.get("delimiter", ",")
        try:
            strdata: str | bytes = stream.read()
            binary = universal_newlines(strdata)
            rows = unicode_csv_reader(binary, delimiter=delimiter)

            header = [c.strip() for c in next(rows)]
            data = []

            for row in rows:
                row_data = dict(zip(header, row))
                data.append(row_data)

            return data
        except Exception as exc:
            raise ParseError("CSV parse error - %s" % str(exc)) from exc
