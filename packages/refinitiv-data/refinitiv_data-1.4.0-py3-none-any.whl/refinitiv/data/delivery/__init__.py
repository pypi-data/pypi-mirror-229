"""
The Delivery Layer provides objects allowing your application to interact with Refinitiv Data service via the
following delivery modes:

Request (HTTP Request/Response)
Stream (WebSockets)
Queue (Alerts)
Files (bulk)

Every data service of the Refinitiv Data exposes one or several of these delivery modes to make its data available to
client applications. For each of these delivery modes, the Delivery layer defines classes that can be used to easily
retrieve data from these data services in raw format that can be transformed into JSON.

Classes defined in the Delivery layer do not dependent on any specific data service exposed by the Refinitiv Data.
They are service-agnostic, meaning that you can use them to access to any service available on the platform.

Designed as the lowest abstraction layer, the Delivery layer targets developers who need specific features that are
not offered by other higher level abstraction layers (Content and Access layers). This layer targets professional
developers but can also be used by financial coders with good programming skills.
"""

__all__ = (
    "_dictionary",
    "cfs",
    "endpoint_request",
    "omm_stream",
    "rdp_stream",
)

from . import endpoint_request, omm_stream, rdp_stream, cfs, _dictionary
