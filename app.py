"""
WattWise — Electricity Consumption Intelligence System
Clean solar-themed Streamlit dashboard.

Run:
    pip install -r requirements.txt
    streamlit run app.py

Place energy_weather_raw_data.csv beside this file.
If the notebook has been run, the app also uses its outputs/ and models/ artifacts
for the ML evaluation section.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Page and theme
# ─────────────────────────────────────────────────────────────────────────────
APP_NAME = "WattWise"
TAGLINE = "Electricity Consumption Intelligence System"
st.set_page_config(page_title=f"{APP_NAME} | Energy Analytics", page_icon="⚡",
                   layout="wide", initial_sidebar_state="expanded")

CREAM = "#FFF8EC"
SAND = "#FDECC8"
WHITE = "#FFFFFF"
INK = "#3B2A14"
MUTED = "#8A6D3B"
AMBER = "#F59E0B"
ORANGE = "#EA580C"
BROWN = "#B45309"
OLIVE = "#65A30D"
TEAL = "#0F766E"
BLUE = "#5B8DB0"
GRID = "rgba(120,80,20,0.12)"
PALETTE = [AMBER, ORANGE, BROWN, OLIVE, TEAL, BLUE]
SEASON = {12:"Winter", 1:"Winter", 2:"Winter", 3:"Spring", 4:"Spring",
          5:"Spring", 6:"Summer", 7:"Summer", 8:"Summer",
          9:"Autumn", 10:"Autumn", 11:"Autumn"}
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');

:root {
  --cream:#FFF9F0; --sand:#FCEBCB; --paper:#FFFFFF; --ink:#302313;
  --muted:#725B3D; --soft:#927A5B; --amber:#F2A900; --orange:#E87518;
  --line:#E9DCC8; --green:#547B42;
}
html, body, .stApp, .stApp p, .stApp label, .stApp input,
.stApp textarea, .stApp button, .stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stMetricLabel"],
.stApp [data-testid="stMetricValue"] {
  font-family:'DM Sans',sans-serif !important;
  color:var(--ink);
  font-size:16px;
}
/* Keep Streamlit's own icon font intact (expander arrows, select arrows, etc.). */
.material-icons, .material-icons-round, .material-symbols-rounded,
.material-symbols-outlined, [data-testid="stExpander"] svg,
[data-testid="stSelectbox"] svg, [data-testid="stMultiSelect"] svg {
  font-family:'Material Symbols Rounded','Material Icons',sans-serif !important;
}
.stApp {
  background:linear-gradient(180deg,#FFF9F0 0%,#FFFDF9 100%);
}
[data-testid="stSidebar"] {
  background:linear-gradient(180deg,#FBE9C5 0%,#FFF2DC 100%);
  border-right:1px solid #E8D5B5;
}
[data-testid="stHeader"] {background:rgba(255,249,240,.92);backdrop-filter:blur(10px);}
.block-container {padding-top:1.5rem;padding-bottom:3rem;max-width:1540px;}
h1,h2,h3,h4,h5,h6 {
  font-family:'Manrope','DM Sans',sans-serif !important;
  color:var(--ink)!important; font-weight:800!important;
  letter-spacing:-.025em!important; line-height:1.25!important;
}
h1 {font-size:2.35rem!important;} h2 {font-size:1.8rem!important;}
h3 {font-size:1.42rem!important;} h4 {font-size:1.18rem!important;}
p,li, label, [data-testid="stMarkdownContainer"] {
  line-height:1.65;
}
p {font-size:1rem;}
small,.stCaption,[data-testid="stCaptionContainer"] {
  color:var(--muted)!important; font-size:.88rem!important; line-height:1.55!important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  font-size:.96rem; line-height:1.55;
}
[data-testid="stSidebar"] label {
  color:#49351D!important; font-size:.95rem!important; font-weight:700!important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
  font-size:.88rem!important; color:#705936!important;
}
.hero {
  position:relative;overflow:hidden;
  background:linear-gradient(112deg,#FCE7B5 0%,#FFF1D6 52%,#FFFAF0 100%);
  border:1px solid #EAD6B2;border-radius:25px;padding:1.9rem 2.1rem;
  margin-bottom:1.5rem;display:flex;align-items:center;justify-content:space-between;
  box-shadow:0 10px 30px rgba(100,65,15,.07);
}
.hero:after {
  content:"";position:absolute;width:230px;height:230px;border-radius:50%;
  right:7%;top:-145px;background:rgba(245,169,0,.13);
  box-shadow:0 0 0 28px rgba(245,169,0,.05),0 0 0 58px rgba(245,169,0,.035);
}
.brand {
  font-family:'Manrope',sans-serif;font-size:2.9rem;font-weight:800;
  line-height:1.05;letter-spacing:-.065em;color:#302313;
}
.brand span {color:#D95F13;}
.tagline {color:#634B2D;font-size:1.08rem;margin-top:.55rem;font-weight:600;line-height:1.55;}
.hero-mark {font-size:4rem;z-index:1;filter:drop-shadow(0 7px 10px rgba(180,83,9,.15));}
.hero-chip {
  display:inline-flex;align-items:center;gap:.4rem;margin-top:1rem;padding:.48rem .85rem;
  border-radius:999px;background:rgba(255,255,255,.84);border:1px solid #EAD9BC;
  color:#68471F;font-size:.78rem;font-weight:800;letter-spacing:.045em;
}
.kpi {
  position:relative;overflow:hidden;background:#FFFFFF;border:1px solid var(--line);
  border-radius:17px;padding:1.2rem 1.2rem;min-height:135px;
  box-shadow:0 5px 16px rgba(80,50,10,.035);
}
.kpi:before {
  content:"";position:absolute;left:0;top:0;bottom:0;width:5px;
  background:linear-gradient(180deg,#F2A900,#E87518);
}
.kpi-label {
  font-size:.78rem;color:#725B3D;font-weight:800;
  text-transform:uppercase;letter-spacing:.065em;line-height:1.4;
}
.kpi-value {
  font-family:'Manrope',sans-serif;font-size:2rem;color:#302313;font-weight:800;
  line-height:1.25;margin-top:.5rem;letter-spacing:-.045em;
  overflow-wrap:anywhere;
}
.kpi-help {font-size:.85rem;color:#725B3D;margin-top:.3rem;line-height:1.45;}
.section-heading {
  display:flex;align-items:center;gap:.75rem;margin:1.45rem 0 .65rem;
}
.section-heading .section-dot {
  flex:0 0 11px;width:11px;height:11px;border-radius:4px;
  background:linear-gradient(135deg,#F2A900,#E87518);
  box-shadow:0 0 0 5px rgba(242,169,0,.12);
}
.section-heading .section-title {
  font-family:'Manrope',sans-serif;font-size:1.45rem;font-weight:800;
  letter-spacing:-.035em;color:#302313;line-height:1.3;
}
.section-note {
  color:#725B3D;font-size:.98rem;margin:0 0 1rem 1.35rem;line-height:1.6;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
  background:#FFFFFF;border:1px solid var(--line);border-radius:17px;
  box-shadow:0 4px 14px rgba(80,50,10,.025);
}
.stTabs [data-baseweb="tab-list"] {
  gap:.45rem;border-bottom:1px solid #E7DCCB;padding:.2rem .1rem;
}
.stTabs [data-baseweb="tab"] {
  color:#725B3D;font-weight:700;padding:.85rem 1rem;
  border-radius:11px 11px 0 0;font-size:.96rem;
}
.stTabs [aria-selected="true"] {color:#302313!important;background:#FFF0D2;}
.stTabs [data-baseweb="tab-highlight"] {
  background:linear-gradient(90deg,#F2A900,#E87518);height:3px;border-radius:4px;
}
.insight {
  background:linear-gradient(110deg,#FFFFFF,#FFFBF3);border:1px solid var(--line);
  border-left:5px solid #E99A1A;border-radius:14px;padding:1.1rem 1.2rem;
  margin-bottom:.8rem;box-shadow:0 4px 14px rgba(80,50,10,.025);
  line-height:1.7;font-size:.98rem;color:#49351D;
}
.insight b {color:#302313;font-size:1.02rem;}
.footer {
  text-align:center;color:#725B3D;font-size:.88rem;padding:1.8rem 0 .4rem;
  border-top:1px solid var(--line);margin-top:2rem;line-height:1.7;
}
.note {
  background:#FFF1D6;border:1px solid #F0D39B;border-radius:14px;
  padding:1.1rem 1.2rem;color:#49351D;line-height:1.7;font-size:.98rem;
}
.stButton>button,[data-testid="stDownloadButton"] button {
  border:0;border-radius:11px;background:linear-gradient(100deg,#EFA900,#E87518);
  color:#fff;font-weight:800;padding:.62rem 1.05rem;font-size:.95rem;
  box-shadow:0 5px 13px rgba(234,88,12,.14);
}
.stButton>button:hover,[data-testid="stDownloadButton"] button:hover {
  color:#fff;border:0;filter:brightness(1.04);transform:translateY(-1px);
}
[data-baseweb="select"]>div,[data-baseweb="input"]>div,[data-baseweb="textarea"] {
  border-radius:10px!important;border-color:#DCCBB2!important;background:#fff;
}
[data-testid="stMetric"] {
  background:#fff;border:1px solid var(--line);padding:15px 17px;border-radius:14px;
}
[data-testid="stMetricLabel"] {color:#725B3D;font-weight:700;font-size:.9rem;}
[data-testid="stMetricValue"] {
  font-family:'Manrope',sans-serif;font-weight:800;color:#302313;font-size:1.6rem;
}
[data-testid="stDataFrame"] {font-size:.92rem;}
hr {border-color:var(--line);}
@media(max-width:760px) {
  .block-container {padding-left:1rem;padding-right:1rem;}
  .brand {font-size:2.15rem;} .hero {padding:1.3rem;}
  .hero-mark {font-size:2.5rem;} .kpi-value {font-size:1.55rem;}
  .stTabs [data-baseweb="tab"] {padding:.65rem .55rem;font-size:.82rem;}
  .section-heading .section-title {font-size:1.2rem;}
}

/* Main dashboard navigation */
.stTabs {
  position:relative;
}
.stTabs [data-baseweb="tab-list"] {
  position:sticky;
  top:3.55rem;
  z-index:30;
  display:flex;
  flex-wrap:wrap;
  align-items:center;
  gap:.45rem;
  padding:.65rem .7rem;
  margin:.15rem 0 1.1rem;
  background:rgba(255,250,242,.96);
  border:1px solid #E9DCC8;
  border-radius:15px;
  box-shadow:0 5px 16px rgba(80,50,10,.055);
  backdrop-filter:blur(12px);
}
.stTabs [data-baseweb="tab"] {
  min-height:43px;
  white-space:nowrap;
  border:1px solid transparent;
  border-radius:10px;
  padding:.68rem 1rem;
  font-size:.94rem;
  line-height:1.25;
}
.stTabs [data-baseweb="tab"]:hover {
  background:#FFF3DE;
  color:#302313;
}
.stTabs [aria-selected="true"] {
  background:#FFE7B5 !important;
  border-color:#F0D39B !important;
  color:#302313 !important;
}
.stTabs [data-baseweb="tab-highlight"] {display:none;}

/* Native Streamlit expanders: readable labels and correctly aligned arrows */
[data-testid="stExpander"] {
  border:1px solid #E7D9C5 !important;
  border-radius:13px !important;
  background:#FFFEFB !important;
  overflow:hidden;
  margin:.65rem 0 !important;
}
[data-testid="stExpander"] summary {
  min-height:54px;
  padding:.8rem 1rem !important;
  display:flex !important;
  align-items:center !important;
  gap:.7rem !important;
  color:#302313 !important;
  font-family:'Manrope','DM Sans',sans-serif !important;
  font-size:1rem !important;
  font-weight:750 !important;
  line-height:1.4 !important;
}
[data-testid="stExpander"] summary p {
  margin:0 !important;
  font-family:'Manrope','DM Sans',sans-serif !important;
  font-size:1rem !important;
  font-weight:750 !important;
  line-height:1.4 !important;
}
[data-testid="stExpander"] summary svg {
  display:block !important;
  flex:0 0 20px !important;
  width:20px !important;
  height:20px !important;
  min-width:20px !important;
  color:#B96512 !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
  padding:.4rem 1rem 1rem !important;
  border-top:1px solid #F0E5D5;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] p {
  font-size:.96rem;
  line-height:1.6;
}

/* Consistent chart and card spacing */
[data-testid="stPlotlyChart"] {padding:.25rem 0;}
[data-testid="stVerticalBlockBorderWrapper"] {overflow:hidden;}
.stAlert {border-radius:13px;}
.stCaption, [data-testid="stCaptionContainer"] {line-height:1.55 !important;}


/* Full-width WattWise hero banner */
.block-container {
  width:100% !important;
  max-width:100% !important;
  padding-left:clamp(1rem, 2.4vw, 2.5rem) !important;
  padding-right:clamp(1rem, 2.4vw, 2.5rem) !important;
}
.hero {
  width:100%;
  min-height:230px;
  box-sizing:border-box;
  padding:2.25rem clamp(1.4rem, 3vw, 3rem);
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:2rem;
  border-radius:26px;
  margin:0 0 1.7rem 0;
  background:
    radial-gradient(circle at 87% 12%, rgba(245,169,0,.12) 0 105px, transparent 106px),
    linear-gradient(112deg,#FCE7B5 0%,#FFF1D6 52%,#FFFAF0 100%);
}
.hero > div:first-child {
  position:relative;
  z-index:2;
  flex:1 1 auto;
  min-width:0;
}
.brand {
  font-size:clamp(2.7rem, 4.2vw, 3.65rem);
  line-height:1.08;
  letter-spacing:-.06em;
}
.tagline {
  font-size:1.12rem;
  line-height:1.55;
  margin-top:.62rem;
  max-width:780px;
}
.hero-chip {
  margin-top:1.1rem;
  padding:.58rem 1rem;
  font-size:.82rem;
}
.hero-mark {
  flex:0 0 auto;
  display:flex;
  align-items:center;
  justify-content:center;
  min-width:145px;
  font-size:4.8rem;
  white-space:nowrap;
  position:relative;
  z-index:2;
}
@media(max-width:760px) {
  .hero {min-height:190px;gap:1rem;padding:1.45rem;align-items:flex-start;}
  .brand {font-size:2.4rem;}
  .tagline {font-size:.98rem;}
  .hero-mark {min-width:auto;font-size:2.6rem;align-self:center;}
}


/* WattWise full-width presentation */
.block-container {
  max-width:none !important;
  width:100% !important;
  padding-left:clamp(1.15rem,2.5vw,2.8rem) !important;
  padding-right:clamp(1.15rem,2.5vw,2.8rem) !important;
}
[data-testid="stSidebar"] {
  min-width:320px !important;
  max-width:360px !important;
  background:linear-gradient(180deg,#FBE7BD 0%,#FFF2D9 58%,#FFF8EB 100%) !important;
  border-right:1px solid #E6D2AC !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding:1.35rem 1.15rem 2rem !important;
}
[data-testid="stSidebar"] h2 {
  font-family:'Manrope',sans-serif !important;
  font-size:1.9rem !important;
  letter-spacing:-.045em !important;
  margin-bottom:.35rem !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
  color:#4A3218;
  letter-spacing:.035em;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div,
[data-testid="stSidebar"] [data-testid="stDateInput"] > div,
[data-testid="stSidebar"] [data-testid="stNumberInput"] > div {
  border-radius:12px !important;
}
[data-testid="stSidebar"] hr {
  margin:1.25rem 0 !important;
  border-color:#E2CDA7 !important;
}
.hero {
  width:100% !important;
  min-height:265px !important;
  box-sizing:border-box !important;
  padding:2.35rem clamp(1.5rem,4vw,3.8rem) !important;
  margin:0 0 1.65rem 0 !important;
  display:flex !important;
  align-items:center !important;
  justify-content:space-between !important;
  gap:2rem !important;
  border-radius:28px !important;
  border:1px solid #E9D3A9 !important;
  background:
    radial-gradient(circle at 88% 15%,rgba(245,169,0,.14) 0 115px,transparent 117px),
    radial-gradient(circle at 88% 15%,rgba(245,169,0,.07) 0 165px,transparent 167px),
    linear-gradient(112deg,#FBE5B3 0%,#FFF0D2 52%,#FFFBF2 100%) !important;
  box-shadow:0 12px 34px rgba(112,73,17,.075) !important;
}
.hero > div:first-child {flex:1 1 auto;min-width:0;position:relative;z-index:2;}
.brand {
  font-size:clamp(3rem,5vw,4.25rem) !important;
  font-weight:850 !important;
  letter-spacing:-.065em !important;
  line-height:1.02 !important;
}
.tagline {
  max-width:850px !important;
  font-size:clamp(1.02rem,1.35vw,1.22rem) !important;
  line-height:1.55 !important;
  margin-top:.72rem !important;
}
.hero-chip {
  margin-top:1.2rem !important;
  padding:.62rem 1.05rem !important;
  font-size:.84rem !important;
}
.hero-mark {
  flex:0 0 auto !important;
  min-width:170px !important;
  display:flex !important;
  align-items:center !important;
  justify-content:center !important;
  font-size:5.3rem !important;
  white-space:nowrap !important;
}
.run-deploy-card {
  border:1px solid #E8D5B4;
  border-radius:15px;
  background:linear-gradient(135deg,rgba(255,255,255,.82),rgba(255,246,226,.95));
  padding:1rem;
  margin:.6rem 0 .25rem;
  color:#49351D;
  line-height:1.6;
}
.run-deploy-title {
  font-family:'Manrope',sans-serif;
  color:#302313;
  font-size:1.03rem;
  font-weight:800;
  margin-bottom:.45rem;
}
.run-deploy-card code {
  display:block;
  background:#3B2A14;
  color:#FFF8EC;
  padding:.7rem .8rem;
  border-radius:9px;
  margin:.45rem 0;
  font-size:.86rem;
  overflow-wrap:anywhere;
}
@media(max-width:760px) {
  [data-testid="stSidebar"] {min-width:280px !important;max-width:320px !important;}
  .hero {min-height:215px !important;padding:1.5rem !important;gap:1rem !important;}
  .brand {font-size:2.55rem !important;}
  .tagline {font-size:.98rem !important;}
  .hero-mark {min-width:auto !important;font-size:2.9rem !important;}
}


/* ── WattWise top hero: wide split layout inspired by the supplied reference ── */
.block-container {
    width: 100% !important;
    max-width: none !important;
    padding-top: 1.15rem !important;
    padding-left: clamp(1rem, 2.4vw, 2.5rem) !important;
    padding-right: clamp(1rem, 2.4vw, 2.5rem) !important;
    padding-bottom: 3rem !important;
}
.hero {
    position: relative !important;
    isolation: isolate !important;
    box-sizing: border-box !important;
    width: 100% !important;
    min-height: 300px !important;
    margin: 0 0 1.65rem 0 !important;
    padding: clamp(2rem, 3.5vw, 3.1rem) clamp(1.5rem, 3.4vw, 3.6rem) !important;
    display: grid !important;
    grid-template-columns: minmax(0, 1.45fr) minmax(220px, .75fr) !important;
    align-items: center !important;
    gap: 1.5rem !important;
    overflow: hidden !important;
    border: 1px solid #E9D3A9 !important;
    border-radius: 25px !important;
    background:
        radial-gradient(circle at 84% 18%, rgba(245,169,0,.19) 0 90px, transparent 92px),
        radial-gradient(circle at 84% 18%, rgba(245,169,0,.09) 0 142px, transparent 144px),
        radial-gradient(circle at 100% 100%, rgba(232,117,24,.10) 0 180px, transparent 182px),
        linear-gradient(112deg, #FBE5B3 0%, #FFF0D2 53%, #FFFBF2 100%) !important;
    box-shadow: 0 13px 34px rgba(112,73,17,.075) !important;
}
.hero:before {
    content: "";
    position: absolute;
    z-index: -1;
    width: 290px;
    height: 290px;
    right: 4.5%;
    top: -190px;
    border-radius: 50%;
    border: 1px solid rgba(201,135,30,.20);
    box-shadow: 0 0 0 23px rgba(201,135,30,.045),
                0 0 0 48px rgba(201,135,30,.03);
}
.hero:after {
    content: "";
    position: absolute;
    z-index: -1;
    width: 220px;
    height: 220px;
    left: 43%;
    bottom: -190px;
    border-radius: 50%;
    background: rgba(232,117,24,.055);
}
.hero > div:first-child {
    min-width: 0 !important;
    position: relative !important;
    z-index: 2 !important;
}
.brand {
    margin: 0 !important;
    font-family: 'Manrope', 'DM Sans', sans-serif !important;
    font-size: clamp(3.15rem, 5.2vw, 4.8rem) !important;
    font-weight: 850 !important;
    line-height: 1.02 !important;
    letter-spacing: -.075em !important;
    color: #302313 !important;
}
.brand span { color: #D95F13 !important; }
.tagline {
    max-width: 760px !important;
    margin-top: .7rem !important;
    color: #634B2D !important;
    font-size: clamp(1rem, 1.35vw, 1.2rem) !important;
    font-weight: 600 !important;
    line-height: 1.55 !important;
}
.hero-chip {
    display: inline-flex !important;
    align-items: center !important;
    margin-top: 1.15rem !important;
    padding: .62rem 1rem !important;
    border-radius: 999px !important;
    background: rgba(255,255,255,.88) !important;
    border: 1px solid #EAD9BC !important;
    color: #68471F !important;
    font-size: .82rem !important;
    font-weight: 800 !important;
    letter-spacing: .045em !important;
}
.hero-mark {
    position: relative !important;
    z-index: 2 !important;
    min-width: 0 !important;
    width: 100% !important;
    min-height: 205px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: .3rem !important;
    white-space: nowrap !important;
    font-size: clamp(4.8rem, 7vw, 6.8rem) !important;
    filter: drop-shadow(0 10px 13px rgba(181,91,15,.17)) !important;
}
.hero-mark:before {
    content: "";
    position: absolute;
    width: 190px;
    height: 105px;
    border: 1px solid rgba(208,139,34,.42);
    border-radius: 50%;
    transform: rotate(-18deg);
}
.hero-mark:after {
    content: "SMART ENERGY  •  LIVE INSIGHTS";
    position: absolute;
    bottom: 4px;
    right: 1%;
    padding: .48rem .8rem;
    border: 1px solid rgba(218,157,64,.38);
    border-radius: 999px;
    background: rgba(255,255,255,.72);
    color: #80551F;
    font-family: 'DM Sans', sans-serif;
    font-size: .66rem;
    font-weight: 800;
    letter-spacing: .08em;
}
@media (max-width: 900px) {
    .hero {
        grid-template-columns: minmax(0, 1.3fr) minmax(130px, .65fr) !important;
        min-height: 255px !important;
        padding: 1.8rem !important;
    }
    .hero-mark { font-size: 4.2rem !important; min-height: 170px !important; }
}
@media (max-width: 620px) {
    .block-container {
        padding-top: .8rem !important;
        padding-left: .8rem !important;
        padding-right: .8rem !important;
    }
    .hero {
        grid-template-columns: 1fr !important;
        min-height: 0 !important;
        gap: .5rem !important;
        padding: 1.5rem !important;
        border-radius: 19px !important;
    }
    .brand { font-size: 2.8rem !important; }
    .tagline { font-size: .98rem !important; }
    .hero-mark {
        min-height: 92px !important;
        justify-content: flex-end !important;
        padding-right: .7rem !important;
        font-size: 3.3rem !important;
    }
    .hero-mark:before { width: 145px; height: 75px; }
    .hero-mark:after { left: 0; right: auto; bottom: 0; font-size: .58rem; }
}


/* Keep Streamlit's native toolbar / Deploy control clear above the app content. */
[data-testid="stHeader"] {
    display: block !important;
    height: 3.5rem !important;
    background: rgba(255,249,240,.96) !important;
    z-index: 1000 !important;
}
[data-testid="stToolbar"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}
[data-testid="stMain"] .block-container {
    padding-top: 1.15rem !important;
    margin-top: 0 !important;
}
.hero {
    margin-top: .25rem !important;
    width: 100% !important;
    max-width: 100% !important;
}
/* Do not let decorative hero layers cover Streamlit's top-right controls. */
.hero, .hero:before, .hero:after {
    pointer-events: none;
}
.hero > div {
    pointer-events: auto;
}
@media (max-width: 620px) {
    [data-testid="stMain"] .block-container {
        padding-top: .75rem !important;
    }
}


/* ── Outer application frame: includes the native Streamlit Deploy toolbar ── */
html, body {
    background: #F4EBDD !important;
}
.stApp {
    box-sizing: border-box !important;
    width: calc(100% - 10px) !important;
    min-height: calc(100vh - 10px) !important;
    margin: 5px !important;
    border: 1.5px solid #DCC8A8 !important;
    border-radius: 16px !important;
    overflow: hidden !important;
    box-shadow:
        0 0 0 1px rgba(255,255,255,.78),
        0 8px 28px rgba(83,55,18,.10) !important;
    background: linear-gradient(180deg,#FFF9F0 0%,#FFFDF9 100%) !important;
}
/* Keep the real Deploy button and Streamlit menu inside the framed top edge. */
[data-testid="stHeader"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    width: 100% !important;
    height: 3.5rem !important;
    background: rgba(255,249,240,.97) !important;
    border-bottom: 1px solid rgba(220,200,168,.48) !important;
    backdrop-filter: blur(10px);
    z-index: 1000 !important;
}
[data-testid="stToolbar"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}
/* Preserve the full-width content while keeping it within the rounded frame. */
[data-testid="stAppViewContainer"] {
    border-radius: 15px !important;
    overflow: hidden !important;
}
[data-testid="stMain"] {
    background: transparent !important;
}
[data-testid="stMain"] .block-container {
    padding-top: 1.15rem !important;
}
@media (max-width: 620px) {
    .stApp {
        width: calc(100% - 6px) !important;
        min-height: calc(100vh - 6px) !important;
        margin: 3px !important;
        border-radius: 12px !important;
    }
    [data-testid="stAppViewContainer"] {
        border-radius: 11px !important;
    }
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Data loading: prefer notebook outputs; build from raw data if outputs absent
# ─────────────────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "outputs"
DASH = OUTPUT / "dashboard_data"
MODEL_DIR = BASE / "models"
RAW_CANDIDATES = [BASE / "energy_weather_raw_data.csv",
                  BASE / "dataset" / "energy_weather_raw_data.csv",
                  BASE.parent / "energy_weather_raw_data.csv"]

@st.cache_data(show_spinner="Preparing electricity and weather data…")
def load_data():
    hourly_file = OUTPUT / "hourly_dataset.csv"
    daily_file = OUTPUT / "daily_dataset.csv"

    if hourly_file.exists() and daily_file.exists():
        h = pd.read_csv(hourly_file, index_col=0, parse_dates=True)
        d = pd.read_csv(daily_file, index_col=0, parse_dates=True)
        h.index.name = "timestamp"
        d.index.name = "date"
        source = "Notebook processed outputs"
        return h, d, source

    raw_path = next((p for p in RAW_CANDIDATES if p.exists()), None)
    if raw_path is None:
        raise FileNotFoundError(
            "Cannot find energy_weather_raw_data.csv or outputs/hourly_dataset.csv. "
            "Place the raw CSV beside app.py, or run the project notebook first."
        )

    raw = pd.read_csv(raw_path, parse_dates=["date"])
    required = {"date", "active_power", "temp"}
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f"Raw CSV is missing required columns: {', '.join(sorted(missing))}")

    raw = (raw.drop_duplicates("date").sort_values("date")
              .dropna(subset=["date", "active_power"]).copy())
    raw["hour_ts"] = raw["date"].dt.floor("h")
    aggregations = {
        "readings": ("active_power", "size"),
        "avg_w": ("active_power", "mean"),
        "peak_w": ("active_power", "max"),
        "min_w": ("active_power", "min"),
        "temp": ("temp", "mean"),
    }
    optional = {
        "feels_like": "feels_like", "humidity": "humidity",
        "pressure": "pressure", "wind": "speed", "reactive_var": "reactive_power",
        "voltage": "voltage", "power_factor": "power_factor",
        "temp_max": "temp_max", "temp_min": "temp_min",
    }
    for output_col, raw_col in optional.items():
        if raw_col in raw.columns:
            aggregations[output_col] = (raw_col, "mean")
    if "main" in raw.columns:
        aggregations["condition"] = ("main", lambda x: x.mode().iat[0] if not x.mode().empty else "Unknown")

    h = raw.groupby("hour_ts").agg(**aggregations)
    full_index = pd.date_range(h.index.min(), h.index.max(), freq="h")
    h = h.reindex(full_index)
    h.index.name = "timestamp"
    # A valid hour requires at least 40 minute readings, matching the notebook.
    h["kwh"] = np.where(h["readings"] >= 40, h["avg_w"] / 1000.0, np.nan)
    h["hour"] = h.index.hour
    h["dow"] = h.index.dayofweek
    h["month"] = h.index.month
    h["is_weekend"] = (h["dow"] >= 5).astype(int)
    h["season"] = h["month"].map(SEASON)

    h["date_key"] = h.index.floor("D")
    daily_agg = {
        "kwh": ("kwh", "sum"), "valid_hours": ("kwh", "count"),
        "temp": ("temp", "mean"), "peak_w": ("peak_w", "max")
    }
    for col in ["temp_max", "temp_min", "humidity", "wind"]:
        if col in h.columns:
            daily_agg[col] = (col, "mean")
    d = h.groupby("date_key").agg(**daily_agg)
    d = d[d["valid_hours"] == 24].drop(columns="valid_hours")
    d.index.name = "date"
    d["dow"] = d.index.dayofweek
    d["month"] = d.index.month
    d["season"] = d["month"].map(SEASON)
    return h, d, f"Raw dataset ({raw_path.name})"

try:
    hourly_all, daily_all, data_source = load_data()
except Exception as exc:
    st.error(f"Data loading problem: {exc}")
    st.stop()

if hourly_all.empty or "kwh" not in hourly_all:
    st.error("No usable hourly energy data was found.")
    st.stop()

# Standardize fields that can be absent in older output files.
for col, default in {"hour": hourly_all.index.hour, "dow": hourly_all.index.dayofweek,
                     "month": hourly_all.index.month,
                     "is_weekend": (hourly_all.index.dayofweek >= 5).astype(int)}.items():
    if col not in hourly_all.columns:
        hourly_all[col] = default
if "season" not in hourly_all.columns:
    hourly_all["season"] = hourly_all["month"].map(SEASON)
if "season" not in daily_all.columns:
    daily_all["season"] = daily_all.index.month.map(SEASON)
if "dow" not in daily_all.columns:
    daily_all["dow"] = daily_all.index.dayofweek
if "month" not in daily_all.columns:
    daily_all["month"] = daily_all.index.month

# ─────────────────────────────────────────────────────────────────────────────
# Chart and UI helpers
# ─────────────────────────────────────────────────────────────────────────────
def chart_style(fig, height=390):
    fig.update_layout(
        template="plotly_white", height=height,
        margin=dict(l=22, r=22, t=76, b=28),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, Arial, sans-serif", color=INK, size=14),
        title=dict(
            font=dict(family="Manrope, Arial, sans-serif", color=INK, size=19),
            x=0.02, xanchor="left", y=0.97
        ),
        legend=dict(
            orientation="h", y=1.08, x=0.02,
            bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans, Arial, sans-serif", size=13, color=INK)
        ),
        colorway=PALETTE,
        hoverlabel=dict(
            bgcolor="#302313", bordercolor="#302313",
            font=dict(family="DM Sans, Arial, sans-serif", size=13, color="#FFFFFF")
        ),
    )
    fig.update_xaxes(
        gridcolor=GRID, zerolinecolor=GRID,
        tickfont=dict(family="DM Sans, Arial, sans-serif", size=12, color="#604B32"),
        title_font=dict(family="DM Sans, Arial, sans-serif", size=13, color=INK)
    )
    fig.update_yaxes(
        gridcolor=GRID, zerolinecolor=GRID,
        tickfont=dict(family="DM Sans, Arial, sans-serif", size=12, color="#604B32"),
        title_font=dict(family="DM Sans, Arial, sans-serif", size=13, color=INK)
    )
    return fig

def show_chart(fig, height=390):
    fig = chart_style(fig, height)

    # Donut charts need their own legend placement so the legend never overlaps
    # the chart title or the ring, and the Plotly canvas does not become scrollable.
    if fig.data and getattr(fig.data[0], "type", None) == "pie":
        fig.update_layout(
            height=max(height, 450),
            autosize=True,
            margin=dict(l=24, r=24, t=92, b=82),
            legend=dict(
                orientation="h",
                x=0.5, xanchor="center",
                y=-0.08, yanchor="top",
                entrywidth=120, entrywidthmode="pixels",
                bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans, Arial, sans-serif", size=14, color=INK)
            ),
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            textfont=dict(family="DM Sans, Arial, sans-serif", size=14, color="#FFFFFF"),
            hovertemplate="<b>%{label}</b><br>%{value:,.1f} kWh<br>%{percent}<extra></extra>",
            sort=False,
            hole=0.60,
            marker=dict(line=dict(color="#FFF9F0", width=3))
        )

    with st.container(border=True):
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "displayModeBar": False,
                "responsive": True,
                "scrollZoom": False
            }
        )

def kpi_card(label, value, help_text=""):
    st.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-help">{help_text}</div></div>',
        unsafe_allow_html=True
    )

def section(title, note=None):
    st.markdown(
        f'<div class="section-heading"><span class="section-dot"></span>'
        f'<span class="section-title">{title}</span></div>',
        unsafe_allow_html=True
    )
    if note:
        st.markdown(f'<div class="section-note">{note}</div>', unsafe_allow_html=True)

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    except Exception:
        return None

def load_optional_csv(path, **kwargs):
    try:
        return pd.read_csv(path, **kwargs) if path.exists() else None
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar controls
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ☀️ WattWise")
    st.markdown("**CONTROL CENTER**")
    st.caption("Personalize the analytics view using the filters below.")
    min_date = hourly_all.index.min().date()
    max_date = hourly_all.index.max().date()
    selected_dates = st.date_input("Analysis period", value=(min_date, max_date),
                                   min_value=min_date, max_value=max_date)
    day_options = [
        "All days", "Weekdays (Mon–Fri)", "Weekends (Sat–Sun)",
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ]
    day_filter = st.selectbox(
        "Day type",
        day_options,
        index=0,
        help="Choose all dates, working days, weekends, or one specific day of the week."
    )
    season_filter = st.multiselect("Season", ["Winter", "Spring", "Summer", "Autumn"],
                                   default=["Winter", "Spring", "Summer", "Autumn"])
    tariff = st.number_input("Assumed tariff (per kWh)", min_value=0.0, max_value=100.0,
                             value=0.12, step=0.01,
                             help="Illustrative only. The dataset does not contain electricity prices.")
    st.divider()
    st.caption("DATA SOURCE")
    st.caption(data_source)
    st.caption(f"{min_date}  →  {max_date}")

    st.divider()
    st.markdown("**RUN & DEPLOY**")
    with st.expander("Launch WattWise", expanded=False):
        st.markdown(
            '<div class="run-deploy-card">'
            '<div class="run-deploy-title">Run on your computer</div>'
            'Open a terminal in the project folder and run:'
            '<code>streamlit run app.py</code>'
            '<div class="run-deploy-title">Deploy online</div>'
            '1. Push the project folder to GitHub.<br>'
            '2. Open Streamlit Community Cloud.<br>'
            '3. Select your repository and choose <b>app.py</b> as the main file.<br>'
            '4. Add the packages from <b>requirements.txt</b> and deploy.'
            '</div>',
            unsafe_allow_html=True
        )

if not isinstance(selected_dates, (tuple, list)) or len(selected_dates) != 2:
    st.info("Select both a start date and an end date in the sidebar.")
    st.stop()

start = pd.Timestamp(selected_dates[0])
end = pd.Timestamp(selected_dates[1]) + pd.Timedelta(days=1)

def filter_frame(frame):
    out = frame[(frame.index >= start) & (frame.index < end)].copy()
    if day_filter in ("Weekdays", "Weekdays (Mon–Fri)"):
        out = out[out["dow"] < 5]
    elif day_filter in ("Weekends", "Weekends (Sat–Sun)"):
        out = out[out["dow"] >= 5]
    elif day_filter in ("Monday", "Tuesday", "Wednesday", "Thursday",
                        "Friday", "Saturday", "Sunday"):
        day_number = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
            "Friday": 4, "Saturday": 5, "Sunday": 6
        }[day_filter]
        out = out[out["dow"] == day_number]
    if "season" in out.columns:
        out = out[out["season"].isin(season_filter)]
    return out

H = filter_frame(hourly_all)
D = filter_frame(daily_all)
valid = H["kwh"].dropna()
if valid.empty:
    st.warning("No valid readings match these filters. Widen the date range or select more seasons.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="hero"><div><div class="brand">Watt<span>Wise</span></div>'
    f'<div class="tagline">{TAGLINE}</div>'
    f'<div class="tagline">Understand your energy. Predict demand. Make smarter decisions.</div>'
    f'<div class="hero-chip">✦ ENERGY INTELLIGENCE &nbsp; · &nbsp; LIVE ANALYTICS DASHBOARD &nbsp; · &nbsp; READY TO DEPLOY</div></div>'
    f'<div class="hero-mark">☀️⚡</div></div>', unsafe_allow_html=True
)

st.markdown(
    '<div style="color:#80613A;font-size:.92rem;font-weight:700;letter-spacing:.02em;margin:.25rem 0 .8rem;">'
    'WATTWISE WORKSPACE  /  SELECT AN ANALYTICS SECTION</div>',
    unsafe_allow_html=True
)
tabs = st.tabs(["🏠 Overview", "📈 Consumption", "🌦️ Weather", "⚡ Peak & Savings", "🤖 ML Insights"])

# ─────────────────────────────────────────────────────────────────────────────
# 1. Overview — executive summary only
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    st.caption(f"Showing {selected_dates[0]} to {selected_dates[1]} · {day_filter.lower()} · {len(season_filter)} seasons")
    avg_day = D["kwh"].mean() if not D.empty else np.nan
    hour_profile = H.groupby("hour")["kwh"].mean()
    peak_hour = int(hour_profile.idxmax()) if not hour_profile.empty else 0
    top_hour = valid.idxmax()
    temp_corr = D[["kwh", "temp"]].corr().iloc[0, 1] if len(D) > 2 and "temp" in D else np.nan

    cols = st.columns(4)
    with cols[0]: kpi_card("TOTAL CONSUMPTION", f"{valid.sum():,.1f} kWh", f"{len(valid):,} valid hours")
    with cols[1]: kpi_card("AVERAGE DAILY USE", f"{avg_day:,.1f} kWh" if pd.notna(avg_day) else "—", "Complete days in selection")
    with cols[2]: kpi_card("PEAK TIME OF DAY", f"{peak_hour:02d}:00", f"{hour_profile.max():.2f} kWh average")
    with cols[3]: kpi_card("HIGHEST HOUR", f"{valid.max():.2f} kWh", top_hour.strftime("%d %b %Y, %H:%M"))

    st.write("")
    left, right = st.columns([1.7, 1])
    with left:
        section("Consumption at a glance", "Daily electricity use with a 14-day moving average.")
        daily_plot = D.dropna(subset=["kwh"]).copy()
        daily_plot["rolling"] = daily_plot["kwh"].rolling(14, min_periods=3).mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_plot.index, y=daily_plot["kwh"], name="Daily use",
                                 mode="lines", line=dict(color=AMBER, width=1.2),
                                 fill="tozeroy", fillcolor="rgba(245,158,11,.13)"))
        fig.add_trace(go.Scatter(x=daily_plot.index, y=daily_plot["rolling"], name="14-day average",
                                 line=dict(color=ORANGE, width=3)))
        fig.update_layout(title="Daily electricity consumption", xaxis_title="", yaxis_title="kWh per day")
        show_chart(fig, 390)
    with right:
        section("When energy is used")
        bands = pd.cut(H["hour"], [-1, 5, 11, 17, 23],
                       labels=["Night", "Morning", "Afternoon", "Evening"])
        by_period = H.groupby(bands, observed=True)["kwh"].sum().dropna()
        fig = px.pie(values=by_period.values, names=by_period.index.astype(str),
                     hole=.60, title="Consumption by time of day",
                     color_discrete_sequence=[BLUE, AMBER, OLIVE, ORANGE])
        fig.update_traces(textposition="inside", textinfo="percent")
        show_chart(fig, 470)

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("TEMPERATURE RELATION", f"{temp_corr:+.2f}" if pd.notna(temp_corr) else "—",
                 "Correlation with daily kWh")
    with c2:
        peak_share = valid.nlargest(max(1, int(np.ceil(len(valid) * .10)))).sum() / valid.sum()
        kpi_card("TOP 10% HOURS", f"{peak_share*100:.1f}%", "Share of total energy used")
    with c3:
        kpi_card("ESTIMATED COST", f"{valid.sum()*tariff:,.2f}",
                 f"At assumed tariff {tariff:.2f} per kWh")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Consumption — hourly, weekday/weekend and monthly patterns
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    section("Hourly and daily demand", "Understand how electricity consumption changes through the day and across the selected period.")
    c1, c2 = st.columns(2)
    with c1:
        profile = H.groupby(["is_weekend", "hour"])["kwh"].mean().reset_index()
        fig = go.Figure()
        for flag, label, color in [(0, "Weekday", ORANGE), (1, "Weekend", AMBER)]:
            g = profile[profile["is_weekend"] == flag]
            if not g.empty:
                fig.add_trace(go.Scatter(x=g["hour"], y=g["kwh"], name=label,
                                         mode="lines+markers", line=dict(color=color, width=2.8)))
        fig.update_layout(title="Average hourly usage: weekday vs weekend",
                          xaxis_title="Hour of day", yaxis_title="kWh per hour")
        show_chart(fig)
    with c2:
        heat = H.pivot_table(index="dow", columns="hour", values="kwh", aggfunc="mean")
        heat = heat.reindex(index=range(7), columns=range(24))
        heat.index = DOW
        fig = px.imshow(heat, aspect="auto", color_continuous_scale="YlOrBr",
                        title="Weekly usage heatmap",
                        labels={"x":"Hour of day", "y":"Day", "color":"kWh"})
        show_chart(fig)

    section("Monthly consumption pattern", "Bars show average daily consumption, so months with different numbers of days can be compared fairly.")
    monthly = D.groupby(D.index.to_period("M")).agg(
        avg_daily_kwh=("kwh", "mean"), total_kwh=("kwh", "sum"),
        avg_temp=("temp", "mean"), days=("kwh", "count")
    )
    monthly.index = monthly.index.astype(str)
    if monthly.empty:
        st.info("There is not enough complete daily data for a monthly comparison.")
    else:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly.index, y=monthly["avg_daily_kwh"], name="Average daily kWh",
                             marker_color=AMBER))
        fig.add_trace(go.Scatter(x=monthly.index, y=monthly["avg_temp"], name="Average temperature",
                                 yaxis="y2", mode="lines+markers", line=dict(color=ORANGE, width=2.5)))
        fig.update_layout(title="Monthly energy use and temperature",
                          yaxis=dict(title="Average kWh per day"),
                          yaxis2=dict(title="Temperature (°C)", overlaying="y", side="right", showgrid=False))
        show_chart(fig, 410)
        with st.container(border=True):
            st.markdown("**Monthly summary**")
            st.dataframe(monthly.rename(columns={"avg_daily_kwh":"Avg kWh/day",
                         "total_kwh":"Total kWh", "avg_temp":"Avg temperature °C",
                         "days":"Complete days"}).round(2), use_container_width=True)

    resolution = st.selectbox("Explore consumption by resolution",
                              ["Hourly", "Daily", "Weekly", "Monthly"], index=1)
    rule = {"Hourly":"h", "Daily":"D", "Weekly":"W", "Monthly":"MS"}[resolution]
    series = H["kwh"].resample(rule).sum(min_count=1).dropna()
    fig = px.area(x=series.index, y=series.values, title=f"{resolution} energy consumption",
                  labels={"x":"Date", "y":"Total kWh"})
    fig.update_traces(line_color=ORANGE, fillcolor="rgba(245,158,11,.16)")
    show_chart(fig, 340)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Weather — weather relationship, no repeated trend charts
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    section("Weather and electricity relationship",
            "Explore whether hotter, colder or more humid conditions are associated with higher energy demand.")
    if "temp" not in D.columns or D["temp"].dropna().empty:
        st.info("Temperature data is not available in the selected dataset.")
    else:
        left, right = st.columns([1.5, 1])
        with left:
            scatter_data = D.dropna(subset=["temp", "kwh"]).reset_index()
            color_col = "season" if "season" in scatter_data.columns else None
            fig = px.scatter(scatter_data, x="temp", y="kwh", color=color_col,
                             color_discrete_sequence=PALETTE,
                             title="Daily energy use vs mean temperature",
                             labels={"temp":"Mean temperature (°C)", "kwh":"Daily energy (kWh)"})
            fig.update_traces(marker=dict(size=7, opacity=.65))
            show_chart(fig, 420)
        with right:
            corr_cols = {"temp":"Temperature", "feels_like":"Feels like",
                         "humidity":"Humidity", "pressure":"Pressure", "wind":"Wind speed"}
            corr_values = {}
            for col, label in corr_cols.items():
                if col in H.columns and H[col].notna().sum() > 2:
                    corr_values[label] = H["kwh"].corr(H[col])
            if corr_values:
                corr = pd.Series(corr_values).dropna().sort_values()
                fig = px.bar(x=corr.values, y=corr.index, orientation="h",
                             title="Weather correlation with hourly use",
                             labels={"x":"Correlation", "y":""},
                             color=corr.values, color_continuous_scale=["#5B8DB0", "#FFF8EC", "#EA580C"])
                fig.update_layout(coloraxis_showscale=False, xaxis=dict(range=[-1, 1]))
                show_chart(fig, 420)
            else:
                st.info("Not enough weather variables are available for correlation analysis.")

    if "temp" in H.columns:
        temp_band = H.dropna(subset=["temp", "kwh"]).copy()
        temp_band["Temperature range"] = pd.cut(temp_band["temp"],
            [-10, 5, 10, 15, 20, 25, 30, 45],
            labels=["<5°C", "5–10°C", "10–15°C", "15–20°C", "20–25°C", "25–30°C", ">30°C"])
        band_summary = temp_band.groupby("Temperature range", observed=True)["kwh"].agg(["mean", "count"]).reset_index()
        fig = px.bar(band_summary, x="Temperature range", y="mean",
                     title="Average hourly consumption by temperature range",
                     labels={"mean":"Average kWh per hour", "Temperature range":"Temperature"},
                     color="mean", color_continuous_scale="YlOrBr")
        fig.update_layout(coloraxis_showscale=False)
        show_chart(fig, 360)

    # Simple interpretable cooling sensitivity model, matching notebook method.
    if len(D.dropna(subset=["temp", "kwh"])) >= 10:
        fit = D.dropna(subset=["temp", "kwh"])
        y = fit["kwh"].to_numpy()
        best = None
        for threshold in np.arange(10, 27.1, .5):
            x = np.maximum(fit["temp"].to_numpy() - threshold, 0)
            A = np.column_stack([np.ones(len(x)), x])
            coef = np.linalg.lstsq(A, y, rcond=None)[0]
            err = np.sum((y - A @ coef) ** 2)
            if best is None or err < best[0]:
                best = (err, threshold, coef)
        _, threshold, coef = best
        st.markdown(
            f'<div class="insight"><b>Temperature sensitivity estimate</b><br>'
            f'Estimated baseline: <b>{coef[0]:.2f} kWh/day</b>. '
            f'Above approximately <b>{threshold:.1f} °C</b>, the fitted relationship adds '
            f'<b>{coef[1]:.2f} kWh/day per °C</b>. This is an association, not proof of causation.</div>',
            unsafe_allow_html=True
        )

# ─────────────────────────────────────────────────────────────────────────────
# 4. Peaks and energy-saving insights
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    section("Peak consumption analysis", "Identify high-demand hours and the times when shifting flexible loads may help.")
    peak_pct = st.slider("Define peak hours as the highest percentage of readings", 1, 30, 10)
    threshold = valid.quantile(1 - peak_pct / 100)
    peaks = H[H["kwh"] >= threshold].copy()
    peak_share = peaks["kwh"].sum() / valid.sum()
    peak_by_hour = peaks.groupby("hour").size().reindex(range(24), fill_value=0)
    quiet = H.groupby("hour")["kwh"].mean().nsmallest(4).index.tolist()
    busy = H.groupby("hour")["kwh"].mean().nlargest(4).index.tolist()

    c = st.columns(4)
    with c[0]: kpi_card("PEAK THRESHOLD", f"{threshold:.2f} kWh", f"Top {peak_pct}% of valid hours")
    with c[1]: kpi_card("PEAK HOURS", f"{len(peaks):,}", f"{peak_share*100:.1f}% of energy")
    with c[2]: kpi_card("MOST COMMON PEAK", f"{int(peak_by_hour.idxmax()):02d}:00", "Hour of day")
    with c[3]: kpi_card("HIGHEST DEMAND", f"{valid.max():.2f} kWh", "Maximum hourly energy")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(x=peak_by_hour.index, y=peak_by_hour.values,
                     title="How peak hours are distributed",
                     labels={"x":"Hour of day", "y":"Number of peak hours"},
                     color=peak_by_hour.values, color_continuous_scale="YlOrBr")
        fig.update_layout(coloraxis_showscale=False)
        show_chart(fig, 350)
    with c2:
        top_days = D.nlargest(10, "kwh").reset_index()
        fig = px.bar(top_days, x="kwh", y=top_days.columns[0], orientation="h",
                     title="10 highest-consumption days",
                     labels={"kwh":"Daily energy (kWh)", top_days.columns[0]:"Date"},
                     color="kwh", color_continuous_scale="YlOrBr")
        fig.update_layout(yaxis={"categoryorder":"total ascending"}, coloraxis_showscale=False)
        show_chart(fig, 350)

    section("Practical energy-saving suggestions")
    st.markdown(
        f'<div class="insight"><b>Shift flexible appliances</b><br>'
        f'Your lowest average-load hours are {", ".join(f"{x:02d}:00" for x in sorted(quiet))}. '
        f'Consider running washing machines, dishwashers or EV charging during suitable low-demand periods.</div>'
        f'<div class="insight"><b>Reduce peak stacking</b><br>'
        f'Your highest average-load hours are {", ".join(f"{x:02d}:00" for x in sorted(busy))}. '
        f'Avoid running several high-power appliances at the same time where practical.</div>'
        f'<div class="insight"><b>Review cooling settings</b><br>'
        f'Compare energy use on hotter days and use efficient cooling settings, clean filters and appropriate thermostat settings.</div>',
        unsafe_allow_html=True
    )

    section("Savings scenario calculator", "Illustrative scenarios only. Change the percentages to estimate possible annual impact.")
    annualized = D["kwh"].mean() * 365 if not D.empty else 0
    base_w = float(H["avg_w"].quantile(.05)) if "avg_w" in H.columns else float(H["kwh"].quantile(.05) * 1000)
    base_annual = base_w * 8760 / 1000
    cooling_share = 0.0
    cooling_fit = D.dropna(subset=["temp", "kwh"]) if "temp" in D.columns else pd.DataFrame()
    if len(cooling_fit) >= 10:
        y_cool = cooling_fit["kwh"].to_numpy()
        best_cool = None
        for t0_cool in np.arange(10, 27.1, .5):
            excess_temp = np.maximum(cooling_fit["temp"].to_numpy() - t0_cool, 0)
            design = np.column_stack([np.ones(len(excess_temp)), excess_temp])
            coef_cool = np.linalg.lstsq(design, y_cool, rcond=None)[0]
            sse_cool = np.sum((y_cool - design @ coef_cool) ** 2)
            if best_cool is None or sse_cool < best_cool[0]:
                best_cool = (sse_cool, t0_cool, coef_cool)
        _, t0_cool, coef_cool = best_cool
        cooling_component = coef_cool[1] * np.maximum(cooling_fit["temp"].to_numpy() - t0_cool, 0)
        cooling_share = float(np.clip(cooling_component.sum() / max(cooling_fit["kwh"].sum(), 1e-9), 0, .8))
    peak_annual = annualized * peak_share
    s1, s2, s3 = st.columns(3)
    cooling_pct = s1.slider("Reduce cooling-related use (%)", 0, 50, 10)
    base_pct = s2.slider("Reduce always-on load (%)", 0, 50, 20)
    shift_pct = s3.slider("Shift peak energy (%)", 0, 50, 15)
    saved_cooling = annualized * cooling_share * cooling_pct / 100
    saved_base = base_annual * base_pct / 100
    shifted = peak_annual * shift_pct / 100
    result = pd.DataFrame({
        "Action":["Cooling reduction", "Always-on load reduction", "Peak load shifted"],
        "Estimated kWh/year":[saved_cooling, saved_base, shifted],
        "Impact":["Potentially saved", "Potentially saved", "Shifted, not saved"]
    })
    fig = px.bar(result, x="Estimated kWh/year", y="Action", orientation="h",
                 color="Impact", title="Estimated annual energy impact",
                 color_discrete_map={"Potentially saved":ORANGE, "Shifted, not saved":AMBER},
                 text=result["Estimated kWh/year"].map(lambda x:f"{x:,.0f}"))
    show_chart(fig, 330)
    st.caption(f"Potential reduction estimate: {saved_cooling+saved_base:,.1f} kWh/year. "
               f"Peak shifting is shown separately because moving usage does not itself reduce energy consumption.")
    st.caption(f"At the assumed tariff, potential reduction value is approximately "
               f"{(saved_cooling+saved_base)*tariff:,.2f} per year. All scenario values are estimates, not measured savings.")

# ─────────────────────────────────────────────────────────────────────────────
# 5. ML insights — keep forecast and current-hour estimate distinct
# ─────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    section("Machine-learning energy estimation",
            "The notebook evaluates two different prediction tasks. Their scores should not be compared as if they were the same task.")
    metadata = load_json(MODEL_DIR / "model_metadata.json") or load_json(OUTPUT / "model_metadata.json")
    forecast = load_optional_csv(DASH / "forecast_test_predictions.csv", parse_dates=["timestamp"])
    live = load_optional_csv(DASH / "live_estimate_test_predictions.csv", parse_dates=["timestamp"])
    leaderboard_a = load_optional_csv(DASH / "model_leaderboard_forecast.csv")
    leaderboard_b = load_optional_csv(DASH / "model_leaderboard_live_estimate.csv")

    if metadata:
        task_a = metadata.get("task_A_next_hour_forecast", {})
        task_b = metadata.get("task_B_live_estimate", {})
        a1, a2 = st.columns(2)
        with a1:
            st.markdown("#### A · Next-hour forecast")
            st.metric("Test R²", f"{task_a.get('test_r2', float('nan')):.3f}" if task_a else "Not available")
            st.caption(f"MAE: {task_a.get('test_mae_kwh', float('nan')):.3f} kWh" if task_a else "Forecast metrics not found.")
            st.info("Predicts energy demand for the following hour using information available before that hour.")
        with a2:
            st.markdown("#### B · Live current-hour estimate")
            st.metric("Test R²", f"{task_b.get('test_r2', float('nan')):.3f}" if task_b else "Not available")
            if task_b:
                st.caption(f"MAE: {task_b.get('test_mae_kwh', float('nan')):.3f} kWh · estimate after minute {task_b.get('cutoff_minute', '—')}")
            st.info("Estimates the current hour after observing part of that hour. It is not a next-hour forecast.")
    else:
        st.info("ML evaluation files are not present yet. Run all notebook cells to generate model metadata and held-out test predictions.")

    if forecast is not None and {"timestamp", "actual_next_hour_kwh", "forecast_kwh"}.issubset(forecast.columns):
        section("Next-hour forecast: actual vs predicted")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=forecast["timestamp"], y=forecast["actual_next_hour_kwh"],
                                 name="Actual", line=dict(color=INK, width=1.8)))
        fig.add_trace(go.Scatter(x=forecast["timestamp"], y=forecast["forecast_kwh"],
                                 name="Forecast", line=dict(color=ORANGE, width=1.8, dash="dash")))
        fig.update_layout(title="Held-out test period", xaxis_title="", yaxis_title="kWh per hour")
        show_chart(fig, 360)

    if live is not None and {"timestamp", "actual_kwh", "estimated_kwh"}.issubset(live.columns):
        section("Live estimate: actual vs estimated")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=live["timestamp"], y=live["actual_kwh"],
                                 name="Actual", line=dict(color=INK, width=1.8)))
        fig.add_trace(go.Scatter(x=live["timestamp"], y=live["estimated_kwh"],
                                 name="Estimate", line=dict(color=TEAL, width=1.8, dash="dash")))
        fig.update_layout(title="Held-out test period", xaxis_title="", yaxis_title="kWh per hour")
        show_chart(fig, 360)

    if leaderboard_a is not None:
        with st.expander("View next-hour model comparison"):
            st.dataframe(leaderboard_a, use_container_width=True, hide_index=True)
    if leaderboard_b is not None:
        with st.expander("View live-estimation model comparison"):
            st.dataframe(leaderboard_b, use_container_width=True, hide_index=True)

    if not metadata and forecast is None and live is None:
        st.markdown(
            '<div class="insight"><b>How to enable ML results</b><br>'
            'Run the complete energy_analytics_dashboard_notebook.ipynb first. '
            'Keep the generated outputs/dashboard_data and models folders beside app.py.</div>',
            unsafe_allow_html=True
        )

st.markdown(
    f'<div class="footer">⚡ {APP_NAME} · {TAGLINE}<br>'
    'Electricity costs use an assumed tariff · Savings scenarios are illustrative · '
    'ML metrics are reported from held-out notebook test data</div>',
    unsafe_allow_html=True
)