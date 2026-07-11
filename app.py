import streamlit as st
import requests
import os
import json
import html
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="7C Trinity", layout="wide")
st_autorefresh(interval=15000, key="trinity_refresh")
SNAPSHOT_DIR = "snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

def save_snapshot(symbol, rows, price, change):
    if rows and price != "NO DATA":
        snapshot = {
            "saved_at": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
            "rows": rows,
            "price": price,
            "change": change
        }

        with open(f"{SNAPSHOT_DIR}/{symbol}_last.json", "w") as f:
            json.dump(snapshot, f)

def load_snapshot(symbol):
    path = f"{SNAPSHOT_DIR}/{symbol}_last.json"

    if os.path.exists(path):
        with open(path, "r") as f:
            snap = json.load(f)

        return snap["rows"], snap["price"], snap["change"], snap

    return None, "NO DATA", "API", {}

# ---------------- API ----------------

API_KEY = st.secrets["QUANTDATA_API_KEY"]
BASE_URL = "https://api.quantdata.us"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


# ---------------- STYLE ----------------

st.markdown("""
<style>
.stApp { background:#050607; color:#f4f6f8; }
.block-container { padding-top:.45rem; padding-bottom:1rem; max-width:1650px; }

#MainMenu, footer, header { visibility:hidden; }

.brand {
    display:flex;
    justify-content:space-between;
    align-items:center;
    background:#0a0d12;
    border:1px solid #202632;
    border-radius:10px;
    padding:7px 11px;
    margin-bottom:8px;
}

.brand-left {
    display:flex;
    align-items:center;
    gap:8px;
}

.brand-mark {
    color:#f1d84b;
    font-size:15px;
    font-weight:950;
    letter-spacing:.04em;
}

.brand-name {
    font-size:11px;
    font-weight:850;
    letter-spacing:.15em;
}

.live-dot {
    color:#55ff99;
    font-size:9px;
    font-weight:900;
    letter-spacing:.08em;
}

[data-testid="stTextInput"] label { display:none; }
[data-testid="stTextInput"] input {
    min-height:34px;
    height:34px;
    font-size:11px;
    border-radius:8px;
    background:#0b0f15;
}

[data-testid="stButton"] button {
    min-height:36px;
    height:36px;
    padding:4px 8px;
    border-radius:8px;
    border:1px solid #232a36;
    background:#0b0f15;
    color:#d7dbe2;
    font-size:10px;
    font-weight:850;
}

[data-testid="stButton"] button:hover {
    border-color:#f1d84b;
    color:#fff;
}

.ticker-strip {
    display:flex;
    gap:6px;
    margin:7px 0 10px;
    flex-wrap:wrap;
}

.summary-card {
    border:1px solid #232a36;
    background:#0b0f15;
    border-radius:9px;
    padding:8px 10px;
}

.symbol-big {
    font-size:17px;
    font-weight:950;
    letter-spacing:.08em;
}

.price-big {
    font-size:15px;
    font-weight:900;
    color:#55ff99;
    margin-top:2px;
}

.status-small {
    color:#8f98a6;
    font-size:9px;
    font-weight:750;
    margin-top:3px;
}

.mini-grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:7px;
    margin-top:12px;
}

.mini {
    border:1px solid #252c38;
    border-radius:8px;
    background:#080b10;
    text-align:center;
    padding:9px 5px;
}

.mini-value {
    font-size:14px;
    font-weight:950;
}

.mini-label {
    font-size:8px;
    color:#7d8694;
    margin-top:2px;
}

.green { color:#55ff99; }
.red { color:#ff6673; }
.yellow { color:#f1d84b; }
.purple { color:#d16cff; }

.level-stack {
    display:flex;
    flex-direction:column;
    gap:7px;
    margin-top:10px;
}

.level {
    border:1px solid #252c38;
    background:#080b10;
    border-radius:8px;
    text-align:center;
    padding:8px 5px;
    font-size:12px;
    font-weight:900;
}

.gex-wrap {
    border:1px solid #232938;
    border-radius:10px;
    overflow:hidden;
    background:#0a0d12;
    max-height:650px;
    overflow-y:auto;
}

.gex-table {
    width:100%;
    border-collapse:collapse;
    table-layout:fixed;
    font-size:10px;
}

.gex-table th {
    position:sticky;
    top:0;
    z-index:1;
    background:#161b23;
    color:#8e97a6;
    text-align:left;
    padding:6px 8px;
    font-size:8px;
    letter-spacing:.08em;
}

.gex-table td {
    padding:4px 8px;
    border-top:1px solid rgba(255,255,255,.06);
    font-weight:800;
}

.gex-table td:first-child {
    width:45%;
    text-align:right;
}

.gex-pos-low { background:#082014; color:#b8c1bb; }
.gex-pos-mid { background:#0d4c24; color:#fff; }
.gex-pos-high { background:#167f36; color:#fff; }
.gex-neg-low { background:#211029; color:#d7ccd9; }
.gex-neg-mid { background:#511167; color:#fff; }
.gex-neg-high { background:#8616b0; color:#fff; }
.gex-magnet { background:#f1d84b; color:#090909; }

@media (max-width:900px) {
    [data-testid="stHorizontalBlock"] { flex-wrap:wrap; }
    [data-testid="column"] {
        min-width:100% !important;
        width:100% !important;
        flex:1 1 100% !important;
    }
    .gex-wrap { max-height:none; }
}
</style>
""", unsafe_allow_html=True)

# ---------------- API FUNCTIONS ----------------

def post_quant(endpoint, payload):
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            json=payload,
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_flow(symbol):
    return post_quant(
        "/v1/options/tool/net-drift",
        {"ticker": symbol}
    )

def get_real_gex(symbol):
    data = post_quant(
        "/v1/options/tool/exposure-by-strike",
        {
            "greekMode": "GAMMA",
            "representationMode": "PER_ONE_DOLLAR_MOVE",
            "filter": {
                "ticker": symbol
            }
        }
    )

    if "data" not in data:
        return None, None, None, data

    ticker_data = data["data"].get(symbol)
    if not ticker_data:
        return None, None, None, data

    stock_price = ticker_data.get("stockPrice", 0)
    exposure_map = ticker_data.get("exposureMap", {})

    combined = {}

    for expiration, strikes in exposure_map.items():
        for strike, exposure in strikes.items():
            strike_float = float(strike)

            call_exposure = exposure.get("callExposure", 0)
            put_exposure = exposure.get("putExposure", 0)
            total_gex = call_exposure + put_exposure

            combined[strike_float] = combined.get(strike_float, 0) + total_gex

    if not combined:
        return None, stock_price, None, data

    closest = sorted(
        combined.items(),
        key=lambda x: abs(x[0] - float(stock_price))
    )[:50]

    closest = sorted(closest, key=lambda x: x[0], reverse=True)

    biggest_positive = max(closest, key=lambda x: x[1])[0]

    rows = []

    for strike, gex in closest:
        star = " ★" if strike == biggest_positive else ""

    rows = []

    for strike, gex in closest:
        star = " ★" if strike == biggest_positive else ""

        if abs(gex) >= 1_000_000:
            value = abs(gex) / 1_000_000

            if gex >= 0:
                formatted = f"${value:.2f}M{star}"
            else:
                formatted = f"-${value:.2f}M"

        elif abs(gex) >= 1000:
            value = abs(gex) / 1000

            if gex >= 0:
                formatted = f"${value:.1f}K{star}"
            else:
                formatted = f"-${value:.1f}K"

        else:
            value = abs(gex)

            if gex >= 0:
                formatted = f"${value:.0f}{star}"
            else:
                formatted = f"-${value:.0f}"

        display_strike = int(strike) if float(strike).is_integer() else round(float(strike), 2)
        rows.append((display_strike, formatted))

    return rows, round(stock_price, 2), "LIVE", data

def placeholder_rows():
    return [
        (100, "$2,100.0K"),
        (99, "$1,800.0K"),
        (98, "-$4,500.0K"),
        (97, "$6,200.0K ★"),
        (96, "-$1,900.0K"),
        (95, "$980.0K"),
        (94, "$755.0K"),
        (93, "-$310.0K"),
        (92, "$640.0K"),
        (91, "$220.0K"),
    ]

def get_rows_for_symbol(symbol):
    rows, price, change, debug = get_real_gex(symbol)

    # Live data available → save snapshot
    if rows and price != "NO DATA":
        save_snapshot(symbol, rows, price, change)
        return rows, price, change, debug

    # Live data unavailable → load last snapshot
    rows, price, change, snapshot = load_snapshot(symbol)

    if rows:
        return rows, price, "SNAPSHOT", snapshot

    # Nothing saved yet
    return placeholder_rows(), "NO DATA", "API", debug

# ---------------- GEX HELPERS ----------------

def clean_gex_value(gex):
    text = str(gex).replace("$", "").replace(",", "").replace("★", "").strip()

    multiplier = 1

    if "M" in text:
        multiplier = 1_000_000
        text = text.replace("M", "")

    elif "K" in text:
        multiplier = 1_000
        text = text.replace("K", "")

    return float(text) * multiplier


def analyze_rows(rows, stock_price):
    negative = []
    positive = []

    for strike, gex in rows:
        value = clean_gex_value(gex)

        if value < 0:
            negative.append((strike, value))
        else:
            positive.append((strike, value))

    largest_negative = min(negative, key=lambda x: x[1]) if negative else None
    largest_positive = max(positive, key=lambda x: x[1]) if positive else None

    below_price = [x for x in rows if float(x[0]) < float(stock_price)]
    above_price = [x for x in rows if float(x[0]) > float(stock_price)]

    downside_targets = sorted([x[0] for x in below_price], reverse=True)[:2]
    upside_targets = sorted([x[0] for x in above_price])[:2]

    negative_below = []

    for strike, gex in rows:
        if float(strike) < float(stock_price) and clean_gex_value(gex) < 0:
            negative_below.append(strike)

    return largest_positive, largest_negative, negative_below, upside_targets, downside_targets

def build_paths(rows, stock_price):
    cleaned = []

    for strike, gex in rows:
        try:
            cleaned.append((float(strike), clean_gex_value(gex)))
        except:
            continue

    if not cleaned:
        return None

    cleaned = sorted(cleaned, key=lambda x: x[0])

    below = [x for x in cleaned if x[0] < float(stock_price)]
    above = [x for x in cleaned if x[0] > float(stock_price)]

    largest_negative = min(cleaned, key=lambda x: x[1])
    largest_positive = max(cleaned, key=lambda x: x[1])

    bull_trigger = above[0][0] if above else None
    bear_trigger = below[-1][0] if below else None

    upside = [x[0] for x in above[:5]]
    downside = [x[0] for x in below[-5:]][::-1]

    return bull_trigger, bear_trigger, upside, downside, largest_negative, largest_positive




# ---------------- V2 HELPERS ----------------

def get_flow_bias(symbol):
    try:
        raw = get_flow(symbol)
        if "data" not in raw or not raw["data"]:
            return "MIXED"

        latest_key = list(raw["data"].keys())[-1]
        latest = raw["data"][latest_key]

        net_call = latest.get("netCallPremium", 0) or 0
        net_put = latest.get("netPutPremium", 0) or 0

        if abs(net_call) > abs(net_put):
            return "CALLS"
        if abs(net_put) > abs(net_call):
            return "PUTS"
    except Exception:
        pass

    return "MIXED"


def calc_score(price, paths, bias):
    score = 50

    if not paths or price in (None, "NO DATA"):
        return score

    bull_trigger, bear_trigger, upside, downside, largest_negative, largest_positive = paths
    price = float(price)
    magnet = float(largest_positive[0])
    accelerator = float(largest_negative[0])

    if bias == "CALLS" and price >= magnet:
        score += 25
    elif bias == "PUTS" and price <= accelerator:
        score += 25
    elif bias in ("CALLS", "PUTS"):
        score += 12

    if abs(price - magnet) <= max(1, abs(price) * .003):
        score += 8

    return min(score, 92)


def score_grade(score):
    if score >= 85:
        return "A+"
    if score >= 75:
        return "A"
    if score >= 65:
        return "B"
    if score >= 55:
        return "C"
    return "D"


def gex_class(gex_text):
    value = clean_gex_value(gex_text)
    text = str(gex_text)

    if "★" in text:
        return "gex-magnet"

    magnitude = abs(value)

    if value < 0:
        if magnitude >= 100_000_000:
            return "gex-neg-high"
        if magnitude >= 50_000_000:
            return "gex-neg-mid"
        return "gex-neg-low"

    if magnitude >= 10_000_000:
        return "gex-pos-high"
    if magnitude >= 5_000_000:
        return "gex-pos-mid"
    return "gex-pos-low"


def render_gex_table(rows):
    table_rows = []

    for strike, gex in rows:
        css_class = gex_class(gex)
        table_rows.append(
            f"<tr class='{css_class}'>"
            f"<td>{html.escape(str(strike))}</td>"
            f"<td>{html.escape(str(gex))}</td>"
            "</tr>"
        )

    st.markdown(
        "<div class='gex-wrap'>"
        "<table class='gex-table'>"
        "<thead><tr><th>STRIKE</th><th>GEX</th></tr></thead>"
        f"<tbody>{''.join(table_rows)}</tbody>"
        "</table>"
        "</div>",
        unsafe_allow_html=True
    )

# ---------------- HEADER ----------------

st.markdown("""
<div class='brand'>
    <div class='brand-left'>
        <span class='brand-mark'>7C</span>
        <span class='brand-name'>TRINITY</span>
    </div>
    <span class='live-dot'>● LIVE</span>
</div>
""", unsafe_allow_html=True)

if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["SPX", "SPY", "QQQ", "IREN"]

if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = st.session_state.watchlist[0]

search_col, add_col = st.columns([5, 1])

with search_col:
    add_symbol = st.text_input(
        "Ticker",
        placeholder="Add ticker",
        key="add_symbol"
    ).upper().strip()

with add_col:
    if st.button("+", width="stretch") and add_symbol:
        if add_symbol not in st.session_state.watchlist:
            st.session_state.watchlist.append(add_symbol)
        st.session_state.selected_symbol = add_symbol

watchlist = st.session_state.watchlist

ribbon_cols = st.columns(len(watchlist))
ribbon_data = {}

for i, symbol in enumerate(watchlist):
    rows, price, change, debug = get_rows_for_symbol(symbol)
    ribbon_data[symbol] = (rows, price, change, debug)

    with ribbon_cols[i]:
        if st.button(
            f"{symbol}\n{price}",
            key=f"select_{symbol}",
            width="stretch"
        ):
            st.session_state.selected_symbol = symbol

selected_symbol = st.session_state.selected_symbol

if selected_symbol not in ribbon_data:
    ribbon_data[selected_symbol] = get_rows_for_symbol(selected_symbol)

rows, price, change, debug = ribbon_data[selected_symbol]
paths = build_paths(rows, price) if rows and price != "NO DATA" else None
bias = get_flow_bias(selected_symbol)
score = calc_score(price, paths, bias)
grade = score_grade(score)

if bias == "CALLS":
    bias_icon = "▲"
    bias_class = "green"
elif bias == "PUTS":
    bias_icon = "▼"
    bias_class = "red"
else:
    bias_icon = "◆"
    bias_class = "yellow"

if paths:
    bull_trigger, bear_trigger, upside, downside, largest_negative, largest_positive = paths
    magnet = largest_positive[0]
    accelerator = largest_negative[0]
else:
    bull_trigger = bear_trigger = magnet = accelerator = "—"
    upside = []
    downside = []

left_html = (
    f"<div class='summary-card'>"
    f"<div class='symbol-big'>{html.escape(selected_symbol)}</div>"
    f"<div class='price-big'>${html.escape(str(price))}</div>"
    f"<div class='status-small'>● {html.escape(str(change))}</div>"
    f"<div class='mini-grid'>"
    f"<div class='mini'><div class='mini-value {bias_class}'>{bias_icon}</div>"
    f"<div class='mini-label'>{html.escape(bias)}</div></div>"
    f"<div class='mini'><div class='mini-value'>{grade}</div>"
    f"<div class='mini-label'>GRADE</div></div>"
    f"<div class='mini'><div class='mini-value'>{score}%</div>"
    f"<div class='mini-label'>CONF</div></div>"
    f"<div class='mini'><div class='mini-value yellow'>★</div>"
    f"<div class='mini-label'>{magnet}</div></div>"
    f"</div>"
    f"<div class='level-stack'>"
    f"<div class='level green'>▲ {bull_trigger}</div>"
    f"<div class='level red'>▼ {bear_trigger}</div>"
    f"<div class='level yellow'>★ {magnet}</div>"
    f"<div class='level purple'>⚡ {accelerator}</div>"
    f"</div>"
    f"</div>"
)

right_up = "".join(
    f"<div class='level green'>▲ {level}</div>"
    for level in upside
) or "<div class='level'>—</div>"

right_down = "".join(
    f"<div class='level red'>▼ {level}</div>"
    for level in downside
) or "<div class='level'>—</div>"

right_html = (
    f"<div class='summary-card'>"
    f"<div class='level-stack'>{right_up}</div>"
    f"<div style='height:12px'></div>"
    f"<div class='level-stack'>{right_down}</div>"
    f"</div>"
)

left_col, center_col, right_col = st.columns([1.05, 2.8, 1.05])

with left_col:
    st.markdown(left_html, unsafe_allow_html=True)

with center_col:
    if rows:
        render_gex_table(rows)
    else:
        st.warning("No live data or saved snapshot is available.")

with right_col:
    st.markdown(right_html, unsafe_allow_html=True)
