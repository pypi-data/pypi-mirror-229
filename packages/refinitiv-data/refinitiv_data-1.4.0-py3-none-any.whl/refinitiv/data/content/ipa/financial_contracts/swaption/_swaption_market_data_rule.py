import warnings

from ..._param_item import param_item
from ..._serializable import Serializable


class SwaptionMarketDataRule(Serializable):
    warnings.warn(
        "The SwaptionMarketDataRule class "
        "will be removed in future versions of the library (2.x). "
        "This parameter is not supported by the back-end anymore.",
        category=DeprecationWarning,
    )

    def __init__(self, discount=None, forward=None):
        super().__init__()
        self.discount = discount
        self.forward = forward

    def _get_items(self):
        return [
            param_item.to_kv("discount", self.discount),
            param_item.to_kv("forward", self.forward),
        ]
