"""
Simple stub for MetaTrader5 module when the real package is unavailable.
This fake implementation returns empty data structures or default values so the
rest of the application can run without MT5 access. It's intentionally minimal
and should be improved if more behaviour is needed for tests.
"""

from typing import Any


class _Dummy:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def _asdict(self):
        return self.__dict__

    def __getattr__(self, name: str) -> Any:
        # any extra attribute just returns None or zero
        return None


# constants (values don't matter as long as they exist)
TIMEFRAME_M1 = 1
TIMEFRAME_M5 = 2
TIMEFRAME_M15 = 3
TIMEFRAME_M30 = 4
TIMEFRAME_H1 = 5
TIMEFRAME_H4 = 6
TIMEFRAME_H12 = 7
TIMEFRAME_D1 = 8
TIMEFRAME_W1 = 9
TIMEFRAME_MN1 = 10

ORDER_TYPE_BUY = 0
ORDER_TYPE_SELL = 1
ORDER_TYPE_BUY_LIMIT = 2
ORDER_TYPE_SELL_LIMIT = 3
ORDER_TYPE_BUY_STOP = 4
ORDER_TYPE_SELL_STOP = 5

ORDER_FILLING_FOK = 0
ORDER_FILLING_IOC = 1
ORDER_FILLING_RETURN = 2

TRADE_ACTION_DEAL = 0
ORDER_TIME_GTC = 0


# stubbed functions

def initialize() -> bool:
    return True


def last_error():
    return 0


def shutdown():
    return True


def orders_get():
    return []


def positions_get():
    return []


def orders_total():
    return 0


def positions_total():
    return 0


def history_deals_total(*args, **kwargs):
    return 0


def history_deals_get(*args, **kwargs):
    return []


def symbol_info(symbol: str) -> Any:
    # return a dummy object with required attributes
    return _Dummy(visible=True, point=0.0, filling_mode=0)


def symbol_select(symbol: str, show: bool) -> bool:
    return True


def symbol_info_tick(symbol: str) -> Any:
    return _Dummy(ask=0.0, bid=0.0)


def copy_rates_from_pos(symbol, timeframe, start, count):
    return []


def account_info():
    return _Dummy()


def terminal_info():
    return _Dummy()


def order_check(request):
    # retcode 0 indicates success
    return _Dummy(retcode=0, comment="")


def order_send(request):
    return _Dummy(retcode=10009, order=0, volume=request.get("volume", 0), price=request.get("price", 0), bid=0.0, ask=0.0)


# alias to mimic module behaviour
class _Module:
    pass

# populate module attributes with above
import sys
_module = sys.modules[__name__]
# convert to list to avoid modifying while iterating
for name in list(globals().keys()):
    if not name.startswith("_"):
        setattr(_Module, name, globals()[name])

# expose everything at module level
for name, value in list(globals().items()):
    if not name.startswith("_"):
        setattr(sys.modules[__name__], name, value)
