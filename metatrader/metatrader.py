from typing import Optional, Literal
from dataclasses import dataclass
from config.environments import config
from .common import bridge_get, bridge_post, ensure_mt5_connection


@dataclass
class OrderRequest:
    symbol: str
    volume: float
    order_type: Literal["BUY", "SELL", "BUY_LIMIT", "SELL_LIMIT", "BUY_STOP", "SELL_STOP"]
    sl_points: Optional[int] = None
    tp_points: Optional[int] = None
    price: Optional[float] = None
    deviation: int = 20
    magic: int = config.MAGIC_NUMBER
    comment: str = "X Particle order"


def send_order(symbol, volume, deviation, order_type, sl_points=None, tp_points=None, price=None, comment="X Particle order") -> dict:
    connected, error = ensure_mt5_connection()
    if not connected:
        return {"success": False, "error": error}
    try:
        quote = bridge_get(f"/quote?symbol={symbol}")
        ask = quote.get("ask", 0)
        bid = quote.get("bid", 0)
        point = quote.get("point", 0.00001)
        if order_type == "BUY":
            exec_price = ask
            sl = (exec_price - sl_points * point) if sl_points else 0.0
            tp = (exec_price + tp_points * point) if tp_points else 0.0
        elif order_type == "SELL":
            exec_price = bid
            sl = (exec_price + sl_points * point) if sl_points else 0.0
            tp = (exec_price - tp_points * point) if tp_points else 0.0
        else:
            exec_price = price or ask
            sl = 0.0
            tp = 0.0
        result = bridge_post("/order", {
            "symbol": symbol, "volume": volume, "order_type": order_type,
            "price": exec_price, "sl": sl, "tp": tp,
            "magic": config.MAGIC_NUMBER, "comment": comment, "type_filling": "FOK",
        })
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def close_order(ticket: int, deviation: int = 20, magic: int = config.MAGIC_NUMBER, comment: str = "Close by X Particle") -> dict:
    connected, error = ensure_mt5_connection()
    if not connected:
        return {"success": False, "error": error}
    try:
        return {"success": True, **bridge_post("/order/close", {"ticket": ticket})}
    except Exception as e:
        return {"success": False, "error": str(e)}


def modify_order(ticket: int, sl: float = None, tp: float = None, **kwargs) -> dict:
    return {"success": False, "error": "modify_order not supported via bridge"}
