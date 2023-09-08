import json
import typing

import numpy
import pandas as pd

from .._core.session._default_session_manager import _eikon_default_session_manager
from .._core.session.tools import is_closed

if typing.TYPE_CHECKING:
    from .._core.session._session import Session


def is_string_type(value):
    try:
        return isinstance(value, basestring)
    except NameError:
        return isinstance(value, str)


def get_json_value(json_data, name):
    if name in json_data:
        return json_data[name]
    else:
        return None


def is_list_of_string(values):
    return all(is_string_type(value) for value in values)


def check_for_string(parameter, name):
    if not is_string_type(parameter):
        raise ValueError("The parameter {} should be a string, found {}".format(name, str(parameter)))


def check_for_string_or_list_of_strings(parameter, name):
    if type(parameter) != list and (not parameter or not is_string_type(parameter)):
        raise ValueError(
            "The parameter {} should be a string or a list of string, found {}".format(name, type(parameter))
        )
    if type(parameter) == list and not is_list_of_string(parameter):
        raise ValueError(
            "All items in the parameter {} should be of data type string, found {}".format(
                name, [type(v) for v in parameter]
            )
        )


def check_for_int(parameter, name):
    if type(parameter) is not int:
        raise ValueError(
            "The parameter {} should be an int, found {} type value ({})".format(name, type(parameter), str(parameter))
        )


def build_list_with_params(values, name):
    if values is None:
        raise ValueError(name + " is None, it must be a string or a list of strings")

    if is_string_type(values):
        return [(v, None) for v in values.split()]
    elif type(values) is list:
        try:
            return [(value, None) if is_string_type(value) else (value[0], value[1]) for value in values]
        except Exception:
            raise ValueError(name + " must be a string or a list of strings or a tuple or a list of tuple")
    else:
        try:
            return values[0], values[1]
        except Exception:
            raise ValueError(name + " must be a string or a list of strings or a tuple or a list of tuple")


def build_list(values, name):
    if values is None:
        raise ValueError(name + " is None, it must be a string or a list of strings")

    if is_string_type(values):
        return [values.strip()]
    elif type(values) is list:
        if all(is_string_type(value) for value in values):
            return [value for value in values]
        else:
            raise ValueError(name + " must be a string or a list of strings")
    else:
        raise ValueError(name + " must be a string or a list of strings")


def build_dictionary(dic, name):
    if dic is None:
        raise ValueError(name + " is None, it must be a string or a dictionary of strings")

    if is_string_type(dic):
        return json.loads(dic)
    elif type(dic) is dict:
        return dic
    else:
        raise ValueError(name + " must be a string or a dictionary")


def tz_replacer(s: str) -> str:
    if isinstance(s, str):
        if s.endswith("Z"):
            s = s[:-1]
        elif s.endswith("-0000"):
            s = s[:-5]
        if s.endswith(".000"):
            s = s[:-4]
    return s


def set_default_session(session: "Session"):
    _eikon_default_session_manager.set_default_session(session)


def get_default_session(app_key=None) -> "Session":
    return _eikon_default_session_manager.get_default_session(app_key)


def close_session():
    _eikon_default_session_manager.get_default_session().close()


def set_app_key(app_key):
    _session = get_default_session(app_key)
    if is_closed(_session):
        _session.open()


def set_log_level(log_level):
    default_session = _eikon_default_session_manager.get_default_session()
    default_session.set_log_level(log_level)


def convert_content_data_to_df_udf(raw: dict) -> pd.DataFrame:
    selected_fields = ["versionCreated", "text", "storyId", "sourceCode"]

    raw_headlines = raw.get("headlines", [])
    first_created = [tz_replacer(headline["firstCreated"]) for headline in raw_headlines]
    headlines = [[headline[field] for field in selected_fields] for headline in raw_headlines]
    if len(headlines):
        df = pd.DataFrame(
            headlines,
            numpy.array(first_created, dtype="datetime64[ns]"),
            selected_fields,
        )

        if not df.empty:
            df = df.convert_dtypes()

    else:
        df = pd.DataFrame([], numpy.array(first_created, dtype="datetime64[ns]"), selected_fields)

    df["versionCreated"] = df.versionCreated.apply(pd.to_datetime)
    df.fillna(pd.NA, inplace=True)

    return df
