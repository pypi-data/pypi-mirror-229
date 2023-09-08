from enum import unique
from typing import Union, List, Optional

from ..._tools import make_enum_arg_parser_by_members
from ..._base_enum import StrEnum


@unique
class SymbolTypes(StrEnum):
    """
    Symbol types to send in request, by default "RIC" is using.
    """

    RIC = "RIC"
    ISIN = "IssueISIN"
    CUSIP = "CUSIP"
    SEDOL = "SEDOL"
    TICKER_SYMBOL = "TickerSymbol"
    OA_PERM_ID = "IssuerOAPermID"
    LIPPER_ID = "FundClassLipperID"


SYMBOL_TYPE_VALUES = tuple(t for t in SymbolTypes)

OptSymbolTypes = Optional[Union[str, List[str], SymbolTypes, List[SymbolTypes]]]

symbol_types_arg_parser = make_enum_arg_parser_by_members(SymbolTypes)
