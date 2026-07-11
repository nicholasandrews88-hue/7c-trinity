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
:root {
    --bg:#050607;
    --panel:#0b0f14;
    --panel-2:#11161d;
    --line:rgba(255,255,255,.10);
    --muted:#8e98a7;
    --text:#f4f6f8;
    --green:#73f6a7;
    --red:#ff6673;
    --yellow:#f5dd4f;
    --purple:#b84cff;
}

.stApp {
    background:
        radial-gradient(circle at 18% -10%, rgba(90,255,135,.08), transparent 28%),
        radial-gradient(circle at 92% 5%, rgba(184,76,255,.07), transparent 26%),
        var(--bg);
    color:var(--text);
}

.block-container {
    padding-top:.45rem;
    padding-bottom:6rem;
    max-width:1920px;
}

#MainMenu, footer, header {
    visibility:hidden;
}

.topbar {
    background:rgba(12,16,22,.88);
    border:1px solid var(--line);
    border-radius:16px;
    padding:9px 12px;
    margin-bottom:8px;
    font-size:11px;
    font-weight:900;
    letter-spacing:.05em;
    box-shadow:0 10px 30px rgba(0,0,0,.22);
    backdrop-filter:blur(12px);
}

.toolbar {
    display:flex;
    gap:7px;
    align-items:center;
    flex-wrap:wrap;
    margin-bottom:9px;
}

.pill {
    display:inline-flex;
    align-items:center;
    gap:6px;
    min-height:34px;
    padding:0 11px;
    border-radius:12px;
    border:1px solid var(--line);
    background:rgba(15,20,27,.90);
    color:#dfe4ea;
    font-size:10px;
    font-weight:850;
    box-shadow:inset 0 1px 0 rgba(255,255,255,.03);
}

.pill-green {
    border-color:rgba(115,246,167,.30);
    background:rgba(26,93,50,.28);
    color:var(--green);
}

.pill-purple {
    border-color:rgba(184,76,255,.35);
    background:rgba(77,22,104,.25);
    color:#d58aff;
}

.pill-yellow {
    border-color:rgba(245,221,79,.35);
    background:rgba(110,91,11,.27);
    color:var(--yellow);
}

.compact-card {
    background:linear-gradient(180deg, rgba(18,23,31,.96), rgba(10,14,20,.96));
    border:1px solid var(--line);
    border-radius:13px;
    padding:8px 10px;
    min-height:52px;
    box-shadow:0 8px 22px rgba(0,0,0,.16);
}

.compact-label {
    color:var(--muted);
    font-size:8px;
    font-weight:850;
    letter-spacing:.10em;
}

.compact-value {
    font-size:15px;
    font-weight:950;
    margin-top:2px;
}

.panel-title {
    font-size:17px;
    line-height:1.05;
    font-weight:950;
    margin-bottom:2px;
    letter-spacing:.03em;
}

.price-red {
    color:var(--red);
    font-size:14px;
    font-weight:900;
}

.price-green {
    color:var(--green);
    font-size:14px;
    font-weight:900;
}

.live {
    color:var(--green);
    font-size:9px;
    font-weight:900;
}

[data-testid="stTextInput"] label {
    font-size:9px;
    color:var(--muted);
}

[data-testid="stTextInput"] input {
    font-size:11px;
    min-height:38px;
    height:38px;
    border-radius:13px;
    background:rgba(12,16,22,.90);
    border:1px solid var(--line);
}

[data-testid="column"] {
    gap:.35rem;
}

hr {
    margin:.6rem 0 !important;
    border-color:rgba(255,255,255,.08) !important;
}

.gex-wrap {
    border:1px solid var(--line);
    border-radius:14px;
    overflow:hidden;
    margin-top:6px;
    background:#09100a;
    max-height:720px;
    overflow-y:auto;
    box-shadow:0 12px 30px rgba(0,0,0,.20);
}

.gex-table {
    width:100%;
    border-collapse:collapse;
    table-layout:fixed;
    font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size:10px;
}

.gex-table th {
    position:sticky;
    top:0;
    z-index:3;
    background:#11161d;
    color:#aeb7c3;
    text-align:left;
    padding:7px 8px;
    font-size:8px;
    letter-spacing:.09em;
    border-bottom:1px solid var(--line);
}

.gex-table td {
    padding:4px 8px;
    border-top:1px solid rgba(255,255,255,.045);
    font-weight:800;
}

.gex-table tr:hover td {
    filter:brightness(1.10);
}

.gex-table td:first-child {
    width:40%;
    text-align:right;
}

.gex-pos-low {
    background:#0b2c18;
    color:#d0dbd3;
}

.gex-pos-mid {
    background:#11502a;
    color:#fff;
}

.gex-pos-high {
    background:#208b43;
    color:#fff;
}

.gex-neg-low {
    background:#26122f;
    color:#ddd1e0;
}

.gex-neg-mid {
    background:#5a1374;
    color:#fff;
}

.gex-neg-high {
    background:#8d18bc;
    color:#fff;
}

.gex-magnet {
    background:linear-gradient(90deg,#f0dc4f,#ffe86b);
    color:#090909;
    box-shadow:inset 0 0 0 1px rgba(0,0,0,.16);
}

.path-card {
    border:1px solid var(--line);
    background:linear-gradient(180deg, rgba(17,22,29,.96), rgba(10,14,19,.96));
    border-radius:13px;
    padding:8px 9px;
    margin-top:7px;
    font-size:10px;
    line-height:1.4;
    box-shadow:0 8px 22px rgba(0,0,0,.14);
}

.path-grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:7px;
}

.path-title {
    font-size:10px;
    font-weight:950;
    margin-bottom:3px;
}

.path-muted {
    color:var(--muted);
}

.summary-panel {
    margin-top:9px;
    background:linear-gradient(180deg, rgba(17,22,29,.96), rgba(9,13,18,.96));
    border:1px solid var(--line);
    border-radius:15px;
    padding:10px;
    box-shadow:0 14px 34px rgba(0,0,0,.20);
}

.summary-grid {
    display:grid;
    grid-template-columns:repeat(6,1fr);
    gap:7px;
}

.summary-item {
    background:#0a0e13;
    border:1px solid var(--line);
    border-radius:11px;
    padding:8px 7px;
    text-align:center;
}

.summary-label {
    color:var(--muted);
    font-size:8px;
    font-weight:850;
    letter-spacing:.09em;
}

.summary-value {
    font-size:12px;
    font-weight:950;
    margin-top:3px;
}

.summary-details {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:7px;
    margin-top:8px;
}

.detail-item {
    background:#0a0e13;
    border:1px solid var(--line);
    border-radius:11px;
    padding:8px 7px;
}

.detail-label {
    color:var(--muted);
    font-size:8px;
    font-weight:850;
    letter-spacing:.07em;
}

.detail-value {
    margin-top:3px;
    font-size:11px;
    font-weight:900;
}

.ai-read {
    margin-top:8px;
    background:rgba(10,14,19,.94);
    border:1px solid var(--line);
    border-radius:11px;
    padding:9px 10px;
}

.ai-read-title {
    font-size:9px;
    font-weight:950;
    letter-spacing:.09em;
    color:#fff;
    margin-bottom:6px;
}

.ai-line {
    font-size:10px;
    line-height:1.5;
    color:#b7c0cc;
    margin:3px 0;
}

.trade-card {
    margin-top:8px;
    background:rgba(10,14,19,.96);
    border:1px solid var(--line);
    border-radius:11px;
    padding:9px 10px;
}

.trade-grid {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:7px;
}

.trade-item {
    background:#090d12;
    border:1px solid var(--line);
    border-radius:11px;
    padding:8px 7px;
    text-align:center;
}

.trade-label {
    color:var(--muted);
    font-size:8px;
    font-weight:850;
    letter-spacing:.07em;
}

.trade-value {
    margin-top:3px;
    font-size:12px;
    font-weight:950;
}

.green { color:var(--green); }
.red { color:var(--red); }
.yellow { color:var(--yellow); }
.purple { color:#d58aff; }

.bottom-dock {
    position:fixed;
    left:50%;
    bottom:14px;
    transform:translateX(-50%);
    z-index:9999;
    display:flex;
    gap:10px;
    align-items:center;
    padding:8px 10px;
    border-radius:18px;
    background:rgba(18,25,20,.78);
    border:1px solid rgba(115,246,167,.22);
    box-shadow:0 14px 40px rgba(0,0,0,.35);
    backdrop-filter:blur(16px);
}

.dock-item {
    min-width:76px;
    text-align:center;
    border-radius:13px;
    padding:7px 10px;
    font-size:9px;
    font-weight:850;
    color:#aeb7c3;
}

.dock-active {
    background:rgba(115,246,167,.14);
    color:var(--green);
    border:1px solid rgba(115,246,167,.20);
}

@media (max-width:900px) {
    [data-testid="stHorizontalBlock"] {
        flex-wrap:wrap;
    }

    [data-testid="column"] {
        min-width:100% !important;
        width:100% !important;
        flex:1 1 100% !important;
    }

    .summary-grid {
        grid-template-columns:repeat(2,1fr);
    }

    .summary-details {
        grid-template-columns:repeat(2,1fr);
    }

    .trade-grid {
        grid-template-columns:repeat(2,1fr);
    }

    .bottom-dock {
        width:calc(100% - 24px);
        justify-content:space-around;
    }

    .dock-item {
        min-width:auto;
        flex:1;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------- TOP BAR ----------------

st.markdown(
    "<div class='topbar'>"
    "<div style='display:flex;justify-content:space-between;align-items:center'>"
    "<div><span style='color:#f5dd4f'>7C</span> &nbsp; TRINITY</div>"
    "<div style='color:#73f6a7'>● LIVE</div>"
    "</div>"
    "</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='toolbar'>"
    "<span class='pill'>☰ 77</span>"
    "<span class='pill'>▣ 3</span>"
    "<span class='pill pill-purple'>⚡ GEX</span>"
    "<span class='pill pill-yellow'>15m</span>"
    "<span class='pill'>◎</span>"
    "<span class='pill'>♛</span>"
    "<span class='pill pill-green'>↶</span>"
    "<span class='pill'>↻</span>"
    "</div>",
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
px = None
magnet_px = None
danger_px = None

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

positive_total = 0.0
negative_total = 0.0

for _, gex in selected_rows:
    try:
        value = clean_gex_value(gex)
        if value >= 0:
            positive_total += value
        else:
            negative_total += abs(value)
    except Exception:
        continue

if positive_total > negative_total * 1.35:
    gamma_regime = "STABLE"
    regime_class = "green"
elif negative_total > positive_total * 1.35:
    gamma_regime = "EXPANSIVE"
    regime_class = "purple"
else:
    gamma_regime = "MIXED"
    regime_class = "yellow"

location_text = "N/A"
magnet_distance = "N/A"
accelerator_distance = "N/A"
nearest_trigger = "N/A"
room_text = "N/A"

try:
    magnet_distance_val = round(abs(px - magnet_px), 2)
    accelerator_distance_val = round(abs(px - danger_px), 2)
    magnet_distance = str(magnet_distance_val)
    accelerator_distance = str(accelerator_distance_val)

    if px > magnet_px:
        location_text = "ABOVE ★"
    elif px < danger_px:
        location_text = "BELOW ⚡"
    else:
        location_text = "BETWEEN"

    trigger_candidates = []
    if upside_targets:
        trigger_candidates.append(("▲", float(upside_targets[0])))
    if downside_targets:
        trigger_candidates.append(("▼", float(downside_targets[0])))

    if trigger_candidates:
        mark, level = min(trigger_candidates, key=lambda item: abs(px - item[1]))
        nearest_trigger = f"{mark} {level}"
        room_text = str(round(abs(px - level), 2))
except Exception:
    pass

dp_primary = primary_magnet
dp_secondary = danger_level

bull_entry = upside_targets[0] if upside_targets else primary_magnet
bear_entry = downside_targets[0] if downside_targets else danger_level
bull_target = upside_targets[-1] if upside_targets else primary_magnet
bear_target = downside_targets[-1] if downside_targets else danger_level

if flow_short == "CALLS" and score >= 65:
    best_side = "CALLS"
    entry_level = bull_entry
    invalidation_level = bear_entry
    target_level = bull_target
    trade_class = "green"
elif flow_short == "PUTS" and score >= 65:
    best_side = "PUTS"
    entry_level = bear_entry
    invalidation_level = bull_entry
    target_level = bear_target
    trade_class = "red"
else:
    best_side = "WAIT"
    entry_level = f"{bear_entry} / {bull_entry}"
    invalidation_level = "N/A"
    target_level = "CONFIRM"
    trade_class = "yellow"

ai_lines = []

if flow_short == "CALLS":
    ai_lines.append(f"• Call flow is leading, giving buyers the cleaner edge.")
elif flow_short == "PUTS":
    ai_lines.append(f"• Put flow is leading, giving sellers the cleaner edge.")
else:
    ai_lines.append(f"• Flow is mixed, so confirmation matters more than prediction.")

ai_lines.append(f"• Gamma regime is {gamma_regime.lower()}, which implies "
                f"{'slower rotation' if gamma_regime == 'STABLE' else 'faster expansion' if gamma_regime == 'EXPANSIVE' else 'two-way trade'}.")

ai_lines.append(f"• Price is {location_text.lower()}, {magnet_distance} from the magnet and "
                f"{accelerator_distance} from the accelerator.")

ai_lines.append(f"• Above {bull_entry} opens the upside path toward {upside_text}.")
ai_lines.append(f"• Below {bear_entry} opens the downside path toward {downside_text}.")
ai_lines.append(f"• DP proxy zones remain {dp_primary} and {dp_secondary} until real dark-pool data is connected.")

ai_html = "".join(f"<div class='ai-line'>{line}</div>" for line in ai_lines)

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

    f"<div class='summary-details'>"
    f"<div class='detail-item'><div class='detail-label'>REGIME</div>"
    f"<div class='detail-value {regime_class}'>{gamma_regime}</div></div>"
    f"<div class='detail-item'><div class='detail-label'>LOCATION</div>"
    f"<div class='detail-value'>{location_text}</div></div>"
    f"<div class='detail-item'><div class='detail-label'>NEAREST</div>"
    f"<div class='detail-value'>{nearest_trigger}</div></div>"
    f"<div class='detail-item'><div class='detail-label'>ROOM</div>"
    f"<div class='detail-value'>{room_text}</div></div>"
    f"<div class='detail-item'><div class='detail-label'>DIST ★</div>"
    f"<div class='detail-value yellow'>{magnet_distance}</div></div>"
    f"<div class='detail-item'><div class='detail-label'>DIST ⚡</div>"
    f"<div class='detail-value purple'>{accelerator_distance}</div></div>"
    f"<div class='detail-item'><div class='detail-label'>DP PROXY 1</div>"
    f"<div class='detail-value purple'>{dp_primary}</div></div>"
    f"<div class='detail-item'><div class='detail-label'>DP PROXY 2</div>"
    f"<div class='detail-value purple'>{dp_secondary}</div></div>"
    f"</div>"

    f"<div class='ai-read'>"
    f"<div class='ai-read-title'>7C TRADE READ</div>"
    f"{ai_html}"
    f"</div>"

    f"<div class='trade-card'>"
    f"<div class='trade-grid'>"
    f"<div class='trade-item'><div class='trade-label'>BEST</div>"
    f"<div class='trade-value {trade_class}'>{best_side}</div></div>"
    f"<div class='trade-item'><div class='trade-label'>ENTRY</div>"
    f"<div class='trade-value'>{entry_level}</div></div>"
    f"<div class='trade-item'><div class='trade-label'>INVALID</div>"
    f"<div class='trade-value'>{invalidation_level}</div></div>"
    f"<div class='trade-item'><div class='trade-label'>TARGET</div>"
    f"<div class='trade-value'>{target_level}</div></div>"
    f"</div>"
    f"</div>"
    f"</div>"
)

st.markdown(summary_html, unsafe_allow_html=True)


st.markdown(
    "<div class='bottom-dock'>"
    "<div class='dock-item dock-active'>▰<br>Heatmaps</div>"
    "<div class='dock-item'>⌁<br>Read</div>"
    "<div class='dock-item'>♢<br>Alerts</div>"
    "<div class='dock-item'>♛<br>Trinity</div>"
    "</div>",
    unsafe_allow_html=True
)
