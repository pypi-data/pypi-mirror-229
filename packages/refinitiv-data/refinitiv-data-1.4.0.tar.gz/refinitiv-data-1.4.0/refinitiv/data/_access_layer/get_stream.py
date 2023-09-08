from contextlib import AbstractContextManager
from typing import Callable, Iterable, List, Optional, TYPE_CHECKING, Union

import pandas as pd

from ._mixed_streams import Stream
from ._pricing_recorder import PricingRecorder
from .._core.session import get_default, raise_if_closed
from .._tools import cached_property, iterator_str_arg_parser
from ..content._universe_stream import _UniverseStream

if TYPE_CHECKING:
    from .. import OpenState


def make_callback(on_data, logger):
    def callback(update, ric, stream):
        try:
            stream = PricingStream(stream)
            df = pd.DataFrame(update, index=[ric])
            on_data(df, ric, stream)
        except Exception as error:
            logger.error(error)

    return callback


def open_pricing_stream(
    universe: Union[str, Iterable[str]],
    fields: Union[str, List[str]] = None,
    service: Optional[str] = None,
    on_data: Optional[Callable] = None,
) -> "PricingStream":
    """
    Creates and opens a pricing stream.

    Parameters
    ----------
    universe : str | List[str]
        Instruments to request.
    fields : str | list, optional
        Fields to request.
    service : str, optional
        Name of the streaming service publishing the instruments.
    on_data : function, optional
        Callback function.

    Returns
    ----------
    PricingStream

    Examples
    -------
    >>> import refinitiv.data as rd
    >>> def callback(updated_data, ric, stream):
    ...    print(updated_data)
    >>> pricing_stream = rd.open_pricing_stream(universe=['EUR='], fields=['BID', 'ASK', 'OPEN_PRC'], on_data=callback)  # noqa
    """
    session = get_default()
    raise_if_closed(session)

    logger = session.logger()

    universe = iterator_str_arg_parser.get_list(universe)
    _stream = Stream(universe=universe, fields=fields, service=service)

    if on_data:
        _stream.on_update(make_callback(on_data, logger))
        _stream.on_refresh(make_callback(on_data, logger))

    stream = PricingStream(_stream)
    stream.open()
    return stream


class PricingStream(AbstractContextManager):
    def __init__(self, stream):
        self._stream: Stream = stream

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def open(self, with_updates: bool = True) -> "OpenState":
        return self._stream.open(with_updates=with_updates)

    def close(self) -> "OpenState":
        return self._stream.close()

    def get_snapshot(
        self,
        universe: Union[str, List[str], None] = None,
        fields: Optional[List[str]] = None,
        convert: bool = True,
    ) -> "pd.DataFrame":
        return self._stream.get_snapshot(universe=universe, fields=fields, convert=convert)

    def _get_fields(self, universe: str, fields: Optional[list] = None) -> dict:
        return self._stream._get_fields(universe=universe, fields=fields)

    def add_instruments(self, *args):
        self._stream.add_instruments(*args)

    def remove_instruments(self, *args):
        self._stream.remove_instruments(*args)

    def __getitem__(self, item) -> "_UniverseStream":
        return self._stream.__getitem__(item)

    def __iter__(self):
        return self._stream.__iter__()

    @cached_property
    def recorder(self) -> PricingRecorder:
        return PricingRecorder(self._stream._stream)
