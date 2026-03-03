import requests

BRIDGE_URL = "http://localhost:8891/v1"


def ensure_mt5_connection():
    try:
        r = requests.get(f"{BRIDGE_URL}/account", timeout=3)
        if r.status_code == 200:
            return True, None
        return None, f"Bridge error {r.status_code}: {r.text}"
    except requests.exceptions.ConnectionError:
        return None, "MT5 bridge offline - run: npm run dev in mt5-bridge/web/mt_nodejs"


def bridge_get(path: str, params: dict = None):
    r = requests.get(f"{BRIDGE_URL}{path}", params=params, timeout=5)
    r.raise_for_status()
    return r.json()


def bridge_post(path: str, body: dict = None):
    r = requests.post(f"{BRIDGE_URL}{path}", json=body or {}, timeout=5)
    r.raise_for_status()
    return r.json()


order_type_map = {
    "BUY": 0,
    "SELL": 1,
    "BUY_LIMIT": 2,
    "SELL_LIMIT": 3,
    "BUY_STOP": 4,
    "SELL_STOP": 5,
}
