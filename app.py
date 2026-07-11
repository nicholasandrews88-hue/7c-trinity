import streamlit as st
import pandas as pd
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
.block-container { padding-top:.45rem; padding-bottom:1rem; max-width:1900px; }

.topbar {
    background:#0a0d12;
    border:1px solid #222936;
    border-radius:10px;
    padding:7px 10px;
    margin-bottom:7px;
    font-size:11px;
    font-weight:900;
    letter-spacing:.04em;
}

.compact-card {
    background:#0b0f15;
    border:1px solid #222936;
    border-radius:9px;
    padding:7px 9px;
    min-height:50px;
}

.compact-label {
    color:#7f8897;
    font-size:8px;
    font-weight:800;
    letter-spacing:.08em;
}

.compact-value {
    font-size:14px;
    font-weight:950;
    margin-top:2px;
}

.panel-title { font-size:16px; line-height:1.1; font-weight:950; margin-bottom:2px; }
.price-red { color:#ff6673; font-size:13px; font-weight:900; }
.price-green { color:#55ff99; font-size:13px; font-weight:900; }
.live { color:#55ff99; font-size:9px; font-weight:900; }

[data-testid="stTextInput"] label { font-size:9px; }
[data-testid="stTextInput"] input {
    font-size:11px;
    min-height:34px;
    height:34px;
    border-radius:8px;
    background:#0b0f15;
}

[data-testid="column"] { gap:.35rem; }
hr { margin:.55rem 0 !important; border-color:#1e2430 !important; }

.gex-wrap {
    border:1px solid #232938;
    border-radius:9px;
    overflow:hidden;
    margin-top:6px;
    background:#0a0d12;
    max-height:650px;
    overflow-y:auto;
}

.gex-table {
    width:100%;
    border-collapse:collapse;
    table-layout:fixed;
    font-size:9px;
}

.gex-table th {
    position:sticky;
    top:0;
    z-index:1;
    background:#171b24;
    color:#8e97a6;
    text-align:left;
    padding:5px 7px;
    font-size:8px;
    letter-spacing:.06em;
}

.gex-table td {
    padding:3px 7px;
    border-top:1px solid rgba(255,255,255,.06);
    font-weight:800;
}

.gex-table td:first-child {
    width:42%;
    text-align:right;
}

.gex-pos-low { background:#082014; color:#b8c0bb; }
.gex-pos-mid { background:#0d4c24; color:#fff; }
.gex-pos-high { background:#167f36; color:#fff; }
.gex-neg-low { background:#211029; color:#d7ccd9; }
.gex-neg-mid { background:#511167; color:#fff; }
.gex-neg-high { background:#8616b0; color:#fff; }
.gex-magnet { background:#f1d84b; color:#090909; }

.path-card {
    border:1px solid #242a36;
    background:#0b0f15;
    border-radius:8px;
    padding:6px 7px;
    margin-top:6px;
    font-size:9px;
    line-height:1.3;
}

.path-grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:5px;
}

.path-title {
    font-size:9px;
    font-weight:950;
    margin-bottom:2px;
}

.path-muted { color:#7f8897; }

.decision-strip {
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:6px;
    margin-top:8px;
}

.decision-item {
    background:#0b0f15;
    border:1px solid #222936;
    border-radius:8px;
    padding:7px 6px;
    text-align:center;
}

.decision-label {
    color:#7f8897;
    font-size:7px;
    font-weight:800;
    letter-spacing:.08em;
}

.decision-value {
    font-size:11px;
    font-weight:950;
    margin-top:2px;
}

.green { color:#55ff99; }
.red { color:#ff6673; }
.yellow { color:#f1d84b; }
.purple { color:#d16cff; }

@media (max-width:900px) {
    [data-testid="stHorizontalBlock"] { flex-wrap:wrap; }
    [data-testid="column"] {
        min-width:100% !important;
        width:100% !important;
        flex:1 1 100% !important;
    }
    .decision-strip { grid-template-columns:repeat(2,1fr); }
    .gex-wrap { max-height:none; }
}

.summary-panel {
    margin-top:8px;
    background:#0b0f15;
    border:1px solid #222936;
    border-radius:9px;
    padding:8px 9px;
}

.summary-grid {
    display:grid;
    grid-template-columns:repeat(6,1fr);
    gap:6px;
}

.summary-item {
    background:#080b10;
    border:1px solid #252c38;
    border-radius:8px;
    padding:7px 6px;
    text-align:center;
}

.summary-label {
    color:#7f8897;
    font-size:7px;
    font-weight:800;
    letter-spacing:.07em;
}

.summary-value {
    font-size:11px;
    font-weight:950;
    margin-top:2px;
}

.summary-note {
    margin-top:7px;
    color:#9aa3b1;
    font-size:8px;
    line-height:1.35;
}

@media (max-width:900px) {
    .summary-grid { grid-template-columns:repeat(2,1fr); }
}


.summary-note {
    margin-top:7px;
    color:#aab2bf;
    font-size:8px;
    line-height:1.45;
    background:#080b10;
    border:1px solid #252c38;
    border-radius:8px;
    padding:7px 8px;
}

.summary-note b {
    color:#f4f6f8;
}

.optimal-call { color:#55ff99; font-weight:900; }
.optimal-put { color:#ff6673; font-weight:900; }
.optimal-wait { color:#f1d84b; font-weight:900; }
.dp-proxy { color:#d16cff; font-weight:900; }

</style>
""", unsafe_allow_html=True)

# ---------------- TOP BAR ----------------

st.markdown(
    "<div class='topbar'>⚡ 7C TRINITY &nbsp;|&nbsp; LIVE GEX + FLOW &nbsp;|&nbsp; 15s</div>",
    unsafe_allow_html=True
)

top1, top2, top3, top4 = st.columns([1, 1, 1, 2])

with top1:
    st.markdown(
        "<div class='compact-card'><div class='compact-label'>MARKET</div>"
        "<div class='compact-value green'>LIVE</div></div>",
        unsafe_allow_html=True
    )

with top2:
    st.markdown(
        "<div class='compact-card'><div class='compact-label'>EDGE</div>"
        "<div class='compact-value'>DYNAMIC</div></div>",
        unsafe_allow_html=True
    )

with top3:
    st.markdown(
        "<div class='compact-card'><div class='compact-label'>SIDE</div>"
        "<div class='compact-value yellow'>FLOW</div></div>",
        unsafe_allow_html=True
    )

with top4:
    ticker_input = st.text_input(
        "TICKERS",
        "SPX, SPY, QQQ, IREN"
    )

symbols = [
    x.strip().upper()
    for x in ticker_input.split(",")
    if x.strip()
]

search_ticker = symbols[-1] if symbols else "SPY"

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

        rows.append((int(strike), formatted))

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

# ---------------- LIVE FLOW ----------------

flow_bias = "MIXED"
side = "WAIT"
swing = "NEUTRAL"
setup = "NO CLEAN EDGE"
risk = "MEDIUM"

call_premium = 0
put_premium = 0
net_call = 0
net_put = 0
raw_flow_data = {}

try:
    raw_flow_data = get_flow(search_ticker)
    latest_key = list(raw_flow_data["data"].keys())[-1]
    latest = raw_flow_data["data"][latest_key]

    call_premium = latest.get("midMarketCallPremium", 0)
    put_premium = latest.get("midMarketPutPremium", 0)
    net_call = latest.get("netCallPremium", 0)
    net_put = latest.get("netPutPremium", 0)

    if abs(net_call) > abs(net_put):
        flow_bias = "CALL FLOW DOMINANT"
        side, swing, setup, risk = "CALLS", "BULLISH", "DIP BUY", "MEDIUM"

    elif abs(net_put) > abs(net_call):
        flow_bias = "PUT FLOW DOMINANT"
        side, swing, setup, risk = "PUTS", "BEARISH", "POP FADE", "HIGH"

except Exception as e:
    raw_flow_data = {"error": str(e), "raw": raw_flow_data}

# ---------------- PANEL ----------------

def panel(symbol, price, change, rows):
    st.markdown(f"<div class='panel-title'>{html.escape(str(symbol))}</div>", unsafe_allow_html=True)

    is_live = str(change) == "LIVE"
    price_class = "price-green" if is_live else "price-red"
    status_label = "● LIVE" if is_live else "● SNAPSHOT"
    st.markdown(
        f"<div class='{price_class}'>${html.escape(str(price))} {html.escape(str(change))}</div>"
        f"<div class='live' style='margin-top:2px'>{status_label} &nbsp; "
        "<span style='color:#8d95a3;font-weight:600'>GEX Map</span></div>",
        unsafe_allow_html=True
    )

    def row_class(gex_text):
        val = str(gex_text)
        num = clean_gex_value(val)
        if "*" in val or "★" in val:
            return "gex-magnet"
        magnitude = abs(num)
        if num < 0:
            if magnitude >= 100_000_000:
                return "gex-neg-high"
            if magnitude >= 50_000_000:
                return "gex-neg-mid"
            return "gex-neg-low"
        if num > 0:
            if magnitude >= 10_000_000:
                return "gex-pos-high"
            if magnitude >= 5_000_000:
                return "gex-pos-mid"
            return "gex-pos-low"
        return "gex-pos-low"

    table_rows = []
    for strike, gex in rows:
        css_class = row_class(gex)
        table_rows.append(
            f"<tr class='{css_class}'><td>{html.escape(str(strike))}</td>"
            f"<td>{html.escape(str(gex))}</td></tr>"
        )

    table_html = (
        "<div class='gex-wrap'><table class='gex-table'>"
        "<thead><tr><th>Strike</th><th>GEX</th></tr></thead>"
        f"<tbody>{''.join(table_rows)}</tbody></table></div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)

    paths = build_paths(rows, price)
    if paths:
        bull_trigger, bear_trigger, upside, downside, largest_negative, largest_positive = paths
        upside_text = " → ".join(str(x) for x in upside) or "N/A"
        downside_text = " → ".join(str(x) for x in downside) or "N/A"
        path_html = f"""
        <div class='path-card'>
          <div class='path-grid'>
            <div><div class='path-title' style='color:#55ff99'>Bullish Path</div>
              <div><span class='path-muted'>Trigger:</span> {bull_trigger}</div>
              <div><span class='path-muted'>Targets:</span> {upside_text}</div>
            </div>
            <div><div class='path-title' style='color:#ff6673'>Bearish Path</div>
              <div><span class='path-muted'>Trigger:</span> {bear_trigger}</div>
              <div><span class='path-muted'>Targets:</span> {downside_text}</div>
            </div>
          </div>
          <div style='margin-top:5px'><span class='purple'>⚡ {largest_negative[0]}</span> &nbsp; <span class='yellow'>★ {largest_positive[0]}</span></div>
        </div>
        """
        st.markdown(path_html, unsafe_allow_html=True)

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



# ---------------- TABLES ON TOP ----------------

st.markdown("---")

cols = st.columns(len(symbols))

selected_rows = None
selected_debug = {}
selected_price = 0

for i, symbol in enumerate(symbols):
    rows, price, change, debug = get_rows_for_symbol(symbol)

    if symbol == search_ticker:
        selected_rows = rows
        selected_debug = debug
        selected_price = price

    with cols[i]:
        panel(symbol, price, change, rows)

if selected_rows is None:
    selected_rows = placeholder_rows()
    selected_price = 100

largest_positive, largest_negative, negative_below, upside_targets, downside_targets = analyze_rows(
    selected_rows,
    selected_price if selected_price else 100
)

primary_magnet = largest_positive[0] if largest_positive else "N/A"
danger_level = largest_negative[0] if largest_negative else "N/A"

neg_list = ", ".join([str(x) for x in negative_below[:8]]) if negative_below else "None"
upside_text = " → ".join([str(x) for x in upside_targets]) if upside_targets else "N/A"
downside_text = " → ".join([str(x) for x in downside_targets]) if downside_targets else "N/A"






# ---------------- COMPACT SUMMARY PANEL ----------------

flow_short = (
    "CALLS" if flow_bias == "CALL FLOW DOMINANT"
    else "PUTS" if flow_bias == "PUT FLOW DOMINANT"
    else "MIXED"
)

flow_class = (
    "green" if flow_short == "CALLS"
    else "red" if flow_short == "PUTS"
    else "yellow"
)

score = 50

if selected_price not in (None, "NO DATA"):
    try:
        px = float(selected_price)
        magnet_px = float(primary_magnet)
        danger_px = float(danger_level)

        if flow_short == "CALLS" and px >= magnet_px:
            score += 25
        elif flow_short == "PUTS" and px <= danger_px:
            score += 25
        elif flow_short in ("CALLS", "PUTS"):
            score += 12

        if abs(px - magnet_px) <= max(1, abs(px) * 0.003):
            score += 8
    except Exception:
        pass

score = min(score, 92)

if score >= 85:
    swing_grade = "A+"
    day_grade = "A"
elif score >= 75:
    swing_grade = "A"
    day_grade = "A"
elif score >= 65:
    swing_grade = "B"
    day_grade = "A"
elif score >= 55:
    swing_grade = "C"
    day_grade = "B"
else:
    swing_grade = "D"
    day_grade = "C"

if flow_short == "MIXED":
    risk_text = "HIGH"
    risk_class = "red"
elif score >= 75:
    risk_text = "LOW"
    risk_class = "green"
else:
    risk_text = "MED"
    risk_class = "yellow"

bias_text = (
    "BULLISH" if flow_short == "CALLS"
    else "BEARISH" if flow_short == "PUTS"
    else "NEUTRAL"
)

# Until a real dark-pool endpoint is connected, use the strongest dealer levels
# as clearly labeled dark-pool proxies rather than pretending they are real prints.
dp_primary = primary_magnet
dp_secondary = danger_level

if flow_short == "CALLS" and score >= 65:
    optimal_text = f"CALLS ABOVE {upside_targets[0] if upside_targets else primary_magnet}"
    optimal_class = "optimal-call"
elif flow_short == "PUTS" and score >= 65:
    optimal_text = f"PUTS BELOW {downside_targets[0] if downside_targets else danger_level}"
    optimal_class = "optimal-put"
else:
    optimal_text = "WAIT FOR CONFIRMATION"
    optimal_class = "optimal-wait"

if flow_short == "CALLS":
    summary_sentence = (
        f"{search_ticker} has bullish flow alignment. "
        f"Best continuation is above {upside_targets[0] if upside_targets else primary_magnet}; "
        f"loss of {danger_level} weakens the setup."
    )
elif flow_short == "PUTS":
    summary_sentence = (
        f"{search_ticker} has bearish flow alignment. "
        f"Best continuation is below {downside_targets[0] if downside_targets else danger_level}; "
        f"reclaiming {primary_magnet} weakens the setup."
    )
else:
    summary_sentence = (
        f"{search_ticker} is mixed. "
        f"Wait for acceptance above {primary_magnet} or below {danger_level}."
    )

summary_html = (
    f"<div class='summary-panel'>"
    f"<div class='summary-grid'>"
    f"<div class='summary-item'><div class='summary-label'>BIAS</div>"
    f"<div class='summary-value {flow_class}'>{bias_text}</div></div>"
    f"<div class='summary-item'><div class='summary-label'>SWING</div>"
    f"<div class='summary-value'>{swing_grade}</div></div>"
    f"<div class='summary-item'><div class='summary-label'>DAY</div>"
    f"<div class='summary-value'>{day_grade}</div></div>"
    f"<div class='summary-item'><div class='summary-label'>CONF</div>"
    f"<div class='summary-value'>{score}%</div></div>"
    f"<div class='summary-item'><div class='summary-label'>RISK</div>"
    f"<div class='summary-value {risk_class}'>{risk_text}</div></div>"
    f"<div class='summary-item'><div class='summary-label'>FLOW</div>"
    f"<div class='summary-value {flow_class}'>{flow_short}</div></div>"
    f"</div>"
    f"<div class='summary-note'>"
    f"<b>Optimal:</b> <span class='{optimal_class}'>{optimal_text}</span><br>"
    f"<b>DP Proxy:</b> <span class='dp-proxy'>{dp_primary}</span> / "
    f"<span class='dp-proxy'>{dp_secondary}</span><br>"
    f"<b>Read:</b> {summary_sentence}"
    f"</div>"
    f"</div>"
)

st.markdown(summary_html, unsafe_allow_html=True)
