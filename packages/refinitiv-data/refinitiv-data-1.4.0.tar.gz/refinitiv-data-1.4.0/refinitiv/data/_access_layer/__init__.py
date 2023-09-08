"""Access layer.

Access layer provides a set of simplified interfaces offering coders uniform access to the breadth and depth of
financial data and services available on the Refinitiv Data Platform. The platform refers to the layer of data
services providing streaming and non-streaming content, bulk content and even more, serving different client types
from the simple desktop interface to the enterprise application.
"""

from .dates_and_calendars import *
from .get_data_func import get_data
from .get_history_func import get_history
from .get_stream import *
from .news import *
from .session import *
