from itertools import product
from typing import List, Dict

import pandas as pd

from ._historical_raw_transf import transform_for_df_by_fields, transform_for_df_by_headers_names
from .._tools._dataframe import convert_dtypes
from .._types import Strings


def process_bad_raws(bad_raws, listofcolumns, last_raw_columns, fields, num_fields):
    listofcolumns_insert = listofcolumns.insert

    for idx, bad_raw in bad_raws:
        raw_columns = fields or last_raw_columns or "Field"
        inst_name = bad_raw["universe"]["ric"]
        if num_fields == 1:
            processed_columns = [inst_name]

        else:
            processed_columns = list(product([inst_name], raw_columns))

        listofcolumns_insert(idx, processed_columns)


def process_data(data_append, index_append, date, items, num_allcolumns, num_raws, left_num_columns):
    prev_idx = None
    counter = 0

    template = [pd.NA] * num_allcolumns
    for instidx, raw_data, raw_columns in items:
        if (counter != 0 and counter % num_raws == 0) or prev_idx == instidx:
            index_append(date)
            data_append(template)
            template = [pd.NA] * num_allcolumns
            prev_idx = instidx

        if prev_idx is None:
            prev_idx = instidx

        counter += 1

        left_idx = left_num_columns[instidx]
        right_idx = left_idx + len(raw_columns)
        for item, i in zip(raw_data, range(left_idx, right_idx)):
            template[i] = item

    index_append(date)
    data_append(template)


class HistoricalBuilder:
    def _prepare_columns(self, raws, listofcolumns, bad_raws, fields, universe, items_by_date, num_fields):
        columns = None
        listofcolumns_append = listofcolumns.append
        bad_raws_append = bad_raws.append
        for instidx, raw in enumerate(raws):
            # it means error in response for custom instruments
            if not raw:
                raw = {"universe": {"ric": universe[instidx]}}
                bad_raws_append((instidx, raw))
                continue

            # it means error in response for historical pricing
            if isinstance(raw, list):
                raw = raw[0]
                bad_raws_append((instidx, raw))
                continue

            # it means in response for historical pricing events
            if isinstance(raw, dict) and not raw.get("headers"):
                raw = {"universe": {"ric": universe[instidx]}}
                bad_raws_append((instidx, raw))
                continue

            else:
                if fields:
                    transformed = transform_for_df_by_fields(raw, fields)

                else:
                    transformed = transform_for_df_by_headers_names(raw)

            columns = transformed.fields

            for date, raw_data in zip(transformed.dates, transformed.data):
                items = items_by_date.setdefault(date, [])
                items.append((instidx, raw_data, columns))

            inst_name = raw["universe"]["ric"]
            if num_fields == 1:
                processed_columns = [inst_name]

            else:
                processed_columns = list(product([inst_name], columns))

            listofcolumns_append(processed_columns)

        return columns

    def build_one(self, raw: dict, fields: Strings, axis_name: str, **__) -> pd.DataFrame:
        if not raw["data"]:
            return pd.DataFrame()

        if fields:
            transformed = transform_for_df_by_fields(raw, fields)

        else:
            transformed = transform_for_df_by_headers_names(raw)

        data = transformed.data
        columns = transformed.fields
        index = transformed.dates

        inst_name = raw["universe"]["ric"]
        columns = pd.Index(data=columns, name=inst_name)
        index = pd.Index(data=index, name=axis_name)
        df = pd.DataFrame(data=data, columns=columns, index=index)
        df = convert_dtypes(df)
        df.sort_index(inplace=True)
        return df

    def build(self, raws: List[dict], universe: Strings, fields: Strings, axis_name: str, **__) -> pd.DataFrame:
        items_by_date: Dict[str, list] = {}
        listofcolumns = []
        num_raws = len(raws)
        bad_raws = []
        num_fields = len(fields)

        last_raw_columns = self._prepare_columns(
            raws, listofcolumns, bad_raws, fields, universe, items_by_date, num_fields
        )

        if not items_by_date:
            return pd.DataFrame()

        if bad_raws:
            process_bad_raws(bad_raws, listofcolumns, last_raw_columns, fields, num_fields)

        left_num_columns = {
            split_idx: sum([len(subcols) for subcols in listofcolumns[:split_idx]]) for split_idx in range(num_raws)
        }

        allcolumns = [col for subcolumns in listofcolumns for col in subcolumns]

        num_allcolumns = len(allcolumns)
        data = []
        index = []
        data_append = data.append
        index_append = index.append
        for date, items in items_by_date.items():
            num_items = len(items)

            if num_items > 1:
                process_data(
                    data_append,
                    index_append,
                    date,
                    items,
                    num_allcolumns,
                    num_raws,
                    left_num_columns,
                )

            else:
                index_append(date)
                instidx, raw_data, raw_columns = items[0]
                left = [pd.NA] * left_num_columns[instidx]
                right = [pd.NA] * (num_allcolumns - len(raw_columns) - len(left))
                data_append(left + raw_data + right)

        if num_fields == 1:
            columns = pd.Index(data=allcolumns, name=fields[0])

        else:
            columns = pd.MultiIndex.from_tuples(allcolumns)

        index = pd.Index(data=index, name=axis_name)
        df = pd.DataFrame(data=data, columns=columns, index=index)
        df = convert_dtypes(df)
        df.sort_index(inplace=True)
        return df


class CustomInstsBuilder(HistoricalBuilder):
    def build_one(self, raw: dict, fields: Strings, axis_name: str, **__) -> pd.DataFrame:
        if fields:
            transformed = transform_for_df_by_fields(raw, fields)

        else:
            transformed = transform_for_df_by_headers_names(raw)

        data = transformed.data
        columns = transformed.fields
        index = transformed.dates

        if all(i is pd.NA for j in data for i in j):
            return pd.DataFrame()

        inst_name = raw["universe"]["ric"]
        columns = pd.Index(data=columns, name=inst_name)
        index = pd.Index(data=index, name=axis_name)
        df = pd.DataFrame(data=data, columns=columns, index=index)
        df = convert_dtypes(df)
        df.sort_index(inplace=True)
        return df


historical_builder = HistoricalBuilder()
custom_insts_builder = CustomInstsBuilder()
