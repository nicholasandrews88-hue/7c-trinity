import streamlit as st
import pandas as pd
import requests
import os
import json
import html
import base64
from pathlib import Path
from datetime import datetime, timedelta, timezone
from streamlit_autorefresh import st_autorefresh
from auth import account_bar, require_active_subscription

st.set_page_config(page_title="7C Trinity", page_icon="7c_logo.jpg", layout="wide")

profile = require_active_subscription()
account_bar(profile)

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


def logo_data_uri():
    logo_path = Path(__file__).with_name("7c_logo.jpg")
    if not logo_path.exists():
        return ""
    encoded = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


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
    --bg:#07050c;
    --panel:#100c18;
    --panel-2:#171021;
    --line:rgba(244,197,66,.13);
    --muted:#9b94aa;
    --text:#f4f6f8;
    --green:#73f6a7;
    --red:#ff6673;
    --yellow:#f4c542;
    --purple:#8b3dff;
}

.stApp {
    background:
        radial-gradient(circle at 13% -6%, rgba(139,61,255,.16), transparent 30%),
        radial-gradient(circle at 92% 0%, rgba(244,197,66,.08), transparent 24%),
        linear-gradient(180deg,#08060d,#050408 72%);
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


.brand-header {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:14px;
    padding:11px 14px;
    margin-bottom:9px;
    border:1px solid rgba(244,197,66,.16);
    border-radius:16px;
    background:
        linear-gradient(110deg,rgba(28,18,42,.96),rgba(10,8,14,.97));
    box-shadow:0 16px 42px rgba(0,0,0,.24);
}

.brand-left {
    display:flex;
    align-items:center;
    gap:11px;
}

.brand-logo {
    width:48px;
    height:48px;
    border-radius:12px;
    object-fit:cover;
    border:1px solid rgba(244,197,66,.27);
    box-shadow:0 0 22px rgba(139,61,255,.18);
}

.brand-kicker {
    color:var(--yellow);
    font-size:8px;
    font-weight:950;
    letter-spacing:.15em;
}

.brand-title {
    margin-top:1px;
    font-size:16px;
    font-weight:950;
    letter-spacing:.08em;
    color:#fff;
}

.brand-subtitle {
    color:var(--muted);
    font-size:8px;
    letter-spacing:.09em;
    margin-top:1px;
}

.brand-live {
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:6px 9px;
    border-radius:999px;
    background:rgba(34,197,94,.10);
    border:1px solid rgba(34,197,94,.22);
    color:#73f6a7;
    font-size:9px;
    font-weight:950;
}

.compact-card,
.summary-panel,
.path-card,
.status-item,
.detail-item,
.summary-item,
.execution-panel,
.market-read {
    box-shadow:
        0 10px 28px rgba(0,0,0,.17),
        inset 0 1px 0 rgba(255,255,255,.025);
}

.compact-card:hover,
.summary-item:hover,
.detail-item:hover,
.status-item:hover {
    border-color:rgba(244,197,66,.32);
    transform:translateY(-1px);
    transition:.18s ease;
}

.gex-wrap {
    border-color:rgba(139,61,255,.20);
}

.gex-magnet {
    background:linear-gradient(90deg,#e7bd2e,#ffe47a);
}

.edge-banner {
    border-color:rgba(244,197,66,.20);
    background:linear-gradient(90deg,rgba(139,61,255,.12),rgba(244,197,66,.07));
}

.execution-panel {
    border-color:rgba(139,61,255,.25);
}



.intelligence-flow-grid {
    display:grid;
    grid-template-columns:minmax(0,1.35fr) minmax(320px,.65fr);
    gap:8px;
    margin-top:8px;
}

.aggressive-flow {
    background:
        radial-gradient(circle at 100% 0%, rgba(139,61,255,.13), transparent 42%),
        #090d12;
    border:1px solid rgba(244,197,66,.16);
    border-radius:11px;
    padding:10px;
}

.aggressive-title {
    color:#fff;
    font-size:9px;
    font-weight:950;
    letter-spacing:.10em;
}

.aggressive-subtitle {
    color:var(--muted);
    font-size:8px;
    margin-top:2px;
    margin-bottom:7px;
}

.flow-contract-grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:7px;
}

.flow-contract {
    background:rgba(8,10,15,.92);
    border:1px solid var(--line);
    border-radius:10px;
    padding:8px;
}

.flow-contract.call {
    border-color:rgba(115,246,167,.21);
}

.flow-contract.put {
    border-color:rgba(255,102,115,.21);
}

.flow-side {
    font-size:8px;
    font-weight:950;
    letter-spacing:.09em;
}

.flow-symbol {
    margin-top:4px;
    color:#fff;
    font-size:12px;
    font-weight:950;
}

.flow-meta {
    margin-top:3px;
    color:#aeb6c3;
    font-size:8px;
    line-height:1.45;
}

.flow-premium {
    margin-top:5px;
    font-size:12px;
    font-weight:950;
    color:var(--yellow);
}

.flow-strength {
    margin-top:3px;
    font-size:8px;
    color:var(--muted);
}

.flow-dominant {
    margin-top:7px;
    padding:7px 8px;
    border-radius:9px;
    background:rgba(139,61,255,.09);
    border:1px solid rgba(139,61,255,.18);
    color:#d9c7ee;
    font-size:8px;
    line-height:1.4;
}

@media (max-width:900px) {
    .intelligence-flow-grid {
        grid-template-columns:1fr;
    }
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

.edge-banner {
    margin-top:8px;
    background:linear-gradient(90deg, rgba(115,246,167,.08), rgba(184,76,255,.06));
    border:1px solid var(--line);
    border-radius:11px;
    padding:9px 10px;
}

.edge-label {
    color:var(--muted);
    font-size:8px;
    font-weight:850;
    letter-spacing:.09em;
}

.edge-text {
    margin-top:3px;
    font-size:12px;
    font-weight:950;
    color:#f4f6f8;
}

.subtext {
    margin-top:2px;
    color:var(--muted);
    font-size:8px;
    font-weight:750;
}

.conf-level {
    display:block;
    margin-top:2px;
    font-size:8px;
    color:var(--muted);
    font-weight:800;
}

.zone-support { color:var(--green); }
.zone-resistance { color:var(--red); }


.status-bar {
    display:grid;
    grid-template-columns:repeat(5,1fr);
    gap:7px;
    margin:8px 0 10px;
}

.status-item {
    background:rgba(10,14,19,.92);
    border:1px solid var(--line);
    border-radius:11px;
    padding:7px 9px;
    text-align:center;
}

.status-label {
    color:var(--muted);
    font-size:8px;
    font-weight:850;
    letter-spacing:.08em;
}

.status-value {
    margin-top:2px;
    font-size:11px;
    font-weight:950;
}

.live-pulse {
    display:inline-block;
    width:7px;
    height:7px;
    border-radius:50%;
    background:var(--green);
    box-shadow:0 0 0 0 rgba(115,246,167,.7);
    animation:pulseLive 1.8s infinite;
    margin-right:5px;
}

@keyframes pulseLive {
    0% { box-shadow:0 0 0 0 rgba(115,246,167,.55); }
    70% { box-shadow:0 0 0 8px rgba(115,246,167,0); }
    100% { box-shadow:0 0 0 0 rgba(115,246,167,0); }
}

.gex-magnet td {
    animation:magnetGlow 2.2s ease-in-out infinite;
}

@keyframes magnetGlow {
    0%,100% { filter:brightness(1); }
    50% { filter:brightness(1.14); }
}

.ticker-meta {
    display:flex;
    gap:6px;
    flex-wrap:wrap;
    margin-top:4px;
}

.badge {
    display:inline-flex;
    align-items:center;
    padding:3px 6px;
    border-radius:999px;
    font-size:8px;
    font-weight:900;
    border:1px solid var(--line);
    background:#0a0e13;
}

.badge-green {
    color:var(--green);
    border-color:rgba(115,246,167,.22);
    background:rgba(24,92,49,.20);
}

.badge-red {
    color:var(--red);
    border-color:rgba(255,102,115,.22);
    background:rgba(110,25,33,.20);
}

.badge-yellow {
    color:var(--yellow);
    border-color:rgba(245,221,79,.22);
    background:rgba(101,87,14,.20);
}

.execution-panel {
    margin-top:8px;
    background:linear-gradient(180deg, rgba(14,19,26,.98), rgba(8,12,17,.98));
    border:1px solid rgba(115,246,167,.15);
    border-radius:13px;
    padding:10px;
    box-shadow:0 12px 28px rgba(0,0,0,.18);
}

.execution-title {
    font-size:9px;
    font-weight:950;
    letter-spacing:.1em;
    color:#fff;
    margin-bottom:7px;
}

.execution-grid {
    display:grid;
    grid-template-columns:repeat(6,1fr);
    gap:7px;
}

.execution-item {
    background:#090d12;
    border:1px solid var(--line);
    border-radius:10px;
    padding:8px 7px;
    text-align:center;
}

.execution-label {
    color:var(--muted);
    font-size:8px;
    font-weight:850;
    letter-spacing:.07em;
}

.execution-value {
    margin-top:3px;
    font-size:11px;
    font-weight:950;
}

.market-read {
    margin-top:8px;
    background:#090d12;
    border:1px solid var(--line);
    border-radius:11px;
    padding:10px;
}

.market-read-title {
    color:#fff;
    font-size:9px;
    font-weight:950;
    letter-spacing:.1em;
    margin-bottom:6px;
}

.market-read-main {
    font-size:12px;
    font-weight:950;
    margin-bottom:6px;
}

.market-read-line {
    color:#b8c1cd;
    font-size:10px;
    line-height:1.5;
    margin:2px 0;
}

@media (max-width:900px) {
    .status-bar { grid-template-columns:repeat(2,1fr); }
    .execution-grid { grid-template-columns:repeat(2,1fr); }
}


/* =========================
   7C MOBILE OPTIMIZATION
   ========================= */

@media (max-width: 768px) {
    .block-container {
        padding-top: .35rem !important;
        padding-left: .55rem !important;
        padding-right: .55rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }

    /* Remove Streamlit desktop chrome spacing */
    [data-testid="stAppViewContainer"] > .main {
        overflow-x: hidden;
    }

    [data-testid="stHorizontalBlock"] {
        gap: .45rem !important;
        flex-wrap: wrap !important;
    }

    [data-testid="column"] {
        min-width: 100% !important;
        width: 100% !important;
        flex: 1 1 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* Branded header */
    .brand-header {
        padding: 9px 10px !important;
        border-radius: 13px !important;
        margin-bottom: 7px !important;
        align-items: center !important;
    }

    .brand-left {
        gap: 8px !important;
        min-width: 0;
    }

    .brand-logo {
        width: 38px !important;
        height: 38px !important;
        border-radius: 10px !important;
        flex: 0 0 38px;
    }

    .brand-kicker {
        font-size: 7px !important;
    }

    .brand-title {
        font-size: 13px !important;
        letter-spacing: .05em !important;
        white-space: nowrap;
    }

    .brand-subtitle {
        font-size: 6px !important;
        letter-spacing: .06em !important;
        white-space: nowrap;
    }

    .brand-live {
        font-size: 7px !important;
        padding: 5px 7px !important;
        white-space: nowrap;
    }

    /* Search / ticker controls */
    [data-testid="stTextInput"] input {
        min-height: 40px !important;
        height: 40px !important;
        font-size: 13px !important;
        border-radius: 11px !important;
    }

    [data-testid="stButton"] button {
        min-height: 40px !important;
        border-radius: 11px !important;
    }

    /* Watchlist ticker buttons: 2 per row */
    .status-bar {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 6px !important;
        margin: 7px 0 !important;
    }

    .status-item {
        padding: 7px 6px !important;
    }

    .status-label {
        font-size: 7px !important;
    }

    .status-value {
        font-size: 10px !important;
    }

    /* Heatmaps */
    .panel-title {
        font-size: 16px !important;
    }

    .price-green,
    .price-red {
        font-size: 14px !important;
    }

    .ticker-meta {
        margin-bottom: 4px;
    }

    .gex-wrap {
        max-height: 575px !important;
        border-radius: 12px !important;
        margin-top: 5px !important;
        overflow-x: hidden !important;
    }

    .gex-table {
        font-size: 10px !important;
        width: 100% !important;
    }

    .gex-table th {
        padding: 7px 7px !important;
        font-size: 8px !important;
    }

    .gex-table td {
        padding: 5px 7px !important;
        font-size: 10px !important;
    }

    .gex-table td:first-child {
        width: 39% !important;
    }

    /* Bullish / bearish path cards */
    .path-card {
        padding: 8px !important;
        border-radius: 11px !important;
        margin-top: 6px !important;
    }

    .path-grid {
        grid-template-columns: 1fr !important;
        gap: 8px !important;
    }

    .path-title {
        font-size: 10px !important;
    }

    /* Summary */
    .summary-panel {
        padding: 8px !important;
        border-radius: 13px !important;
        margin-top: 7px !important;
    }

    .edge-banner {
        padding: 8px 9px !important;
        border-radius: 10px !important;
        margin-top: 0 !important;
    }

    .edge-label {
        font-size: 7px !important;
    }

    .edge-text {
        font-size: 11px !important;
        line-height: 1.35 !important;
    }

    .summary-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 6px !important;
        margin-top: 7px;
    }

    .summary-item {
        padding: 8px 6px !important;
        min-height: 58px;
        border-radius: 10px !important;
    }

    .summary-label {
        font-size: 7px !important;
    }

    .summary-value {
        font-size: 12px !important;
    }

    .summary-details {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 6px !important;
        margin-top: 7px !important;
    }

    .detail-item {
        padding: 8px 7px !important;
        min-height: 54px;
        border-radius: 10px !important;
    }

    .detail-label {
        font-size: 7px !important;
    }

    .detail-value {
        font-size: 11px !important;
    }

    /* Market intelligence + flow stack */
    .intelligence-flow-grid {
        grid-template-columns: 1fr !important;
        gap: 7px !important;
        margin-top: 7px !important;
    }

    .market-read,
    .aggressive-flow {
        padding: 9px !important;
        border-radius: 11px !important;
    }

    .market-read-title,
    .aggressive-title {
        font-size: 8px !important;
        letter-spacing: .08em !important;
    }

    .market-read-main {
        font-size: 11px !important;
    }

    .market-read-line {
        font-size: 9px !important;
        line-height: 1.45 !important;
    }

    .aggressive-subtitle {
        font-size: 7px !important;
    }

    .flow-contract-grid {
        grid-template-columns: 1fr !important;
        gap: 7px !important;
    }

    .flow-contract {
        padding: 9px !important;
        border-radius: 10px !important;
    }

    .flow-symbol {
        font-size: 13px !important;
    }

    .flow-meta,
    .flow-strength,
    .flow-dominant {
        font-size: 8px !important;
    }

    .flow-premium {
        font-size: 14px !important;
    }

    /* Execution plan */
    .execution-panel {
        padding: 9px !important;
        border-radius: 11px !important;
        margin-top: 7px !important;
    }

    .execution-title {
        font-size: 8px !important;
    }

    .execution-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 6px !important;
    }

    .execution-item {
        padding: 8px 6px !important;
        min-height: 57px;
        border-radius: 10px !important;
    }

    .execution-label {
        font-size: 7px !important;
    }

    .execution-value {
        font-size: 11px !important;
    }

    /* Authenticated account bar */
    .account-chip {
        width: 100%;
        justify-content: center;
        text-align: center;
        font-size: 7px !important;
        padding: 6px 8px !important;
    }

    /* Reduce title/header whitespace */
    h1, h2, h3 {
        margin-top: .35rem !important;
        margin-bottom: .35rem !important;
    }

    hr {
        margin: .45rem 0 !important;
    }
}

/* Very small phones */
@media (max-width: 420px) {
    .brand-subtitle {
        display: none;
    }

    .brand-live {
        font-size: 0 !important;
        padding: 6px !important;
    }

    .brand-live .live-pulse {
        margin-right: 0 !important;
    }

    .summary-grid,
    .summary-details,
    .execution-grid,
    .status-bar {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }

    .gex-table {
        font-size: 9px !important;
    }

    .gex-table td,
    .gex-table th {
        padding-left: 6px !important;
        padding-right: 6px !important;
    }
}

</style>
""", unsafe_allow_html=True)

# ---------------- BRANDED HEADER ----------------

_logo_uri = logo_data_uri()
_logo_html = (
    f"<img class='brand-logo' src='{_logo_uri}' alt='7th Capital logo'>"
    if _logo_uri else ""
)

st.markdown(
    f"<div class='brand-header'>"
    f"<div class='brand-left'>{_logo_html}"
    f"<div><div class='brand-kicker'>7TH CAPITAL</div>"
    f"<div class='brand-title'>TRINITY TERMINAL</div>"
    f"<div class='brand-subtitle'>INSTITUTIONAL OPTIONS INTELLIGENCE</div></div></div>"
    f"<div class='brand-live'><span class='live-pulse'></span>MARKET DATA LIVE</div>"
    f"</div>",
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


st.markdown(
    "<div class='status-bar'>"
    "<div class='status-item'><div class='status-label'>STATUS</div>"
    "<div class='status-value green'><span class='live-pulse'></span>LIVE</div></div>"
    "<div class='status-item'><div class='status-label'>REFRESH</div>"
    "<div class='status-value'>15 SEC</div></div>"
    "<div class='status-item'><div class='status-label'>MODE</div>"
    "<div class='status-value'>GEX + FLOW</div></div>"
    "<div class='status-item'><div class='status-label'>WATCHLIST</div>"
    f"<div class='status-value'>{len(symbols)} NAMES</div></div>"
    "<div class='status-item'><div class='status-label'>SELECTED</div>"
    f"<div class='status-value yellow'>{search_ticker}</div></div>"
    "</div>",
    unsafe_allow_html=True
)

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


def format_flow_premium(value):
    try:
        value = float(value or 0)
    except (TypeError, ValueError):
        return "$0"

    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def aggressive_flow_score(row):
    """Rank short-dated trades by premium plus aggressive-flow characteristics."""
    premium = float(row.get("premium") or 0)
    multiplier = 1.0

    if row.get("tradeSideCode") == "ABOVE_ASK":
        multiplier *= 1.25

    consolidation = str(row.get("tradeConsolidationType") or "").upper()
    if consolidation == "SWEEP":
        multiplier *= 1.18
    elif consolidation == "BLOCK":
        multiplier *= 1.08

    if row.get("isGoldenSweep"):
        multiplier *= 1.20
    if row.get("isUnusual"):
        multiplier *= 1.10
    if row.get("isOpeningPosition"):
        multiplier *= 1.10
    if row.get("isVolumeGreaterThanOpenInterest"):
        multiplier *= 1.08

    return premium * multiplier


@st.cache_data(ttl=60, show_spinner=False)
def get_strongest_aggressive_flow(symbol, contract_type):
    """
    Pull the strongest aggressive consolidated trade from the last 14 days,
    restricted to contracts with 0–14 DTE.
    """
    now_utc = datetime.now(timezone.utc)
    start_utc = now_utc - timedelta(days=14)

    payload = {
        "timeRange": {
            "startTime": start_utc.isoformat().replace("+00:00", "Z"),
            "endTime": now_utc.isoformat().replace("+00:00", "Z"),
        },
        "filter": {
            "ticker": symbol,
            "contractType": contract_type,
        },
        "size": 100,
        "sort": {
            "field": "premium",
            "direction": "DESCENDING",
        },
        "includes": [
            "ticker",
            "contractType",
            "expirationDate",
            "dte",
            "strikePrice",
            "premium",
            "size",
            "volume",
            "openInterest",
            "tradeSideCode",
            "tradeConsolidationType",
            "isGoldenSweep",
            "isUnusual",
            "isOpeningPosition",
            "isVolumeGreaterThanOpenInterest",
            "tradeTime",
        ],
    }

    response = post_quant("/v1/options/tool/order-flow/consolidated", payload)
    rows = response.get("data", []) if isinstance(response, dict) else []

    candidates = []
    for row in rows:
        try:
            dte = float(row.get("dte"))
        except (TypeError, ValueError):
            continue

        # "Aggressive" means it printed above the ask.
        if not (0 <= dte <= 14):
            continue
        if str(row.get("tradeSideCode") or "").upper() != "ABOVE_ASK":
            continue

        row = dict(row)
        row["_score"] = aggressive_flow_score(row)
        candidates.append(row)

    if not candidates:
        return None

    return max(candidates, key=lambda item: item["_score"])


def aggressive_contract_html(row, side):
    css_side = "call" if side == "CALL" else "put"
    side_class = "green" if side == "CALL" else "red"

    if not row:
        return (
            f"<div class='flow-contract {css_side}'>"
            f"<div class='flow-side {side_class}'>{side}</div>"
            f"<div class='flow-symbol'>NO QUALIFYING FLOW</div>"
            f"<div class='flow-meta'>No above-ask 0–14 DTE trade found in the selected window.</div>"
            f"</div>"
        )

    strike = row.get("strikePrice", "—")
    expiration = row.get("expirationDate", "—")
    dte = row.get("dte", "—")
    premium = format_flow_premium(row.get("premium"))
    consolidation = str(row.get("tradeConsolidationType") or "TRADE").upper()
    size = row.get("size", "—")
    flags = []

    if row.get("isGoldenSweep"):
        flags.append("GOLDEN")
    if row.get("isUnusual"):
        flags.append("UNUSUAL")
    if row.get("isOpeningPosition"):
        flags.append("OPENING")
    if row.get("isVolumeGreaterThanOpenInterest"):
        flags.append("VOL>OI")

    flag_text = " · ".join(flags) if flags else "ABOVE ASK"
    strength = row.get("_score", 0)

    return (
        f"<div class='flow-contract {css_side}'>"
        f"<div class='flow-side {side_class}'>{side} · {consolidation}</div>"
        f"<div class='flow-symbol'>{search_ticker} {strike}</div>"
        f"<div class='flow-meta'>{expiration} · {dte:g} DTE · {size} contracts<br>{flag_text}</div>"
        f"<div class='flow-premium'>{premium}</div>"
        f"<div class='flow-strength'>Aggression score: {format_flow_premium(strength)}</div>"
        f"</div>"
    )


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


aggressive_call = get_strongest_aggressive_flow(search_ticker, "CALL")
aggressive_put = get_strongest_aggressive_flow(search_ticker, "PUT")

call_aggression = float((aggressive_call or {}).get("_score") or 0)
put_aggression = float((aggressive_put or {}).get("_score") or 0)

if call_aggression > put_aggression:
    aggressive_dominance = "CALL aggression is stronger over the selected 14-day window."
    aggressive_dominance_class = "green"
elif put_aggression > call_aggression:
    aggressive_dominance = "PUT aggression is stronger over the selected 14-day window."
    aggressive_dominance_class = "red"
else:
    aggressive_dominance = "No clear aggressive-flow advantage."
    aggressive_dominance_class = "yellow"

# ---------------- PANEL ----------------

def panel(symbol, price, change, rows):
    is_live = str(change) == "LIVE"
    price_class = "price-green" if is_live else "price-red"
    status_badge = "badge-green" if is_live else "badge-yellow"
    status_text = "LIVE" if is_live else "SNAPSHOT"

    try:
        local_paths = build_paths(rows, price)
        local_regime = "MIXED"
        if local_paths:
            _, _, _, _, local_neg, local_pos = local_paths
            local_regime = "LONG GAMMA" if abs(local_pos[1]) >= abs(local_neg[1]) else "SHORT GAMMA"
    except Exception:
        local_regime = "MIXED"

    regime_badge = (
        "badge-green" if local_regime == "LONG GAMMA"
        else "badge-red" if local_regime == "SHORT GAMMA"
        else "badge-yellow"
    )

    st.markdown(
        f"<div class='panel-title'>{html.escape(str(symbol))}</div>"
        f"<div class='{price_class}'>${html.escape(str(price))}</div>"
        f"<div class='ticker-meta'>"
        f"<span class='badge {status_badge}'>{status_text}</span>"
        f"<span class='badge {regime_badge}'>{local_regime}</span>"
        f"</div>",
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
    execution_grade = "A+"
elif score >= 75:
    swing_grade = "A"
    execution_grade = "A"
elif score >= 65:
    swing_grade = "B"
    execution_grade = "A"
elif score >= 55:
    swing_grade = "C"
    execution_grade = "B"
else:
    swing_grade = "D"
    execution_grade = "C"

if score >= 75:
    confidence_label = "HIGH"
elif score >= 60:
    confidence_label = "MED"
else:
    confidence_label = "LOW"

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
    dealer_bias = "LONG GAMMA"
    environment = "CHOP"
elif negative_total > positive_total * 1.35:
    gamma_regime = "EXPANSIVE"
    regime_class = "purple"
    dealer_bias = "SHORT GAMMA"
    environment = "TREND"
else:
    gamma_regime = "MIXED"
    regime_class = "yellow"
    dealer_bias = "BALANCED"
    environment = "ROTATION"

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

support_zone = downside_targets[0] if downside_targets else danger_level
resistance_zone = upside_targets[0] if upside_targets else primary_magnet

bull_entry = upside_targets[0] if upside_targets else primary_magnet
bear_entry = downside_targets[0] if downside_targets else danger_level
bull_target_1 = upside_targets[0] if upside_targets else primary_magnet
bull_target_2 = upside_targets[-1] if upside_targets else primary_magnet
bear_target_1 = downside_targets[0] if downside_targets else danger_level
bear_target_2 = downside_targets[-1] if downside_targets else danger_level

if flow_short == "CALLS" and score >= 65:
    best_side = "LONGS"
    entry_level = bull_entry
    confirmation_level = bull_target_1
    invalidation_level = bear_entry
    target_1 = bull_target_1
    target_2 = bull_target_2
    trade_class = "green"
    edge_text = f"Buyers control above {bull_entry}. Avoid longs below {bear_entry}."
    read_main = f"BUYERS CONTROL ABOVE {bull_entry}"
elif flow_short == "PUTS" and score >= 65:
    best_side = "SHORTS"
    entry_level = bear_entry
    confirmation_level = bear_target_1
    invalidation_level = bull_entry
    target_1 = bear_target_1
    target_2 = bear_target_2
    trade_class = "red"
    edge_text = f"Sellers control below {bear_entry}. Avoid shorts above {bull_entry}."
    read_main = f"SELLERS CONTROL BELOW {bear_entry}"
else:
    best_side = "WAIT"
    entry_level = f"{bear_entry} / {bull_entry}"
    confirmation_level = "BREAK RANGE"
    invalidation_level = "N/A"
    target_1 = "CONFIRM"
    target_2 = "CONFIRM"
    trade_class = "yellow"
    edge_text = f"Wait for a break outside {bear_entry}–{bull_entry}."
    read_main = f"NO CLEAN EDGE INSIDE {bear_entry}–{bull_entry}"

if gamma_regime == "STABLE":
    read_line_1 = "Dealer positioning favors rotation and mean reversion."
elif gamma_regime == "EXPANSIVE":
    read_line_1 = "Dealer positioning can amplify momentum and volatility."
else:
    read_line_1 = "Dealer positioning is mixed and two-way trade remains possible."

if flow_short == "CALLS":
    read_line_2 = f"Call flow supports continuation while price holds above {bull_entry}."
elif flow_short == "PUTS":
    read_line_2 = f"Put flow supports continuation while price remains below {bear_entry}."
else:
    read_line_2 = "Flow is mixed, so confirmation matters more than anticipation."

read_line_3 = f"Primary magnet: {primary_magnet}. Key accelerator: {danger_level}."
read_line_4 = f"Upside path: {upside_text}. Downside path: {downside_text}."


aggressive_flow_html = (
    f"<div class='aggressive-flow'>"
    f"<div class='aggressive-title'>2-WEEK AGGRESSIVE FLOW</div>"
    f"<div class='aggressive-subtitle'>Strongest above-ask CALL and PUT · 0–14 DTE</div>"
    f"<div class='flow-contract-grid'>"
    f"{aggressive_contract_html(aggressive_call, 'CALL')}"
    f"{aggressive_contract_html(aggressive_put, 'PUT')}"
    f"</div>"
    f"<div class='flow-dominant'><span class='{aggressive_dominance_class}'>●</span> "
    f"{aggressive_dominance}</div>"
    f"</div>"
)

summary_html = (
    f"<div class='summary-panel'>"

    f"<div class='edge-banner'>"
    f"<div class='edge-label'>7C EDGE</div>"
    f"<div class='edge-text'>{edge_text}</div>"
    f"</div>"

    f"<div class='summary-grid'>"
    f"<div class='summary-item'><div class='summary-label'>BIAS</div>"
    f"<div class='summary-value {flow_class}'>{bias_text}</div></div>"
    f"<div class='summary-item'><div class='summary-label'>SWING</div>"
    f"<div class='summary-value'>{swing_grade}</div></div>"
    f"<div class='summary-item'><div class='summary-label'>EXECUTION</div>"
    f"<div class='summary-value'>{execution_grade}</div></div>"
    f"<div class='summary-item'><div class='summary-label'>CONF</div>"
    f"<div class='summary-value'>{score}%<span class='conf-level'>{confidence_label}</span></div></div>"
    f"<div class='summary-item'><div class='summary-label'>RISK</div>"
    f"<div class='summary-value {risk_class}'>{risk_text}</div></div>"
    f"<div class='summary-item'><div class='summary-label'>FLOW</div>"
    f"<div class='summary-value {flow_class}'>{flow_short}</div></div>"
    f"</div>"

    f"<div class='summary-details'>"
    f"<div class='detail-item'><div class='detail-label'>REGIME</div>"
    f"<div class='detail-value {regime_class}'>{gamma_regime}</div></div>"
    f"<div class='detail-item'><div class='detail-label'>DEALERS</div>"
    f"<div class='detail-value'>{dealer_bias}</div></div>"
    f"<div class='detail-item'><div class='detail-label'>ENVIRONMENT</div>"
    f"<div class='detail-value'>{environment}</div></div>"
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
    f"<div class='detail-item'><div class='detail-label'>SUPPORT ZONE</div>"
    f"<div class='detail-value zone-support'>{support_zone}</div></div>"
    f"<div class='detail-item'><div class='detail-label'>RESISTANCE ZONE</div>"
    f"<div class='detail-value zone-resistance'>{resistance_zone}</div></div>"
    f"</div>"

    f"<div class='intelligence-flow-grid'>"
    f"<div class='market-read'>"
    f"<div class='market-read-title'>7TH CAPITAL MARKET INTELLIGENCE</div>"
    f"<div class='market-read-main {flow_class}'>{read_main}</div>"
    f"<div class='market-read-line'>• {read_line_1}</div>"
    f"<div class='market-read-line'>• {read_line_2}</div>"
    f"<div class='market-read-line'>• {read_line_3}</div>"
    f"<div class='market-read-line'>• {read_line_4}</div>"
    f"</div>"
    f"{aggressive_flow_html}"
    f"</div>"

    f"<div class='execution-panel'>"
    f"<div class='execution-title'>7TH CAPITAL EXECUTION PLAN</div>"
    f"<div class='execution-grid'>"
    f"<div class='execution-item'><div class='execution-label'>SIDE</div>"
    f"<div class='execution-value {trade_class}'>{best_side}</div></div>"
    f"<div class='execution-item'><div class='execution-label'>ENTRY</div>"
    f"<div class='execution-value'>{entry_level}</div></div>"
    f"<div class='execution-item'><div class='execution-label'>CONFIRM</div>"
    f"<div class='execution-value'>{confirmation_level}</div></div>"
    f"<div class='execution-item'><div class='execution-label'>INVALID</div>"
    f"<div class='execution-value'>{invalidation_level}</div></div>"
    f"<div class='execution-item'><div class='execution-label'>TARGET 1</div>"
    f"<div class='execution-value'>{target_1}</div></div>"
    f"<div class='execution-item'><div class='execution-label'>TARGET 2</div>"
    f"<div class='execution-value'>{target_2}</div></div>"
    f"</div>"
    f"</div>"
    f"</div>"
)

st.markdown(summary_html, unsafe_allow_html=True)
