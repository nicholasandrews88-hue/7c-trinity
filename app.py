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
.stApp { background-color:#050607; color:white; }
.block-container { padding-top:0.45rem; padding-bottom:1rem; max-width:1900px; }

.topbar {
    background:#0b0e14;
    border:1px solid #252b38;
    border-radius:14px;
    padding:8px 12px;
    margin-bottom:7px;
    font-weight:800;
    font-size:12px;
}

.panel-title { font-size:17px; line-height:1.1; font-weight:900; margin-bottom:2px; }
.price-red { color:#ff5c68; font-size:14px; font-weight:900; }
.price-green { color:#55ff99; font-size:14px; font-weight:900; }
.live { color:#55ff99; font-size:11px; font-weight:900; }

.green-box {
    background:linear-gradient(90deg,#062b16,#06361d);
    border:1px solid #00ff66;
    color:#55ff99;
    padding:10px 12px;
    border-radius:10px;
    font-size:13px;
    font-weight:800;
}

.red-box {
    background:linear-gradient(90deg,#3a0505,#160000);
    border:1px solid #ff4d4d;
    color:#ff6b6b;
    padding:10px 12px;
    border-radius:10px;
    font-size:13px;
    font-weight:800;
}

.yellow-box {
    background:linear-gradient(90deg,#302800,#181300);
    border:1px solid #ffde59;
    color:#ffde59;
    padding:10px 12px;
    border-radius:10px;
    font-size:13px;
    font-weight:800;
}

[data-testid="stMetricLabel"] { font-size:10px; }
[data-testid="stMetricValue"] { font-size:19px; }
[data-testid="stMetricDelta"] { font-size:9px; }
[data-testid="stTextInput"] label { font-size:11px; }
[data-testid="stTextInput"] input { font-size:12px; min-height:38px; }
[data-testid="column"] { gap:0.35rem; }
hr { margin:0.7rem 0 !important; }

.gex-wrap {
    border:1px solid #232938;
    border-radius:10px;
    overflow:hidden;
    margin-top:7px;
    background:#0a0d12;
}
.gex-table { width:100%; border-collapse:collapse; table-layout:fixed; font-size:10px; }
.gex-table th { background:#171b24; color:#aeb5c2; text-align:left; padding:6px 8px; font-size:9px; letter-spacing:.03em; }
.gex-table td { padding:4px 8px; border-top:1px solid rgba(255,255,255,.07); font-weight:750; }
.gex-table td:first-child { width:42%; text-align:right; }
.gex-pos-low { background:#082515; color:#b8c0bb; }
.gex-pos-mid { background:#0d5426; color:#fff; }
.gex-pos-high { background:#188d3a; color:#fff; }
.gex-neg-low { background:#23102d; color:#d4c8d8; }
.gex-neg-mid { background:#55116f; color:#fff; }
.gex-neg-high { background:#8a14b8; color:#fff; }
.gex-magnet { background:#f1d84b; color:#090909; }
.path-card { border:1px solid #242a36; background:#0b0f15; border-radius:9px; padding:8px 9px; margin-top:7px; font-size:10px; line-height:1.35; }
.path-title { font-size:10px; font-weight:900; margin-bottom:3px; }
.path-grid { display:grid; grid-template-columns:1fr 1fr; gap:6px; }
.path-muted { color:#98a1af; }
@media (max-width: 900px) {
  [data-testid="stHorizontalBlock"] { flex-wrap:wrap; }
  [data-testid="column"] { min-width:100% !important; width:100% !important; flex:1 1 100% !important; }
  .gex-table { font-size:11px; }
}
</style>
""", unsafe_allow_html=True)

# ---------------- TOP BAR ----------------

st.markdown(
    "<div class='topbar'>⚡ 7C TRINITY | LIVE GEX + FLOW | AUTO REFRESH: 15s</div>",
    unsafe_allow_html=True
)

top1, top2, top3, top4 = st.columns([1, 1, 1, 2])

with top1:
    st.metric("Market Mode", "Live", "GEX + Flow")

with top2:
    st.metric("7C Edge", "Dynamic", "Building")

with top3:
    st.metric("Best Side", "Live", "Flow Driven")

with top4:
    ticker_input = st.text_input(
        "Search Tickers",
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
            <div><div class='path-title' style='color:#55ff99'>Bullish</div>
              <div><span class='path-muted'>Hold:</span> {bull_trigger}</div>
              <div><span class='path-muted'>Targets:</span> {upside_text}</div>
            </div>
            <div><div class='path-title' style='color:#ff6673'>Bearish</div>
              <div><span class='path-muted'>Lose:</span> {bear_trigger}</div>
              <div><span class='path-muted'>Targets:</span> {downside_text}</div>
            </div>
          </div>
          <div style='margin-top:6px'><span class='path-muted'>Accelerator:</span> {largest_negative[0]} &nbsp; | &nbsp;
          <span class='path-muted'>Magnet:</span> {largest_positive[0]}</div>
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



# ---------------- 7C ROADMAP READOUT ----------------

st.markdown("---")
st.subheader(f"7C Roadmap — {search_ticker}")

risk_ceiling = upside_targets[-1] if upside_targets else primary_magnet
support_alert = downside_targets[0] if downside_targets else danger_level

nearest_upside = upside_targets[0] if upside_targets else primary_magnet

if flow_bias == "CALL FLOW DOMINANT":

    roadmap_class = "green-box"
    roadmap_title = "Ceiling Cascade"

    market_role = "Growth-risk monitor"

    trigger = (
        f"Above {nearest_upside} keeps upside pressure active. "
        f"Above {risk_ceiling} confirms continuation."
    )

    invalidation = (
        f"Loss of {support_alert} increases downside risk."
    )

    timeline = (
        f"Near-term caution below {support_alert}. "
        f"Stronger warning below {danger_level}."
    )

    interpretation = (
        f"{search_ticker} remains constructive while holding "
        f"above the nearest positive GEX support zone. "
        f"If support fails, downside risk opens toward "
        f"{downside_text}."
    )

elif flow_bias == "PUT FLOW DOMINANT":

    roadmap_class = "red-box"
    roadmap_title = "Hedge Launchpad"

    market_role = "Downside-risk monitor"

    trigger = (
        f"Below {support_alert} keeps puts favored. "
        f"Negative GEX zones can accelerate downside."
    )

    invalidation = (
        f"Reclaiming {primary_magnet} weakens bearish pressure."
    )

    timeline = (
        f"Immediate caution while below key dealer levels."
    )

    interpretation = (
        f"{search_ticker} remains vulnerable while trading "
        f"below major dealer positioning levels. "
        f"Watch downside path toward {downside_text}."
    )

else:

    roadmap_class = "yellow-box"
    roadmap_title = "Decision Zone"

    market_role = "Neutral / Chop monitor"

    trigger = (
        f"Above {primary_magnet} favors upside. "
        f"Below {support_alert} favors downside."
    )

    invalidation = (
        "No clean invalidation yet due to mixed flow."
    )

    timeline = (
        "Wait for confirmation before forcing trades."
    )

    interpretation = (
        f"{search_ticker} currently has mixed flow and no clean edge. "
        f"Wait for confirmation above {upside_text} "
        f"or below {downside_text}."
    )

st.markdown(f"""
<div class='{roadmap_class}'>

<h3 style='margin-top:0;'>
{search_ticker} — {roadmap_title}
</h3>

<b>Current Price:</b> {selected_price}<br>

<b>Market Role:</b> {market_role}<br>

<b>Risk Ceiling:</b> {risk_ceiling}<br>

<b>Strongest Positive GEX:</b> {primary_magnet}<br>

<b>Strongest Negative GEX:</b> {danger_level}<br>

<b>Nearest Positive Support:</b> {nearest_upside}<br>

<b>Negative Gamma Zones:</b> {neg_list}<br>

<b>Upside Ladder:</b> {upside_text}<br>

<b>Downside Ladder:</b> {downside_text}<br>

<b>Trigger:</b> {trigger}<br>

<b>Invalidation:</b> {invalidation}<br>

<b>Timeline:</b> {timeline}<br><br>

<b>7C Interpretation:</b> {interpretation}

</div>
""", unsafe_allow_html=True)


# ---------------- 7C PREMIUM + SWING READOUT ----------------

st.markdown("---")
st.subheader(f"7C Premium + Swing Readout — {search_ticker}")

if flow_bias == "CALL FLOW DOMINANT":

    premium_class = "green-box"
    options_money = "CALLS LEADING"
    swing_grade = "OK TO SWING BULLISH — IF LEVELS HOLD"
    why = (
        f"Call flow is stronger than put flow, meaning buyers are leaning bullish. "
        f"As long as {search_ticker} holds above {support_alert}, the bullish swing idea is valid."
    )
    gameplan = (
        f"Look for continuation above {nearest_upside}. "
        f"Upside path is {upside_text}. "
        f"If price loses {support_alert}, stop treating it as a clean bullish swing."
    )

elif flow_bias == "PUT FLOW DOMINANT":

    premium_class = "red-box"
    options_money = "PUTS LEADING"
    swing_grade = "CAUTION / BEARISH SWING FAVORED"
    why = (
        f"Put flow is stronger than call flow, meaning traders are leaning defensive or bearish. "
        f"As long as {search_ticker} stays below {primary_magnet}, long swings are higher risk."
    )
    gameplan = (
        f"Downside path is {downside_text}. "
        f"If price reclaims {primary_magnet}, bearish pressure can weaken fast."
    )

else:

    premium_class = "yellow-box"
    options_money = "MIXED FLOW"
    swing_grade = "NO CLEAN SWING EDGE"
    why = (
        "Calls and puts are not clearly aligned. "
        "This usually means chop risk is higher."
    )
    gameplan = (
        f"Wait for price to confirm above {upside_text} or below {downside_text}."
    )

st.markdown(f"""
<div class='{premium_class}'>

<h3 style='margin-top:0;'>
{search_ticker} — Options Money / Swing Decision
</h3>

<b>Options Money:</b> {options_money}<br>
<b>Swing Grade:</b> {swing_grade}<br><br>

<b>Why:</b> {why}<br><br>

<b>Game Plan:</b> {gameplan}<br><br>

<b>7C Rule:</b> Swing only when options money, GEX levels, and price structure agree.

</div>
""", unsafe_allow_html=True)


# ---------------- 7C DARK POOL READOUT ----------------

st.markdown("---")
st.subheader(f"7C Dark Pool Readout — {search_ticker}")

# PLACEHOLDER LEVELS
# later we can connect real DP API

largest_dp = primary_magnet
secondary_dp = support_alert

distance_main = round(selected_price - float(largest_dp), 2)
distance_secondary = round(selected_price - float(secondary_dp), 2)

if flow_bias == "CALL FLOW DOMINANT":

    dp_class = "green-box"
    dp_bias = "BULLISH ACCEPTANCE"

    dp_interpretation = (
        f"Price holding above the primary dark pool zone suggests institutions "
        f"are accepting higher prices."
    )

    dp_gameplan = (
        f"Above {largest_dp} keeps upside continuation active. "
        f"If price loses {secondary_dp}, downside pressure can accelerate."
    )

elif flow_bias == "PUT FLOW DOMINANT":

    dp_class = "red-box"
    dp_bias = "BEARISH PRESSURE"

    dp_interpretation = (
        f"Price trading below major dark pool positioning suggests "
        f"institutional sellers remain active."
    )

    dp_gameplan = (
        f"Below {secondary_dp} keeps downside pressure active. "
        f"Reclaiming {largest_dp} weakens bearish control."
    )

else:

    dp_class = "yellow-box"
    dp_bias = "NEUTRAL / BALANCED"

    dp_interpretation = (
        f"Dark pool positioning is currently balanced with no dominant edge."
    )

    dp_gameplan = (
        f"Wait for acceptance above {largest_dp} or rejection below {secondary_dp}."
    )

st.markdown(f"""
<div class='{dp_class}'>

<h3 style='margin-top:0;'>
{search_ticker} — Institutional Dark Pool Map
</h3>

<b>Largest Dark Pool Level:</b> {largest_dp}<br>

<b>Secondary Dark Pool Level:</b> {secondary_dp}<br>

<b>Distance From Main DP:</b> {distance_main}<br>

<b>Distance From Secondary DP:</b> {distance_secondary}<br><br>

<b>Dark Pool Bias:</b> {dp_bias}<br><br>

<b>Interpretation:</b> {dp_interpretation}<br><br>

<b>Game Plan:</b> {dp_gameplan}<br><br>

<b>7C Insight:</b> GEX + Dark Pool alignment creates the strongest trade locations. 
When dealer positioning and institutional positioning align, moves tend to be cleaner and stronger.

</div>
""", unsafe_allow_html=True)



