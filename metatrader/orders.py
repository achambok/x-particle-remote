from .common import bridge_get, ensure_mt5_connection


def pending_orders():
    connected, error = ensure_mt5_connection()
    if not connected:
        return error
    try:
        result = bridge_get("/order/list")
        pending = result.get("pending", []) if isinstance(result, dict) else []
        return pending if pending else "Currently no pending orders"
    except Exception as e:
        return f"Error: {e}"


def active_positions():
    connected, error = ensure_mt5_connection()
    if not connected:
        return error
    try:
        result = bridge_get("/order/list")
        opened = result.get("opened", []) if isinstance(result, dict) else []
        return opened if opened else "Currently no active positions"
    except Exception as e:
        return f"Error: {e}"


def pending_orders_count():
    connected, error = ensure_mt5_connection()
    if not connected:
        return error
    try:
        return len(bridge_get("/order/list").get("pending", []))
    except Exception:
        return 0


def active_orders_count():
    connected, error = ensure_mt5_connection()
    if not connected:
        return error
    try:
        return len(bridge_get("/order/list").get("opened", []))
    except Exception:
        return 0


def deals_history_count(prev_days: int):
    connected, error = ensure_mt5_connection()
    if not connected:
        return error
    try:
        result = bridge_get("/history/orders", params={"mode": "history"})
        return len(result) if isinstance(result, list) else 0
    except Exception:
        return 0


def deals_history_list(prev_days: int):
    connected, error = ensure_mt5_connection()
    if not connected:
        return error
    try:
        return bridge_get("/history/orders", params={"mode": "history"})
    except Exception as e:
        return f"Error: {e}"


def deals_details(ticket: str | int):
    connected, error = ensure_mt5_connection()
    if not connected:
        return error
    try:
        return bridge_get("/history/orders", params={"mode": "history", "ticket": int(ticket)})
    except Exception as e:
        return f"Error: {e}"
