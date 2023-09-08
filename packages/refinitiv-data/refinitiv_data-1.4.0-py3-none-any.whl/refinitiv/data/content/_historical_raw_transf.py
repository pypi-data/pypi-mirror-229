from dataclasses import dataclass
from typing import List, Dict

import pandas as pd

from .._tools import convert_str_to_timestamp
from .._types import Strings, TimestampOrNaT


@dataclass
class _TransformedData:
    data: List[List]
    fields: Strings
    dates: List[TimestampOrNaT]


@dataclass
class _ParsedData:
    data: List[List]
    headers_names: Strings
    timestamp_idx: int
    timestamp_name: str


def _parse_raw(raw: dict) -> _ParsedData:
    headers_names = [header["name"] for header in raw["headers"]]

    timestamp_name = None
    if "DATE_TIME" in headers_names:
        timestamp_name = "DATE_TIME"
    elif "DATE" in headers_names:
        timestamp_name = "DATE"

    timestamp_idx = headers_names.index(timestamp_name)
    return _ParsedData(raw["data"], headers_names, timestamp_idx, timestamp_name)


def transform_for_df_by_fields(raw: dict, fields: Strings) -> _TransformedData:
    parsed = _parse_raw(raw)
    headers_names = parsed.headers_names
    timestamp_idx = parsed.timestamp_idx
    data = []
    dates = []
    for lst in parsed.data:
        date_item = lst[timestamp_idx]
        dates.append(convert_str_to_timestamp(date_item))
        newlst = []
        for field in fields:
            if field in headers_names:
                item = lst[headers_names.index(field)]
                newlst.append(pd.NA if item is None else item)

            else:
                newlst.append(pd.NA)

        data.append(newlst)

    return _TransformedData(data, fields, dates)


def transform_for_df_by_headers_names(raw: dict) -> _TransformedData:
    parsed = _parse_raw(raw)
    headers_names = parsed.headers_names
    timestamp_idx = parsed.timestamp_idx
    timestamp_name = parsed.timestamp_name
    data = []
    dates = []
    for lst in parsed.data:
        newlst = []
        for item, hdr_name in zip(lst, headers_names):
            if timestamp_name == hdr_name:
                dates.append(convert_str_to_timestamp(item))
                continue

            newlst.append(pd.NA if item is None else item)

        data.append(newlst)

    headers_names.pop(timestamp_idx)
    return _TransformedData(data, headers_names, dates)


def transform_to_dicts(raw: dict, fields: Strings, date_name: str) -> List[Dict]:
    parsed = _parse_raw(raw)
    headers_names = [header_name.casefold() for header_name in parsed.headers_names]
    timestamp_idx = parsed.timestamp_idx
    dicts = []
    fields = [f.casefold() for f in fields]
    for lst in parsed.data:
        newlst = []
        for field in fields:
            if field in headers_names:
                item = lst[headers_names.index(field)]
                newlst.append(pd.NA if item is None else item)

            else:
                newlst.append(pd.NA)

        dicts.append({date_name: lst[timestamp_idx], **dict(item for item in zip(fields, newlst))})

    return dicts
