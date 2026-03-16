import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import networkx as nx
from sklearn.linear_model import LinearRegression
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


st.set_page_config(page_title="University Research Analytics", page_icon="📚",
                   layout="wide", initial_sidebar_state="expanded")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&family=DM+Mono:wght@300;400;600&display=swap');

html, body, [class*="css"] { background-color: #0a0c10; color: #e8eaf0; }
h1, h2, h3 { font-family: 'Bebas Neue', mono-serif; letter-spacing: 0.05em; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background-color: #111418 !important; border-right: 1px solid #232836; }
[data-testid="stSidebar"] * { color: #e8eaf0 !important; }
[data-testid="stSidebar"] label { color: #e8eaf0 !important; }
[data-testid="stSidebar"] label p { color: #e8eaf0 !important; }
[data-testid="stSidebar"] label span { color: #e8eaf0 !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] { color: #e8eaf0 !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] * { color: #e8eaf0 !important; }

/* ── Dropdowns / select ── */
[data-baseweb="select"] * { color: #e8eaf0 !important; }
[data-baseweb="select"] [data-baseweb="tag"] { background: #232836 !important; }
[data-baseweb="select"] [data-baseweb="tag"] span { color: #e8ff47 !important; }
[data-baseweb="menu"] { background-color: #111418 !important; }
[data-baseweb="option"] { background-color: #e8eaf0 !important; color: #0a0c10 !important; }
[data-baseweb="option"]:hover { background-color: #e8ff47 !important; }
[data-baseweb="option"] span { color: #0a0c10 !important; }
[data-baseweb="popover"] { background-color: #e8eaf0 !important; }
[data-baseweb="popover"] * { color: #0a0c10 !important; }
ul[role="listbox"] { background-color: #e8eaf0 !important; }
ul[role="listbox"] li, ul[role="listbox"] li span { color: #0a0c10 !important; }
[data-baseweb="select"] div[aria-haspopup="listbox"] { background-color: #111418 !important; }
[data-baseweb="select"] div { color: #e8eaf0 !important; }
[data-baseweb="select"] input { color: #e8eaf0 !important; background-color: #111418 !important; }
[data-baseweb="select"] input::placeholder { color: #6b7385 !important; }

[data-testid="stSidebar"] .stCheckbox label p {
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: #e8eaf0 !important;
}
/* ── Widget labels (Rank by, Publications, Citations и т.д.) ── */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] span,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stMultiSelect label {
    color: #e8eaf0 !important;
}

/* ── Slider ── */
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"],
[data-testid="stThumbValue"] { color: #e8eaf0 !important; }

[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: none !important;
    color: #6b7385 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 2px 0 !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    color: #e8ff47 !important;
    background: transparent !important;
}
/* ── Radio (sidebar only) ── */
[data-testid="stSidebar"] .stRadio label p {
    color: #e8eaf0 !important;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    color: #e8eaf0 !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    color: #e8eaf0 !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {
    color: #e8eaf0 !important;
}

/* ── Text input ── */
.stTextInput input {
    background-color: #111418 !important; color: #e8eaf0 !important;
    border: 1px solid #232836 !important; border-radius: 4px !important;
    font-size: 14px !important;
}
.stTextInput input:focus { border-color: #e8ff47 !important; box-shadow: none !important; }
.stTextInput input::placeholder { color: #6b7385 !important; }

[data-testid="stMain"] [data-baseweb="select"] > div {
    background-color: #111418 !important;
    border: 1px solid #232836 !important;
    border-radius: 4px !important;
}
[data-testid="stMain"] [data-baseweb="select"] > div:focus-within {
    border-color: #e8ff47 !important;
}
/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #0a0c10 !important; border-bottom: 1px solid #232836 !important; gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background-color: #111418 !important; color: #0a0c10 !important;
    border: 1px solid #232836 !important; border-radius: 2px 2px 0 0 !important;
    font-family: 'DM Mono', monospace !important; font-size: 10px !important;
    letter-spacing: 0.15em !important; text-transform: uppercase !important; padding: 8px 20px !important;
}
.stTabs [data-baseweb="tab"] span,
.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] div {
    color: #0a0c10 !important;
}
.stTabs [aria-selected="true"] {
    background-color: #232836 !important; color: #e8ff47 !important; border-bottom-color: #232836 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 24px !important; }

/* ── Sidebar filter section ── */
.filter-section {
    margin-bottom: 4px;
}
.filter-header {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #0a0c10;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid #1e2230;
}
.filter-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0;
    cursor: pointer;
    border-radius: 2px;
    font-size: 12px;
    color: #c8cad4;
    transition: color 0.15s;
}
.filter-item:hover { color: #e8ff47; }
.filter-item.active { color: #e8ff47; font-weight: 600; }
.filter-count {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #6b7385;
    background: #1a1e28;
    padding: 1px 6px;
    border-radius: 10px;
    min-width: 28px;
    text-align: center;
}
.show-more {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: #6b7385;
    letter-spacing: 0.1em;
    cursor: pointer;
    padding: 4px 0;
    text-transform: uppercase;
}
.show-more:hover { color: #e8ff47; }
/* __ Download buttons __ */
.stDownloadButton button {
    background-color: #111418 !important;
    color: #e8ff47 !important;
    border: 1px solid #e8ff47 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.1em !important;
    border-radius: 2px !important;
    padding: 6px 16px !important;
}
.stDownloadButton button:hover {
    background-color: #e8ff47 !important;
    color: #0a0c10 !important;
}
            
/* ── Metric cards ── */
.metric-card {
    background: #111418; border: 1px solid #232836;
    padding: 20px 24px; border-radius: 4px; text-align: center;
}
.metric-label {
    font-family: 'DM Mono', monospace; font-size: 10px;
    letter-spacing: 0.2em; text-transform: uppercase; color: #6b7385; margin-bottom: 6px;
}
.metric-value { font-family: 'Bebas Neue', sans-serif; font-size: 48px; line-height: 1; }
.metric-sub { font-family: 'DM Mono', sans-serif; font-size: 12px; color: #6b7385; margin-top: 4px; }

/* ── Section label ── */
.section-label {
    font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.25em;
    text-transform: uppercase; color: #6b7385;
    border-bottom: 1px solid #232836; padding-bottom: 8px; margin-bottom: 20px;
}

/* ── h-index box ── */
.hindex-box {
    background: #111418; border: 1px solid #232836; padding: 24px 28px;
    border-radius: 4px; text-align: center; position: relative; overflow: hidden;
}
.hindex-box::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 3px; height: 100%; background: var(--accent-color, #e8ff47);
}
.hindex-num { font-family: 'Bebas Neue', sans-serif; font-size: 64px; line-height: 1; }
.hindex-label { font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; color: #6b7385; margin-top: 4px; }
.hindex-sub { font-size: 12px; color: #6b7385; margin-top: 6px; }

/* ── Info pill ── */
.info-pill {
    display: inline-block; background: #111418; border: 1px solid #232836;
    padding: 4px 12px; border-radius: 20px;
    font-family: 'DM Mono', monospace; font-size: 11px; color: #9aa0b0; margin: 3px;
}

/* ── Keyword tag ── */
.kw-tag {
    display: inline-block;
    padding: 3px 9px;
    margin: 2px;
    border-radius: 2px;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.05em;
    background: #1a1e28;
    border: 1px solid #2a3045;
    color: #c8cad4;
}

/* ── Search result card ── */
.paper-row {
    background: #111418;
    border: 1px solid #232836;
    border-left: 3px solid #e8ff47;
    padding: 16px 20px;
    margin-bottom: 10px;
    border-radius: 0 4px 4px 0;
    transition: border-color 0.2s;
}
.paper-row:hover { border-left-color: #47c8ff; }
.paper-row-title { font-size: 14px; line-height: 1.5; color: #e8eaf0; margin-bottom: 6px; font-weight: 400; }
.paper-row-authors { font-size: 12px; color: #e8ff47; font-style: italic; margin-bottom: 5px; }
.paper-row-meta { font-family: 'DM Mono', monospace; font-size: 10px; color: #6b7385; }
.paper-row-citations { font-family: 'Bebas Neue', sans-serif; font-size: 42px; line-height: 1; text-align: right; }
.paper-row-cites-label { font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.1em; color: #6b7385; text-align: right; }
div[role="radiogroup"] {
    gap: 0.5rem;
}

div[role="radiogroup"] > label {
    padding: 0.55rem 1rem;
    border-radius: 999px;
    background: rgba(255,255,255,0.04);
    transition: 0.2s ease;
    color: #0a0c10 !important;
}

div[role="radiogroup"] > label p,
div[role="radiogroup"] > label span,
div[role="radiogroup"] > label div {
    color: #0a0c10 !important;
}

div[role="radiogroup"] > label:hover {
    background: rgba(255,255,255,0.08);
}

div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
    display: none;
}

/* ── Бордер на все radio label ── */
label[data-baseweb="radio"] {
    border: 1px solid #232836 !important;
    border-radius: 999px !important;
}
label[data-baseweb="radio"]:hover {
    border-color: #e8ff47 !important;
}
label[data-baseweb="radio"]:has(input:checked) {
    background: transparent !important;
    border-color: #ff4747 !important;
    border-width: 2px !important;
}
label[data-baseweb="radio"]:has(input:checked) p,
label[data-baseweb="radio"]:has(input:checked) span {
    color: #0a0c10 !important;
    font-weight: 600 !important;
}

/* ── Активный выбор — для всех radio ── */
div[role="radiogroup"] > label[aria-checked="true"] {
    background: #e8ff47 !important;
    border-color: #e8ff47 !important;
    color: #0a0c10 !important;
}
div[role="radiogroup"] > label[aria-checked="true"] p,
div[role="radiogroup"] > label[aria-checked="true"] span,
div[role="radiogroup"] > label[aria-checked="true"] div {
    color: #0a0c10 !important;
    font-weight: 600 !important;
}

/* ── Navigation radio (main content) ── */
[data-testid="stMain"] .stRadio div[role="radiogroup"] > label,
[data-testid="stMain"] .stRadio div[role="radiogroup"] > label p,
[data-testid="stMain"] .stRadio div[role="radiogroup"] > label span,
[data-testid="stMain"] .stRadio div[role="radiogroup"] > label div,
html body [data-testid="stMain"] .stRadio label p,
html body [data-testid="stMain"] .stRadio label span {
    color: #0a0c10 !important;
}
</style>
""", unsafe_allow_html=True)

# ── PLOTLY THEME ───────────────────────────────────────────────────────────────
THEME = dict(
    paper_bgcolor="#0a0c10", plot_bgcolor="#0a0c10",
    font=dict(family="DM Mono, monospace", color="#e8eaf0", size=11),
    margin=dict(t=20, b=40, l=10, r=10),
)
AXIS = dict(gridcolor="#1e2230", linecolor="#232836", tickcolor="#232836",
            tickfont=dict(color="#e8eaf0"), title_font=dict(color="#e8eaf0"),
            tickformat="d")
# Axis for categorical (string) labels — no tickformat to avoid "0 1 1" numeric rendering
AXIS_CAT = dict(gridcolor="#1e2230", linecolor="#232836", tickcolor="#232836",
                tickfont=dict(color="#e8eaf0"), title_font=dict(color="#e8eaf0"))
# Year axis — linear with integer ticks, no decimals
YEAR_AXIS = dict(gridcolor="#1e2230", linecolor="#232836", tickcolor="#232836",
                 tickfont=dict(color="#e8eaf0"), title_font=dict(color="#e8eaf0"),
                 tickmode="linear", dtick=1, tickformat="d")
# Year axis with every-5-year ticks and angled labels for dense charts
YEAR_AXIS_5 = dict(gridcolor="#1e2230", linecolor="#232836", tickcolor="#232836",
                   tickfont=dict(color="#e8eaf0"), title_font=dict(color="#e8eaf0"),
                   tickmode="linear", dtick=5, tickformat="d", tickangle=0)
COLORS = ["#e8ff47", "#47c8ff", "#ff6b47", "#a47fff", "#47ffb8",
          "#ff47a4", "#ffa447", "#4778ff", "#ff4747", "#47ffd4"]

# ── LOAD DATA ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("рез2.csv")
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "Год": "year", "Цитирования": "citations", "Тип документа": "doc_type",
        "Название документа": "title", "Название источника": "journal",
        "Автор (ы)": "authors", "Open Access (открытый доступ)": "open_access",
        "subject_area": "area", "DOI": "doi",
        "Ссылка": "scopus_link",
        "Организации": "affiliations",
        "Краткое описание": "abstract",
        "Ключевые слова автора": "keywords_author",
        "Ключевые слова указателя": "keywords_index",
        "Название конференции": "conference",
        "Сведения о финансировании": "funding",
        "Спонсоры": "sponsors",
    })
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # Parse "Author full names" → list of (lastname, firstname, scopus_id) tuples
    def parse_full_authors(s):
        import re as _re
        if pd.isna(s) or not str(s).strip():
            return []
        result = []
        for entry in str(s).split(";"):
            entry = entry.strip()
            id_match = _re.search(r'\((\d+)\)', entry)
            scopus_id = id_match.group(1) if id_match else None
            entry = _re.sub(r'\(\d+\)', '', entry).strip()
            if ',' in entry:
                parts = entry.split(',', 1)
                lastname  = parts[0].strip()
                firstname = parts[1].strip()
                if lastname and firstname:
                    result.append((lastname, firstname, scopus_id))
        return result

    if "Author full names" in df.columns:
        df["author_full_list"] = df["Author full names"].apply(parse_full_authors)
    else:
        df["author_full_list"] = [[] for _ in range(len(df))]

    # ── Новые колонки квартилей из result_final5.csv ──────────────────────────
    # quartile      = лучший квартиль (Q1/Q2/Q3/Q4) — для фильтров и бейджей
    # quartile_all  = все квартили через запятую: "Q1, Q2, Q3"
    # quartile_detail = детально: "Food Science: Q1 (91%); Chemistry: Q2 (68%)"
    # quartile_status = статус API для объяснения отсутствия квартиля

    if "Квартиль_лучший" in df.columns:
        df["quartile"] = df["Квартиль_лучший"].astype(str).str.strip()
        df["quartile"] = df["quartile"].replace({"nan": None, "": None, "None": None})
    elif "Quartile_final" in df.columns:
        df["quartile"] = df["Quartile_final"].astype(str).str.strip()
        df["quartile"] = df["quartile"].replace({"nan": None, "": None, "None": None})
    else:
        df["quartile"] = None

    df["quartile_all"] = df.get("Квартили_все", pd.Series(dtype=str)).astype(str).str.strip()
    df["quartile_all"] = df["quartile_all"].replace({"nan": None, "": None, "None": None})

    df["quartile_detail"] = df.get("Квартили_детально", pd.Series(dtype=str)).astype(str).str.strip()
    df["quartile_detail"] = df["quartile_detail"].replace({"nan": None, "": None, "None": None})

    df["quartile_status"] = df.get("API_Status", pd.Series(dtype=str)).astype(str).str.strip()
    df["quartile_status"] = df["quartile_status"].replace({"nan": None, "": None, "None": None})

    df["citations"] = pd.to_numeric(df["citations"], errors="coerce").fillna(0).astype(int)
    df["open_access_bool"] = df["open_access"].notna() & (df["open_access"].str.strip() != "")
    df["area_clean"] = df["area"].str.replace("_", " ").str.title() if "area" in df.columns else "Unknown"
    df["n_authors"] = df["authors"].apply(
        lambda x: len(str(x).split(";")) if pd.notna(x) and str(x).strip() else 0
    )
    # Extract first-level org unit from affiliations
    def first_unit(aff_str):
        if pd.isna(aff_str): return []
        units = []
        for part in str(aff_str).split(";"):
            part = part.strip()
            if part:
                units.append(part.split(",")[0].strip())
        return list(set(units))
    df["units"] = df["affiliations"].apply(first_unit)
    # Parse keywords
    def parse_kw(s):
        if pd.isna(s): return []
        return [k.strip() for k in str(s).split(";") if k.strip()]
    df["kw_list"] = df["keywords_author"].apply(parse_kw)
    # Parse full org names from affiliations
    def parse_orgs(aff_str):
        if pd.isna(aff_str): return []
        orgs = []
        for part in str(aff_str).split(";"):
            part = part.strip()
            if part:
                org = part.split(",")[0].strip()
                if org: orgs.append(org)
        return list(set(orgs))
    df["org_list"] = df["affiliations"].apply(parse_orgs)
    # Parse funders
    def parse_funders(s):
        if pd.isna(s): return []
        return [p.strip().split(",")[0].strip() for p in str(s).split(";") if p.strip() and len(p.strip()) > 3]
    df["funder_list"] = df["funding"].apply(parse_funders)
    return df

df = load_data()

# ── PRECOMPUTE FILTER COUNTS ───────────────────────────────────────────────────
year_counts = df.groupby("year").size().sort_index(ascending=False)
all_years = year_counts.index.tolist()

author_counter = Counter()
for v in df["authors"].dropna():
    for a in str(v).split(";"):
        author_counter[a.strip()] += 1

unit_counter = Counter()
for units in df["units"]:
    for u in units:
        if u:
            unit_counter[u] += 1

org_counter = Counter()
for orgs in df["org_list"]:
    for o in orgs:
        if o:
            org_counter[o] += 1

conf_counter = df["conference"].dropna().value_counts()
all_confs = conf_counter.index.tolist()

funder_counter = Counter()
for fl in df["funder_list"]:
    for f in fl:
        if f:
            funder_counter[f] += 1

# ── HELPERS ────────────────────────────────────────────────────────────────────
def detect_role_in_team(G_full, ego_author):
    """
    Heuristic role detection for co-authorship networks.
    Uses:
      - degree (number of co-authors)
      - weighted degree (sum of edge weights)
      - clustering coefficient (are my co-authors connected to each other?)
      - local betweenness (computed on radius=2 ego graph, using distance=1/weight)
    Returns: (role, explanation, metrics_dict)
    """
    if ego_author not in G_full:
        return "Unknown", "Author not found in graph.", {}

    deg0 = int(G_full.degree(ego_author))
    wdeg0 = float(G_full.degree(ego_author, weight="weight"))

    # clustering: high => author sits in a tight team; low => hub-and-spoke
    try:
        clust0 = float(nx.clustering(G_full, ego_author, weight="weight"))
    except TypeError:
        clust0 = float(nx.clustering(G_full, ego_author))

    # local betweenness on radius=2 subgraph (fast, still meaningful)
    G2 = nx.ego_graph(G_full, ego_author, radius=2)
    for u, v, d in G2.edges(data=True):
        w = d.get("weight", 1) or 1
        d["distance"] = 1.0 / w

    btw_local = nx.betweenness_centrality(G2, weight="distance", normalized=True).get(ego_author, 0.0)

    # percentiles (context) computed on full graph degrees (fast enough)
    deg_series = pd.Series([G_full.degree(n) for n in G_full.nodes()])
    wdeg_series = pd.Series([G_full.degree(n, weight="weight") for n in G_full.nodes()])

    deg_p90 = float(deg_series.quantile(0.90)) if len(deg_series) else 0
    deg_p50 = float(deg_series.quantile(0.50)) if len(deg_series) else 0
    wdeg_p50 = float(wdeg_series.quantile(0.50)) if len(wdeg_series) else 0

    # neighbor community diversity (local): if ego connects multiple local groups
    neighbor_groups = 1
    if G2.number_of_nodes() >= 5 and G2.number_of_edges() >= 4:
        comms = list(nx.algorithms.community.greedy_modularity_communities(G2, weight="weight"))
        node_group = {}
        for i, c in enumerate(comms):
            for n in c:
                node_group[n] = i
        neigh = [n for n in G_full.neighbors(ego_author)]
        groups = set(node_group.get(n, None) for n in neigh if n in node_group)
        groups.discard(None)
        neighbor_groups = max(1, len(groups))

    # ── Role rules (simple + interpretable) ───────────────────────────────
    if deg0 <= 1:
        role = "Peripheral collaborator"
        why = "Few direct co-authors (degree ≤ 1)."
    elif btw_local >= 0.12 and neighbor_groups >= 2:
        role = "Bridge / broker"
        why = f"High local betweenness ({btw_local:.3f}) and links across {neighbor_groups} local groups."
    elif deg0 >= deg_p90 and clust0 <= 0.25:
        role = "Hub / coordinator"
        why = f"Very high degree (≥ P90 ~ {deg_p90:.0f}) with low clustering ({clust0:.2f}) → hub-and-spoke."
    elif clust0 >= 0.55 and wdeg0 >= wdeg_p50:
        role = "Core team member"
        why = f"High clustering ({clust0:.2f}) + solid collaboration strength (≥ median)."
    elif deg0 >= deg_p50:
        role = "Active collaborator"
        why = f"Above-median degree (≥ P50 ~ {deg_p50:.0f})."
    else:
        role = "Contributor"
        why = "Moderate connectivity; not a hub or bridge under current thresholds."

    metrics = dict(
        degree=deg0,
        weighted_degree=round(wdeg0, 1),
        clustering=round(clust0, 3),
        betweenness_local=round(float(btw_local), 4),
        neighbor_groups=int(neighbor_groups),
    )
    return role, why, metrics

def detect_unknown_sdu_papers(df, matched_idx):
    """
    Находит публикации где есть SDU в affiliations,
    но ни один автор не попал в faculty matching.
    """

    sdu_mask = df["affiliations"].fillna("").str.contains(
        "SDU|Suleyman Demirel", case=False, regex=True
    )

    sdu_df = df[sdu_mask]

    unknown = sdu_df[~sdu_df.index.isin(matched_idx)].copy()

    return unknown


def build_coauthor_edges(df_in, min_edge_weight=2, max_authors_per_paper=25):
    """
    Returns: DataFrame with columns [a, b, w] for coauthor edges.
    - min_edge_weight: keep pairs that coauthored at least this many times
    - max_authors_per_paper: ignore huge collaborations (to avoid dense hairball)
    """
    pair_counts = Counter()

    for authors_raw in df_in["authors"].dropna():
        names = [a.strip() for a in str(authors_raw).split(";") if a.strip()]
        names = list(dict.fromkeys(names))  # preserve order, remove duplicates
        if len(names) < 2:
            continue
        if len(names) > max_authors_per_paper:
            continue

        # all unordered pairs
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                if a == b:
                    continue
                key = tuple(sorted((a, b)))
                pair_counts[key] += 1

    rows = [{"a": k[0], "b": k[1], "w": v} for k, v in pair_counts.items() if v >= min_edge_weight]
    return pd.DataFrame(rows)


def plot_network_plotly(G, node_size_map=None, node_color_map=None, node_group_map=None, title=""):
    """
    Plotly network visualization.
    node_size_map: dict(node -> size) optional
    """
    if G.number_of_nodes() == 0:
        return None

    pos = nx.spring_layout(G, k=0.45, iterations=60, seed=42)

    # Edges
    # максимальный вес ребра
    # --- Weighted edges (thicker = more shared papers) ---
    weights = [d.get("weight", 1) for _, _, d in G.edges(data=True)]
    w_max = max(weights) if weights else 1

    def edge_width(w):
        if w_max == 1:
            return 1.5
        return 1.2 + 3.8 * (w / w_max)

    edge_traces = []
    for u, v, d in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        w = d.get("weight", 1)

        edge_traces.append(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(width=edge_width(w), color="rgba(232,255,71,0.22)"),
                hoverinfo="text",
                text=f"{u} — {v}<br>{w} shared papers",
            )
        )
    # Nodes
    nodes = list(G.nodes())
    node_x = [pos[n][0] for n in nodes]
    node_y = [pos[n][1] for n in nodes]

    degrees = dict(G.degree())
    node_sizes = []
    for n in nodes:
        if node_size_map and n in node_size_map:
            node_sizes.append(node_size_map[n])
        else:
            node_sizes.append(8 + 4 * degrees.get(n, 1))  # fallback

    # Hover text
        # Hover text (+ community id if available)
    hover_text = []
    for n in nodes:
        comm = node_group_map.get(n, None) if node_group_map else None
        comm_str = f"Community: {comm}<br>" if comm is not None else ""
        hover_text.append(
            f"{n}<br>"
            f"{comm_str}"
            f"Co-authors: {degrees.get(n, 0)}<br>"
            f"Total collaborations (weighted): {int(G.degree(n, weight='weight'))}"
        )

    node_colors = [node_color_map.get(n, "#e8ff47") for n in nodes] if node_color_map else "#e8ff47"

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hovertext=hover_text,
        hoverinfo="text",
        marker=dict(
            size=node_sizes,
            color=node_colors,          # ← вот ключевое: список hex/rgba цветов
            showscale=False,
            line=dict(width=1, color="#0a0c10"),
            opacity=0.92,
        ),
    )

    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        **THEME,
        height=560,
        title=dict(
            text=title,
            x=0.02,
            y=0.98,
            font=dict(size=12, color="#6b7385", family="DM Mono")
        ),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )

    # Переопределяем margin отдельно
    fig.update_layout(margin=dict(t=40, b=10, l=10, r=10))
    return fig

def calc_h_index(s):
    cites = sorted(s.tolist(), reverse=True)
    h = 0
    for i, c in enumerate(cites):
        if c >= i + 1: h = i + 1
        else: break
    return h

def calc_g_index(s):
    cites = sorted(s.tolist(), reverse=True)
    g, cs = 0, 0
    for i, c in enumerate(cites):
        cs += c
        if cs >= (i+1)**2: g = i + 1
        else: break
    return g

def explode_authors(df_in):
    rows = []
    for _, row in df_in.iterrows():
        authors_raw = row.get("authors")
        if pd.notna(authors_raw) and str(authors_raw).strip():
            for name in str(authors_raw).split(";"):
                name = name.strip()
                if name:
                    rows.append({
                        "author": name,
                        "authors": row.get("authors", ""),
                        "citations": int(row.get("citations", 0) or 0),
                        "year": row.get("year"),
                        "area_clean": row.get("area_clean", "Unknown"),
                        "title": row.get("title", ""),
                        "journal": row.get("journal", ""),
                        "doi": row.get("doi", ""),
                        "scopus_link": row.get("scopus_link", ""),
                        "kw_list": row.get("kw_list", []),
                        "quartile": row.get("quartile", None),
                        "quartile_all": row.get("quartile_all", None),
                        "quartile_detail": row.get("quartile_detail", None),
                        "quartile_status": row.get("quartile_status", None),
                        "open_access_bool": row.get("open_access_bool", False),
                    })
    return pd.DataFrame(rows)

def to_csv_bytes(df_in):
    return df_in.to_csv(index=False).encode("utf-8")

QUARTILE_COLORS = {
    "Q1": ("#e8ff47", "#1a2200"),
    "Q2": ("#47c8ff", "#001a22"),
    "Q3": ("#ffa447", "#221200"),
    "Q4": ("#ff6b47", "#220800"),
}

# Human-readable explanations for API statuses
QUARTILE_STATUS_LABELS = {
    "conference_or_book":    ("conference / book", "#a47fff"),
    "no_quartile_in_scopus": ("no quartile in Scopus", "#4a5060"),
    "no_information_in_scopus": ("not in Scopus", "#4a5060"),
    "removed_from_scopus":   ("removed from Scopus", "#4a5060"),
    "ok_2024_manual":        None,
}

def quartile_badge(q):
    """Single badge for the best quartile."""
    if not q or str(q).strip().lower() in ("nan", "none", ""):
        return ""
    q = str(q).strip().upper()
    bg, txt_color = QUARTILE_COLORS.get(q, ("#2a3045", "#e8eaf0"))
    return (
        f"<span style='display:inline-block;background:{bg};color:{txt_color};"
        f"font-family:DM Mono,monospace;font-size:10px;font-weight:700;"
        f"padding:2px 8px;border-radius:2px;letter-spacing:0.05em;margin-right:4px;'>"
        f"{q}</span>"
    )

def quartile_full_display(row):
    """
    Returns HTML showing ALL quartiles with subject names.
    If no quartile — shows a short explanation why.
    """
    q_detail = row.get("quartile_detail")
    q_best   = row.get("quartile")
    status   = str(row.get("quartile_status", "") or "")

    # Has detailed breakdown
    if q_detail and str(q_detail).strip() not in ("nan", "None", ""):
        parts = [p.strip() for p in str(q_detail).split(";") if p.strip()]
        badges_html = ""
        for part in parts:
            # Format: "Food Science: Q1 (91%, rank 23/731)"
            if ": Q" in part:
                subject, rest = part.split(": Q", 1)
                q_val = "Q" + rest.split(" ")[0].rstrip(")")
                extra = rest[len(q_val)-1:].strip()  # e.g. "(91%, rank 23/731)"

                # Parse percent and rank from extra: "(91%, rank 23/731)"
                rank_html = ""
                import re
                m = re.search(r'\(rank\s+(\d+)[^,]*,\s*(\d+)%\)', extra)
                if m:
                    r_num, pct = m.group(1), m.group(2)
                    rank_html = (
                        f"<span style='font-family:DM Mono,monospace;font-size:10px;"
                        f"color:#ffffff;border-bottom:1px solid #ffffff;"
                        f"padding-bottom:1px;margin-left:4px;'>"
                        f"{pct}%, #{r_num}</span>"
                    )
                else:
                    # fallback — show raw extra dimmed
                    rank_html = (
                        f"<span style='font-family:DM Mono,monospace;font-size:9px;"
                        f"color:#4a5060;margin-left:4px;'>{extra}</span>"
                    )

                bg, tc = QUARTILE_COLORS.get(q_val, ("#2a3045", "#e8eaf0"))
                badges_html += (
                    f"<div style='display:flex;align-items:center;gap:6px;margin:2px 0;'>"
                    f"<span style='background:{bg};color:{tc};font-family:DM Mono,monospace;"
                    f"font-size:10px;font-weight:700;padding:1px 7px;border-radius:2px;"
                    f"min-width:28px;text-align:center;'>{q_val}</span>"
                    f"<span style='font-family:DM Mono,monospace;font-size:10px;color:#9aa0b0;'>"
                    f"{subject}</span>"
                    f"{rank_html}"
                    f"</div>"
                )
        return f"<div style='margin:4px 0;'>{badges_html}</div>"

    # Has only best quartile (no detail)
    if q_best and str(q_best).strip() not in ("nan", "None", ""):
        return quartile_badge(q_best)

    # No quartile — show explanation
    explanation = None
    border_color = "#4a5060"
    for key, val in QUARTILE_STATUS_LABELS.items():
        if key in status:
            if val is not None:
                explanation, border_color = val
            break
    if explanation is None and status.startswith("ok_"):
        explanation = f"data from {status.replace('ok_', '')} only"
        border_color = "#4a5060"
    if explanation is None:
        explanation = "quartile data not available"
        border_color = "#4a5060"

    return (
        f"<span style='display:inline-block;font-family:DM Mono,monospace;font-size:9px;"
        f"color:{border_color};border:1px solid {border_color};"
        f"padding:1px 7px;border-radius:2px;letter-spacing:0.05em;'>"
        f"{explanation}</span>"
    )

def fmt_authors(authors_str, n=5):
    parts = [a.strip() for a in str(authors_str).split(";") if a.strip()]
    if not parts: return ""
    if len(parts) > n: return ", ".join(parts[:n]) + " et al."
    return ", ".join(parts)

def get_keywords(df_in, n=5):
    kws = []
    for lst in df_in["kw_list"]:
        kws.extend(lst)
    return [k for k, _ in Counter(kws).most_common(n)]
@st.cache_data
def load_teachers():
    try:
        t = pd.read_csv("teachers.csv", encoding="utf-8-sig")
        return t
    except FileNotFoundError:
        return pd.DataFrame()

@st.cache_data
def load_aliases():
    """Load aliases.csv with columns: scopus_name; emp_id  (semicolon separated).
    scopus_name: full author name as in Scopus, e.g. "Tulenbaev, Aibek"
    emp_id: teacher EMP_ID from teachers.csv
    Returns dict {normalized_scopus_key -> "empid:EMP_ID"}."""
    try:
        # Use semicolon separator so names with commas are preserved intact
        a = pd.read_csv("aliase.csv", encoding="utf-8-sig", sep=";")
        a.columns = [str(col).strip().lower() for col in a.columns]
        if "scopus_name" not in a.columns or "emp_id" not in a.columns:
            return {}
        result = {}
        for _, row in a.iterrows():
            name = str(row["scopus_name"]).strip()
            eid  = str(row["emp_id"]).strip()
            if not name or not eid or name == "nan" or eid == "nan":
                continue
            # normalize the scopus name the same way as matching pipeline
            if "," in name:
                parts = name.split(",", 1)
                norm_key = _normalize_str(parts[0].strip()) + ", " + _normalize_str(parts[1].strip())
            else:
                # "Firstname Lastname" order — normalize whole string
                norm_key = _normalize_str(name)
            result[norm_key] = f"empid:{eid}"
        return result
    except FileNotFoundError:
        return {}

@st.cache_data
def _normalize_str(s):
    """Unified normalization: cyrillic→latin, strip accents, lowercase."""
    import unicodedata
    # Extended cyrillic→latin transliteration
    cyr_map = {
        'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'E','Ж':'Zh',
        'З':'Z','И':'I','Й':'Y','К':'K','Л':'L','М':'M','Н':'N','О':'O',
        'П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'Kh','Ц':'Ts',
        'Ч':'Ch','Ш':'Sh','Щ':'Sch','Ъ':'','Ы':'Y','Ь':'','Э':'E','Ю':'Yu',
        'Я':'Ya',
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh',
        'з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o',
        'п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'kh','ц':'ts',
        'ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu',
        'я':'ya',
    }
    result = ''
    for ch in str(s):
        result += cyr_map.get(ch, ch)
    result = result.lower().strip()
    result = unicodedata.normalize('NFD', result)
    result = ''.join(c for c in result if unicodedata.category(c) != 'Mn')
    return result

def _levenshtein(a, b):
    """Fast Levenshtein distance between two strings."""
    if a == b: return 0
    if len(a) < len(b): a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j] + (ca != cb), curr[j] + 1, prev[j + 1] + 1))
        prev = curr
    return prev[-1]

def _fuzzy_lookup(key, mapping, max_dist=2):
    """Try fuzzy match on the surname part (before ',') with same first initial.
    Returns matched info dict or None."""
    if ',' not in key:
        return None
    surname_q, rest_q = key.split(',', 1)
    surname_q = surname_q.strip()
    initial_q = rest_q.strip()[:1]  # first char after comma
    best_info, best_dist = None, max_dist + 1
    for k, info in mapping.items():
        if ',' not in k:
            continue
        surname_k, rest_k = k.split(',', 1)
        surname_k = surname_k.strip()
        initial_k = rest_k.strip()[:1]
        # First initial must match
        if initial_q and initial_k and initial_q != initial_k:
            continue
        dist = _levenshtein(surname_q, surname_k)
        if dist <= max_dist and dist < best_dist:
            best_dist = dist
            best_info = info
    return best_info


def build_fuzzy_map(mapping, max_dist=2):
    """Pre-compute {any_variant_surname -> canonical_staff_key} for fuzzy matching.
    mapping = author_dept (staff keys). fuzzy_map maps UNKNOWN pub keys -> staff keys.
    Works by grouping staff keys by initial and pre-indexing for fast lookup."""
    # Index staff keys by (first_initial, surname_length_bucket) for fast lookup
    by_initial = {}
    for k in mapping:
        if ',' not in k:
            continue
        parts = k.split(',', 1)
        initial = parts[1].strip()[:1]
        by_initial.setdefault(initial, []).append((parts[0].strip(), k))
    # Also build reverse index: surname -> staff_key (for direct fuzzy from pub side)
    surname_to_staff = {}
    for k in mapping:
        if ',' not in k:
            continue
        surname = k.split(',', 1)[0].strip()
        surname_to_staff.setdefault(surname, k)
    return {"by_initial": by_initial, "surname_to_staff": surname_to_staff}

def make_author_pdf(author_name, adf):
    buf = BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=f"{author_name} - publications",
        author="University Research Analytics",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#111418"),
        spaceAfter=10,
        alignment=TA_LEFT,
    )

    meta_style = ParagraphStyle(
        "MetaCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#555555"),
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.black,
        spaceAfter=5,
    )

    small_style = ParagraphStyle(
        "SmallCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#444444"),
        spaceAfter=4,
    )

    story = []

    papers = len(adf)
    total_cites = int(adf["citations"].sum()) if "citations" in adf.columns else 0
    year_min = int(adf["year"].min()) if adf["year"].notna().any() else "-"
    year_max = int(adf["year"].max()) if adf["year"].notna().any() else "-"

    story.append(Paragraph(f"Author publications report", title_style))
    story.append(Paragraph(f"<b>{author_name}</b>", styles["Heading2"]))
    story.append(
        Paragraph(
            f"Papers: <b>{papers}</b> &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"Citations: <b>{total_cites}</b> &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"Years: <b>{year_min} - {year_max}</b>",
            meta_style,
        )
    )
    story.append(Spacer(1, 6))

    # short summary table
    top_journal = "—"
    if "journal" in adf.columns and adf["journal"].notna().any():
        top_journal = adf["journal"].fillna("—").value_counts().idxmax()

    summary_data = [
        ["Metric", "Value"],
        ["Author", author_name],
        ["Publications", str(papers)],
        ["Total citations", str(total_cites)],
        ["Year range", f"{year_min} - {year_max}"],
        ["Top journal", str(top_journal)],
    ]

    summary_tbl = Table(summary_data, colWidths=[42 * mm, 120 * mm])
    summary_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111418")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f7f7f7")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(summary_tbl)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Publication list", styles["Heading2"]))
    story.append(Spacer(1, 4))

    sort_cols = [c for c in ["year", "citations"] if c in adf.columns]
    if sort_cols:
        adf = adf.sort_values(sort_cols, ascending=[False, False][:len(sort_cols)]).copy()

    for i, (_, row) in enumerate(adf.iterrows(), 1):
        title = str(row.get("title", "Untitled")).strip()
        year = row.get("year", "")
        journal = str(row.get("journal", "—")).strip()
        cites = int(row.get("citations", 0) or 0)
        doi = str(row.get("doi", "")).strip()
        scopus_link = str(row.get("scopus_link", "")).strip()
        authors = str(row.get("authors", "")).strip()

        if doi.lower() in ("nan", "none"):
            doi = ""
        if scopus_link.lower() in ("nan", "none"):
            scopus_link = ""

        story.append(Paragraph(f"{i}. <b>{title}</b>", body_style))
        story.append(
            Paragraph(
                f"Year: {year} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"Journal: {journal} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"Citations: {cites}",
                small_style,
            )
        )

        if authors:
            story.append(Paragraph(f"Authors: {authors}", small_style))

        links = []
        if doi:
            links.append(f"DOI: {doi}")
        if scopus_link:
            links.append(f"Scopus: {scopus_link}")

        if links:
            story.append(Paragraph("<br/>".join(links), small_style))

        story.append(Spacer(1, 6))

        # мягкий разрыв через каждые ~12 записей
        if i % 12 == 0 and i < len(adf):
            story.append(PageBreak())

    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes

def _resolve_key(key, author_dept, fuzzy_map, max_dist=2):
    """Return canonical key present in author_dept, or None.
    First tries exact match, then fuzzy on surname with same first initial."""
    if key in author_dept:
        return key
    if ',' not in key:
        return None
    parts = key.split(',', 1)
    surname_q = parts[0].strip()
    initial_q = parts[1].strip()[:1]
    best_key, best_dist = None, max_dist + 1
    for (surname_c, staff_key) in fuzzy_map["by_initial"].get(initial_q, []):
        if abs(len(surname_q) - len(surname_c)) > max_dist:
            continue
        d = _levenshtein(surname_q, surname_c)
        if d <= max_dist and d < best_dist:
            best_dist = d
            best_key = staff_key
    return best_key

def build_author_dept_map(surnames, names, staff_types, statuses, departments):
    """Build {normalized_author_key: (department, status)} from Academic staff (all statuses)."""
    mapping = {}
    for surname, name, stype, status, dept in zip(surnames, names, staff_types, statuses, departments):
        if stype != "Academic":
            continue
        if pd.isna(surname) or pd.isna(name) or not str(name).strip():
            continue
        norm_surname = _normalize_str(str(surname).strip())
        first = next((c for c in _normalize_str(str(name).strip()) if c.isalpha()), '')
        key = norm_surname + ", " + first + "."
        if key not in mapping:
            mapping[key] = {"dept": str(dept or ""), "status": str(status or "")}
    return mapping

def build_author_dept_map(surnames, names, staff_types, statuses, departments, emp_ids=None):
    """Build {normalized_key: info} from Academic staff.
    Registers initial-based, full-name, and emp_id-based keys.
    """
    mapping = {}
    if emp_ids is None:
        emp_ids = [None] * len(surnames)
    for surname, name, stype, status, dept, emp_id in zip(surnames, names, staff_types, statuses, departments, emp_ids):
        if stype != "Academic":
            continue
        if pd.isna(surname) or pd.isna(name) or not str(name).strip():
            continue
        norm_surname  = _normalize_str(str(surname).strip())
        norm_name     = _normalize_str(str(name).strip())
        first_initial = next((c for c in norm_name if c.isalpha()), "")
        if not first_initial:
            continue
        info = {"dept": str(dept or ""), "status": str(status or "")}
        key_init = norm_surname + ", " + first_initial + "."
        if key_init not in mapping:
            mapping[key_init] = info
        key_full = norm_surname + ", " + norm_name
        if key_full not in mapping:
            mapping[key_full] = info
        # emp_id key for alias matching
        if emp_id and str(emp_id).strip() not in ("", "nan", "None"):
            eid_key = f"empid:{str(emp_id).strip()}"
            mapping[eid_key] = info
    return mapping

def normalize_pub_author(raw_author):
    """Normalize a publication author string to a list of candidate keys.
    Handles 'Lastname, Firstname', 'Lastname, F.', 'F. Lastname' formats.
    Returns list of keys to try against the teacher map.
    """
    import re as _re
    raw = str(raw_author).strip()
    # Remove Scopus ID: "Kadyrov, Shirali (36844229300)"
    raw = _re.sub(r'\(\d+\)', '', raw).strip()
    if not raw:
        return []
    if ',' in raw:
        parts = raw.split(',', 1)
        surname   = _normalize_str(parts[0].strip())
        rest      = _normalize_str(parts[1].strip())
    else:
        tokens = raw.split()
        if len(tokens) < 2:
            return []
        surname = _normalize_str(tokens[-1].strip())
        rest    = _normalize_str(tokens[0].strip())

    first_initial = next((c for c in rest if c.isalpha()), '')
    if not first_initial:
        return []

    keys = []
    # full-name key: "kadyrov, shirali"  (when full firstname available)
    # check if rest looks like a full name (>2 chars, not just initials like "s.")
    rest_clean = rest.replace('.', '').strip()
    if len(rest_clean) > 2:
        keys.append(f"{surname}, {rest_clean}")
    # initial-based key: "kadyrov, s."
    keys.append(f"{surname}, {first_initial}.")
    return keys


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='color:#e8ff47;font-size:28px;letter-spacing:0.05em;font-family:Bebas Neue,sans-serif;'>FILTERS</h2>",
                unsafe_allow_html=True)

    # ── Year filter ────────────────────────────────────────────────────────────
    st.markdown("<div class='filter-header'>Year</div>", unsafe_allow_html=True)
    YEAR_SHOW = 5
    if "show_all_years" not in st.session_state:
        st.session_state.show_all_years = False
    if "selected_years" not in st.session_state:
        st.session_state.selected_years = set()

    display_years = all_years if st.session_state.show_all_years else all_years[:YEAR_SHOW]
    for y in display_years:
        cnt = year_counts[y]
        checked = st.checkbox(f"{int(y)}  ({cnt})", key=f"yr_{y}", value=(y in st.session_state.selected_years))
        if checked:
            st.session_state.selected_years.add(y)
        else:
            st.session_state.selected_years.discard(y)

    if len(all_years) > YEAR_SHOW:
        label = "Show less ↑" if st.session_state.show_all_years else f"Show more ({len(all_years) - YEAR_SHOW} more) ↓"
        if st.button(label, key="btn_years"):
            st.session_state.show_all_years = not st.session_state.show_all_years

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Research units filter ──────────────────────────────────────────────────
    st.markdown("<div class='filter-header'>Research Units</div>", unsafe_allow_html=True)
    UNIT_SHOW = 5
    if "show_all_units" not in st.session_state:
        st.session_state.show_all_units = False
    if "selected_units" not in st.session_state:
        st.session_state.selected_units = set()
    if "selected_authors" not in st.session_state:
        st.session_state.selected_authors = set()

    top_units_list = unit_counter.most_common(20)
    display_units = top_units_list if st.session_state.show_all_units else top_units_list[:UNIT_SHOW]
    for unit, cnt in display_units:
        short = unit[:35] + "…" if len(unit) > 35 else unit
        checked = st.checkbox(f"{short}  ({cnt})", key=f"unt_{unit}", value=(unit in st.session_state.selected_units))
        if checked:
            st.session_state.selected_units.add(unit)
        else:
            st.session_state.selected_units.discard(unit)

    if len(top_units_list) > UNIT_SHOW:
        label = "Show less ↑" if st.session_state.show_all_units else "Show more ↓"
        if st.button(label, key="btn_units"):
            st.session_state.show_all_units = not st.session_state.show_all_units

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── OA filter ─────────────────────────────────────────────────────────────
    st.markdown("<div class='filter-header'>Open Access</div>", unsafe_allow_html=True)
    oa_filter = st.radio("", ["All", "Open Access Only", "Closed Only"], label_visibility="collapsed")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Quartile filter ────────────────────────────────────────────────────────
    if df["quartile"].notna().any():
        st.markdown("<div class='filter-header'>Quartile</div>", unsafe_allow_html=True)
        q_options = ["All", "Q1", "Q2", "Q3", "Q4"]
        quartile_filter = st.radio("", q_options, label_visibility="collapsed", key="quartile_filter")
    else:
        quartile_filter = "All"

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Reset all filters", key="reset_btn"):
        st.session_state.selected_years = set()
        st.session_state.selected_authors = set()
        st.session_state.selected_units = set()
        st.session_state.selected_orgs = set()
        st.session_state.selected_confs = set()
        st.session_state.selected_funders = set()
        st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-family:DM Mono,monospace;font-size:10px;color:#6b7385;'>Source: Scopus</p>",
                unsafe_allow_html=True)

# ── APPLY FILTERS ──────────────────────────────────────────────────────────────
mask = pd.Series([True] * len(df), index=df.index)

if st.session_state.selected_years:
    mask &= df["year"].isin(st.session_state.selected_years)

if st.session_state.selected_authors:
    def has_author(authors_str):
        parts = [a.strip() for a in str(authors_str).split(";")]
        return any(a in st.session_state.selected_authors for a in parts)
    mask &= df["authors"].apply(has_author)

if st.session_state.selected_units:
    def has_unit(units_list):
        return any(u in st.session_state.selected_units for u in units_list)
    mask &= df["units"].apply(has_unit)

if st.session_state.get("selected_orgs"):
    def has_org(org_list):
        return any(o in st.session_state.selected_orgs for o in org_list)
    mask &= df["org_list"].apply(has_org)

if st.session_state.get("selected_confs"):
    mask &= df["conference"].isin(st.session_state.selected_confs)

if st.session_state.get("selected_funders"):
    def has_funder(funder_list):
        return any(f in st.session_state.selected_funders for f in funder_list)
    mask &= df["funder_list"].apply(has_funder)

if oa_filter == "Open Access Only":
    mask &= df["open_access_bool"]
elif oa_filter == "Closed Only":
    mask &= ~df["open_access_bool"]

if quartile_filter != "All":
    mask &= df["quartile_all"].fillna("").str.contains(quartile_filter, na=False)

fdf = df[mask].copy()

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:8px 0 32px">
    <p style="font-family:DM Mono,monospace;font-size:11px;letter-spacing:0.2em;text-transform:uppercase;">
        Scopus · Research Analytics Dashboard
    </p>
    <h1 style="font-size:64px;line-height:0.95;margin:8px 0 0;">
        UNIVERSITY <span style="color:#e8ff47;">RESEARCH</span>
    </h1>
</div>
""", unsafe_allow_html=True)

# ── KPI ────────────────────────────────────────────────────────────────────────
h_idx = calc_h_index(fdf["citations"])
g_idx = calc_g_index(fdf["citations"])
oa_pct = int(fdf["open_access_bool"].mean() * 100) if len(fdf) else 0

kpi_subs = [
    ("Indexed in Scopus", ""),
    (f"Avg {fdf['citations'].mean():.1f}/paper", ""),
    (f"{fdf['open_access_bool'].sum()} papers", ""),
    ("Disciplines", ""),
    ("Hirsch index", ""),
    ("g-index", ""),
]
k1, k2, k3, k4, k5, k6 = st.columns(6)
for col, label, val, (sub_text, _), color in [
    (k1, "Publications",  len(fdf),                      kpi_subs[0], "#e8eaf0"),
    (k2, "Citations",     f"{fdf['citations'].sum():,}",  kpi_subs[1], "#e8ff47"),
    (k3, "Open Access",   f"{oa_pct}%",                  kpi_subs[2], "#47c8ff"),
    (k4, "Subject Areas", fdf["area_clean"].nunique(),    kpi_subs[3], "#ff6b47"),
    (k5, "h-index",       h_idx,                         kpi_subs[4], "#a47fff"),
    (k6, "g-index",       g_idx,                         kpi_subs[5], "#47ffb8"),
]:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color};">{val}</div>
            <div class="metric-sub">{sub_text}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "📊 OVERVIEW"

# ── TABS ───────────────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:32px;border-top:2px solid #232836;margin-bottom:24px;'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-label'>Navigation</div>", unsafe_allow_html=True)
st.markdown("<div class='nav-radio-wrapper'>", unsafe_allow_html=True)
tab = st.radio(
    "Navigation",
    ["📊 OVERVIEW", "👤 AUTHORS", "🤝 CO-AUTHORSHIP", "🔍 SEARCH", "📰 JOURNALS", "📈 INDEXES", "🎯 CONFERENCES & FUNDING", "🎓 FIND A SUPERVISOR", "🏛️ FACULTY"],
    horizontal=True,
    key="active_tab",
    label_visibility="collapsed",
)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div style='border-top:2px solid #e8314a;margin-top:12px;margin-bottom:24px;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if tab == "📊 OVERVIEW":
    ov1, ov2 = st.columns([2, 1])
    with ov1:
        st.markdown("<div class='section-label'>Publications by Year</div>", unsafe_allow_html=True)
        yc = fdf.groupby("year").size().reset_index(name="count")
        fig = go.Figure(go.Bar(
            x=yc["year"], y=yc["count"],
            marker_color=[COLORS[0] for _ in yc["year"]],
            hovertemplate="<b>%{x}</b><br>%{y} publications<extra></extra>",
        ))
        fig.update_layout(**THEME, height=320, bargap=0.15,
            xaxis=YEAR_AXIS,
            yaxis=AXIS)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with ov2:
        st.markdown("<div class='section-label'>Document Types</div>", unsafe_allow_html=True)
        tc = fdf["doc_type"].value_counts().reset_index()
        tc.columns = ["type", "count"]
        # Group tiny slices (<1.5%) into "Other" so all types are visible
        tc_total = tc["count"].sum()
        tc["pct"] = tc["count"] / tc_total * 100
        tc_main = tc[tc["pct"] >= 1.5].copy()
        tc_other = tc[tc["pct"] < 1.5]
        if not tc_other.empty:
            other_row = pd.DataFrame([{
                "type": f"Other ({', '.join(tc_other['type'].tolist())})",
                "count": tc_other["count"].sum(),
                "pct": tc_other["pct"].sum()
            }])
            tc_main = pd.concat([tc_main, other_row], ignore_index=True)

        _doc_palette = [
            "#e8ff47", "#47c8ff", "#ff6b47", "#a47fff",
            "#47ffb8", "#ff47a4", "#ffa447", "#4778ff",
            "#ff4747", "#47ffd4", "#d4ff47", "#ff47d4"
        ]
        fig2 = go.Figure(go.Pie(
            labels=tc_main["type"], values=tc_main["count"], hole=0.65,
            marker=dict(
                colors=_doc_palette[:len(tc_main)],
                line=dict(color="#0a0c10", width=2)
            ),
            hovertemplate="<b>%{label}</b><br>%{value} papers (%{percent})<extra></extra>",
            textinfo="none",
            sort=False,
        ))
        fig2.update_layout(**THEME, height=320, showlegend=True,
            legend=dict(
                orientation="h", xanchor="center", x=0.5, y=-0.15,
                font=dict(size=10, color="#e8eaf0"),
                bgcolor="rgba(0,0,0,0)",
                itemwidth=30,
                tracegroupgap=4,
            ),
        )
        fig2.update_layout(margin=dict(t=20, b=80, l=10, r=10))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    ov3, ov4 = st.columns(2)
    with ov3:
        st.markdown("<div class='section-label'>Top Subject Areas</div>", unsafe_allow_html=True)
        ac = fdf["area_clean"].value_counts().head(10).reset_index()
        ac.columns = ["area", "count"]
        fig3 = go.Figure(go.Bar(x=ac["count"], y=ac["area"], orientation="h", marker_color=COLORS[0],
            hovertemplate="<b>%{y}</b><br>%{x} publications<extra></extra>"))
        fig3.update_layout(**THEME, height=320, xaxis=AXIS, yaxis=dict(**AXIS_CAT, autorange="reversed"), bargap=0.3)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with ov4:
        st.markdown("<div class='section-label'>Open Access Distribution</div>", unsafe_allow_html=True)
        oa_v = fdf["open_access_bool"].value_counts()
        fig_oa = go.Figure(go.Pie(
            labels=["Closed Access", "Open Access"],
            values=[oa_v.get(False, 0), oa_v.get(True, 0)],
            hole=0.7, marker=dict(colors=["#3B66DC", COLORS[0]], line=dict(color="#0a0c10", width=3)),
            hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>", textinfo="none",
        ))
        fig_oa.update_layout(**THEME, height=320, showlegend=True,
            legend=dict(font=dict(size=11, color="#e8eaf0"), bgcolor="rgba(0,0,0,0)",
                        orientation="h", x=0.2, y=-0.1))
        st.plotly_chart(fig_oa, use_container_width=True, config={"displayModeBar": False})

    # Citation trend + scatter — ONLY in this tab
    ov5, ov6 = st.columns(2)
    with ov5:
        st.markdown("<div class='section-label'>Citation Trend by Year</div>", unsafe_allow_html=True)
        ct = fdf.groupby("year")["citations"].sum().reset_index()
        fig_ct = go.Figure(go.Scatter(
            x=ct["year"], y=ct["citations"], mode="lines+markers",
            line=dict(color=COLORS[1], width=2), fill="tozeroy",
            fillcolor="rgba(71,200,255,0.08)", marker=dict(color=COLORS[1], size=5),
            hovertemplate="<b>%{x}</b><br>%{y} citations<extra></extra>",
        ))
        fig_ct.update_layout(**THEME, height=300, xaxis=YEAR_AXIS_5, yaxis=AXIS)
        st.plotly_chart(fig_ct, use_container_width=True, config={"displayModeBar": False})

    with ov6:
        st.markdown("<div class='section-label'>Citations vs Year</div>", unsafe_allow_html=True)
        sdf = fdf[fdf["citations"] > 0].copy()
        sdf["title_short"] = sdf["title"].apply(lambda x: x[:80] + "…" if len(str(x)) > 80 else x)
        fig_sc = px.scatter(sdf, x="year", y="citations", color="area_clean",
            hover_data={"title_short": True, "title": False},
            color_discrete_sequence=COLORS,
            labels={"year": "Year", "citations": "Citations", "area_clean": "", "title_short": "Title"})
        fig_sc.update_traces(marker=dict(size=7, opacity=0.75))
        fig_sc.update_layout(**THEME)
        fig_sc.update_layout(
            height=300,
            xaxis=YEAR_AXIS_5,
            yaxis=AXIS,
            margin=dict(t=10, b=20, l=10, r=10),
            legend=dict(font=dict(color="#e8eaf0", size=10), bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_sc, use_container_width=True, config={"displayModeBar": False})

    # Most cited papers WITH keywords
    st.markdown("<div class='section-label' style='margin-top:8px;'>Most Cited Publications</div>", unsafe_allow_html=True)
    border_colors = ["#e8ff47", "#47c8ff", "#ff6b47", "#a47fff", "#47ffb8"]
    for i, (_, row) in enumerate(fdf.nlargest(5, "citations").iterrows()):
        authors_str = fmt_authors(row.get("authors", ""))
        # Get up to 5 keywords
        kws = row["kw_list"][:5] if hasattr(row, "kw_list") and row["kw_list"] else []
        kw_html = "".join([f"<span class='kw-tag'>{k}</span>" for k in kws])
        doi_str = str(row.get("doi", "")).split(";")[0].split(",")[0].strip()
        doi_str_clean = doi_str.split("\n")[0].strip()
        doi_link = f'<a href="https://doi.org/{doi_str_clean}" target="_blank" style="color:#6b7385;font-size:10px;font-family:DM Mono,monospace;text-decoration:none;">↗ {doi_str_clean[:40]}</a>' if doi_str_clean and doi_str_clean.lower() not in ("nan", "none", "", "n/a", "-") else ""
        scopus_url = str(row.get("scopus_link", "")).strip()
        scopus_link = f'<a href="{scopus_url}" target="_blank" style="color:#47c8ff;font-size:10px;font-family:DM Mono,monospace;text-decoration:none;margin-left:12px;">↗ Scopus</a>' if scopus_url and scopus_url != "nan" else ""
        q_badge_ov = quartile_full_display(row)
        st.markdown(f"""
        <div style="background:#111418;border-left:3px solid {border_colors[i]};
                    padding:16px 20px;margin-bottom:10px;border-radius:0 4px 4px 0;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
                <div style="flex:1;">
                    <div style="font-size:14px;line-height:1.5;color:#e8eaf0;margin-bottom:5px;">{row['title']}</div>
                    <div style="font-size:12px;color:{border_colors[i]};font-style:italic;margin-bottom:6px;">{authors_str}</div>
                    <div style="font-family:DM Mono,monospace;font-size:10px;color:#6b7385;margin-bottom:8px;">
                        {int(row['year'])} · {str(row['journal'])[:65]}{'…' if len(str(row['journal']))>65 else ''} · {row['area_clean']}
                    </div>
                    <div style="margin-bottom:4px;">{q_badge_ov}{kw_html}</div>
                    {doi_link}{scopus_link}
                </div>
                <div style="text-align:right;white-space:nowrap;min-width:70px;">
                    <div style="font-family:Bebas Neue,sans-serif;font-size:42px;color:{border_colors[i]};line-height:1;">{row['citations']}</div>
                    <div style="font-family:DM Mono,monospace;font-size:9px;color:#6b7385;letter-spacing:0.1em;">CITATIONS</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — AUTHORS
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "👤 AUTHORS":
    author_df = explode_authors(fdf)
    if author_df.empty:
        st.info("No author data available.")
    else:
        # ── Pre-compute first-author stats for the entire tab ──────────────────
        _fa_rows = []
        for _, _r in fdf.iterrows():
            _raw = _r.get("authors")
            if pd.isna(_raw) or not str(_raw).strip():
                continue
            _parts = [a.strip() for a in str(_raw).split(";") if a.strip()]
            if not _parts:
                continue
            _fa_rows.append({"author": _parts[0], "citations": int(_r.get("citations", 0) or 0),
                              "year": _r.get("year"), "area_clean": _r.get("area_clean", "Unknown")})
        _fa_df = pd.DataFrame(_fa_rows) if _fa_rows else pd.DataFrame(columns=["author","citations","year","area_clean"])
        _fa_counts = _fa_df.groupby("author").size().reset_index(name="fa_papers") if not _fa_df.empty else pd.DataFrame(columns=["author","fa_papers"])

        a1, a2 = st.columns([2, 2])
        with a1:
            author_mode = st.radio("Rank by", ["Publications", "Citations"], horizontal=True, key="author_mode")
        with a2:
            top_n_authors = st.slider("Top N authors", 5, 30, 15)

        # ── Chart 1a: All papers (any author position) ────────────────────────
        all_pubs = author_df.groupby("author").size().reset_index(name="total_papers")
        all_pubs = all_pubs.merge(_fa_counts, on="author", how="left").fillna({"fa_papers": 0})
        all_pubs["fa_papers"] = all_pubs["fa_papers"].astype(int)
        all_pubs["fa_pct"] = (all_pubs["fa_papers"] / all_pubs["total_papers"] * 100).round(1)

        if author_mode == "Publications":
            chart_df_all = all_pubs.sort_values("total_papers", ascending=False).head(top_n_authors)
            x_all = chart_df_all["total_papers"]
            x_fa_all = chart_df_all["fa_papers"]
            x_title = "Papers"
            label_all = "Top Authors by Publications · All Papers"
            label_fa  = "Top Authors by Publications · First Author Only"
        else:
            all_cit = author_df.groupby("author")["citations"].sum().reset_index(name="total_citations")
            fa_cit = _fa_df.groupby("author")["citations"].sum().reset_index(name="fa_citations") if not _fa_df.empty else pd.DataFrame(columns=["author","fa_citations"])
            chart_df_all = all_cit.merge(fa_cit, on="author", how="left").fillna({"fa_citations": 0})
            chart_df_all["fa_citations"] = chart_df_all["fa_citations"].astype(int)
            chart_df_all["fa_pct"] = (chart_df_all["fa_citations"] / chart_df_all["total_citations"].replace(0,1) * 100).round(1)
            chart_df_all = chart_df_all.sort_values("total_citations", ascending=False).head(top_n_authors)
            x_all = chart_df_all["total_citations"]
            x_fa_all = chart_df_all["fa_citations"]
            x_title = "Citations"
            label_all = "Top Authors by Citations · All Papers"
            label_fa  = "Top Authors by Citations · First Author Only"

        # All papers — total only
        st.markdown(f"<div class='section-label'>{label_all}</div>", unsafe_allow_html=True)
        fig_all = go.Figure()
        fig_all.add_trace(go.Bar(
            x=x_all, y=chart_df_all["author"], orientation="h",
            name="Total", marker_color="#e8ff47",
            hovertemplate="<b>%{y}</b><br>Total: %{x}<extra></extra>",
        ))
        fig_all.update_layout(**THEME, barmode="overlay",
            height=max(300, top_n_authors * 32),
            xaxis=dict(**AXIS, title=x_title),
            yaxis=dict(**AXIS_CAT, autorange="reversed"), bargap=0.25,
            legend=dict(bgcolor="rgba(17,20,24,0.85)", bordercolor="#232836", borderwidth=1,
                font=dict(size=10, color="#e8eaf0", family="DM Mono, monospace"),
                x=1, y=1, xanchor="right", yanchor="top"),
        )
        st.plotly_chart(fig_all, use_container_width=True, config={"displayModeBar": False})

        # First author only — total (grey) + first author overlay (yellow)
        st.markdown(f"<div class='section-label' style='margin-top:8px;'>{label_fa}</div>", unsafe_allow_html=True)
        fig_fa = go.Figure()
        fig_fa.add_trace(go.Bar(
            x=x_all, y=chart_df_all["author"], orientation="h",
            name="Total", marker_color="rgba(35,40,54,1)",
            hovertemplate="<b>%{y}</b><br>Total: %{x}<extra></extra>",
        ))
        fig_fa.add_trace(go.Bar(
            x=x_fa_all, y=chart_df_all["author"], orientation="h",
            name="First author", marker_color="#e8ff47",
            customdata=chart_df_all["fa_pct"],
            hovertemplate="<b>%{y}</b><br>First author: %{x} (%{customdata:.1f}%)<extra></extra>",
        ))
        fig_fa.update_layout(**THEME, barmode="overlay",
            height=max(300, top_n_authors * 32),
            xaxis=dict(**AXIS, title=x_title),
            yaxis=dict(**AXIS_CAT, autorange="reversed"), bargap=0.25,
            legend=dict(bgcolor="rgba(17,20,24,0.85)", bordercolor="#232836", borderwidth=1,
                font=dict(size=10, color="#e8eaf0", family="DM Mono, monospace"),
                x=1, y=1, xanchor="right", yanchor="top"),
        )
        st.plotly_chart(fig_fa, use_container_width=True, config={"displayModeBar": False})

        # ── Chart 2: Avg citations — first author vs co-author ────────────────
        st.markdown("<div class='section-label' style='margin-top:8px;'>First Author Impact</div>", unsafe_allow_html=True)

        _impact_rows = []
        for _, _r in fdf.iterrows():
            _raw = _r.get("authors")
            if pd.isna(_raw) or not str(_raw).strip():
                continue
            _parts = [a.strip() for a in str(_raw).split(";") if a.strip()]
            for _i, _name in enumerate(_parts):
                _impact_rows.append({"author": _name, "citations": int(_r.get("citations", 0) or 0), "is_first": _i == 0})
        _impact_df = pd.DataFrame(_impact_rows) if _impact_rows else pd.DataFrame()

        if not _impact_df.empty:
            _fa_avg = _impact_df[_impact_df["is_first"]].groupby("author")["citations"].mean().reset_index(name="avg_first")
            _co_avg = _impact_df[~_impact_df["is_first"]].groupby("author")["citations"].mean().reset_index(name="avg_co")
            _fa_n = _impact_df[_impact_df["is_first"]].groupby("author").size().reset_index(name="n_first")
            _co_n = _impact_df[~_impact_df["is_first"]].groupby("author").size().reset_index(name="n_co")
            _imp = _fa_avg.merge(_co_avg, on="author").merge(_fa_n, on="author").merge(_co_n, on="author")
            _imp = _imp[(_imp["n_first"] >= 2) & (_imp["n_co"] >= 2)]
            _imp = _imp.sort_values("avg_first", ascending=False).head(top_n_authors)
            _imp["avg_first"] = _imp["avg_first"].round(1)
            _imp["avg_co"] = _imp["avg_co"].round(1)

            if not _imp.empty:
                fig_imp = go.Figure()
                fig_imp.add_trace(go.Bar(
                    x=_imp["avg_first"], y=_imp["author"], orientation="h",
                    name="As first author", marker_color="#e8ff47",
                    hovertemplate="<b>%{y}</b><br>First author avg: %{x:.1f} cit<extra></extra>",
                ))
                fig_imp.add_trace(go.Bar(
                    x=_imp["avg_co"], y=_imp["author"], orientation="h",
                    name="As co-author", marker_color="rgba(71,200,255,0.55)",
                    hovertemplate="<b>%{y}</b><br>Co-author avg: %{x:.1f} cit<extra></extra>",
                ))
                fig_imp.update_layout(**THEME, barmode="group",
                    height=max(300, len(_imp) * 32),
                    xaxis=dict(**AXIS, title="Avg citations / paper"),
                    yaxis=dict(**AXIS_CAT, autorange="reversed"),
                    bargap=0.2, bargroupgap=0.05,
                    legend=dict(
                        bgcolor="rgba(17,20,24,0.85)",
                        bordercolor="#232836", borderwidth=1,
                        font=dict(size=10, color="#e8eaf0", family="DM Mono, monospace"),
                        x=1, y=1, xanchor="right", yanchor="top",
                    ),
                )
                st.plotly_chart(fig_imp, use_container_width=True, config={"displayModeBar": False})
        # ── Author Impact Matrix ─────────────────────────────────────────────
    st.markdown("<div class='section-label' style='margin-top:8px;'>Author Impact Matrix</div>", unsafe_allow_html=True)

    m1, m2, m3 = st.columns([1.2, 1.2, 1.6])
    with m1:
        min_pubs_matrix = st.number_input("Min publications (matrix)", min_value=1, value=3, step=1)
    with m2:
        y_metric = st.selectbox("Y-axis", ["Avg citations", "Total citations"], index=0, key="aim_y")
    with m3:
        show_top = st.slider("Show top N (by total citations)", 10, 200, 80, step=10, key="aim_top")

    # Author-level stats
    astats = author_df.groupby("author").agg(
        publications=("citations", "count"),
        total_citations=("citations", "sum"),
        avg_citations=("citations", "mean"),
        last_year=("year", "max"),
    ).reset_index()

    # Primary area = most frequent subject area for that author
    primary_area = (
        author_df.groupby(["author", "area_clean"]).size().reset_index(name="n")
        .sort_values(["author", "n"], ascending=[True, False])
        .drop_duplicates("author")[["author", "area_clean"]]
        .rename(columns={"area_clean": "primary_area"})
    )
    astats = astats.merge(primary_area, on="author", how="left")
    astats["avg_citations"] = astats["avg_citations"].round(2)

    # Filter + keep readable subset
    astats = astats[astats["publications"] >= min_pubs_matrix].copy()
    astats = astats.sort_values("total_citations", ascending=False).head(show_top)

    if astats.empty:
        st.info("Not enough data for the matrix with current filters.")
    else:
        y_col = "avg_citations" if y_metric == "Avg citations" else "total_citations"
        y_label = "Avg citations / paper" if y_metric == "Avg citations" else "Total citations"

        fig_m = px.scatter(
            astats,
            x="publications",
            y=y_col,
            size="total_citations",
            color="primary_area",
            hover_name="author",
            hover_data={
                "primary_area": True,
                "publications": True,
                "total_citations": True,
                "avg_citations": True,
                "last_year": True,
            },
            labels={
                "publications": "Publications",
                y_col: y_label,
                "primary_area": "Primary area",
            },
            color_discrete_sequence=COLORS,
        )
        fig_m.update_traces(marker=dict(opacity=0.75), selector=dict(mode="markers"))
        fig_m.update_layout(
            **THEME,
            height=420,
            xaxis=AXIS,
            yaxis=dict(**AXIS, title=y_label),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9, color="#e8eaf0"), orientation="h", y=-0.25),
        )
        st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar": False})

        st.markdown(
            "<p style='font-family:DM Mono,monospace;font-size:10px;color:#6b7385;'>"
            "Tip: top-right = high output + high impact. "
            "Big bubbles = high total citations. Colors = primary subject area."
            "</p>",
            unsafe_allow_html=True
        )
        # ═════════════════════════════════════════════════════════════════════
    # Author Profile (mini-Scopus)
    # ═════════════════════════════════════════════════════════════════════
    st.markdown("<div class='section-label' style='margin-top:18px;'>Author Profile</div>", unsafe_allow_html=True)

    # список авторов из текущего фильтра
    author_list = sorted(author_df["author"].dropna().unique().tolist())

    p1, p2 = st.columns([2.2, 1.0])
    with p1:
        # Preserve selected author in session_state so search/filter reruns don't reset it
        if "author_profile_select" not in st.session_state or st.session_state.author_profile_select not in author_list:
            st.session_state.author_profile_select = author_list[0] if author_list else None
        selected_author = st.selectbox("Choose author", author_list, key="author_profile_select")
    with p2:
        min_year = int(fdf["year"].min()) if fdf["year"].notna().any() else 2000
        max_year = int(fdf["year"].max()) if fdf["year"].notna().any() else 2026
        if min_year == max_year:
            max_year = min_year + 1
        year_range = st.slider("Years", min_year, max_year, (min_year, max_year), key="author_profile_years")

    a_lo, a_hi = year_range
    adf = author_df[
        (author_df["author"] == selected_author) &
        (author_df["year"].between(a_lo, a_hi, inclusive="both"))
    ].copy()

    if adf.empty:
        st.info("No records for this author in the selected range.")
    else:
        pdf_bytes = make_author_pdf(selected_author, adf)
        st.download_button(
            "⬇ Download author PDF",
            data=pdf_bytes,
            file_name=f"{selected_author.replace('/', '_')}_publications.pdf",
            mime="application/pdf",
            key=f"dl_author_pdf_{selected_author}"
        )

        # Author KPIs
        papers = len(adf)
        total_cites = int(adf["citations"].sum())
        avg_cites = float(adf["citations"].mean()) if papers else 0.0
        h_a = calc_h_index(adf["citations"])
        g_a = calc_g_index(adf["citations"])
        i10_a = int((adf["citations"] >= 10).sum())

        # First-author stats for selected author
        _sel_fa = _fa_df[_fa_df["author"] == selected_author] if not _fa_df.empty else pd.DataFrame()
        _fa_paper_count = len(_sel_fa)
        _fa_share = round(_fa_paper_count / papers * 100) if papers else 0
        _fa_avg_cit = round(_sel_fa["citations"].mean(), 1) if not _sel_fa.empty else 0
        # co-author avg citations
        _sel_co_rows = [r for r in _impact_rows if r["author"] == selected_author and not r["is_first"]] if "_impact_rows" in dir() else []
        _co_avg_cit_sel = round(sum(r["citations"] for r in _sel_co_rows) / len(_sel_co_rows), 1) if _sel_co_rows else 0
        _fa_role = "Lead researcher" if _fa_share >= 60 else ("Active collaborator" if _fa_share >= 30 else "Collaborator")

        kA1, kA2, kA3, kA4, kA5, kA6, kA7 = st.columns(7)
        for col, label, val, sub, color in [
            (kA1, "Papers", papers, f"{a_lo}–{a_hi}", "#e8eaf0"),
            (kA2, "Citations", f"{total_cites:,}", f"Avg {avg_cites:.1f}/paper", "#47c8ff"),
            (kA3, "h-index", h_a, f"{h_a} papers ≥ {h_a}", "#e8ff47"),
            (kA4, "g-index", g_a, f"top {g_a} cum ≥ {g_a}²", "#a47fff"),
            (kA5, "i10-index", i10_a, "papers ≥ 10 cites", "#ff6b47"),
            (kA6, "Last year", int(pd.to_numeric(adf["year"], errors="coerce").max()), "most recent", "#47ffb8"),
            (kA7, "1st author", f"{_fa_share}%", f"{_fa_paper_count} of {papers} papers", "#ff47a4"),
        ]:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value" style="color:{color};">{val}</div>
                    <div class="metric-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        # First-author role badge + impact comparison
        _adv = _fa_avg_cit - _co_avg_cit_sel
        _adv_sign = "+" if _adv >= 0 else ""
        _adv_color = "#e8ff47" if _adv >= 0 else "#ff6b47"
        _role_color = "#e8ff47" if _fa_share >= 60 else ("#47c8ff" if _fa_share >= 30 else "#6b7385")
        _bar_w = _fa_share
        st.markdown(f"""
        <div style="display:flex;gap:10px;align-items:stretch;margin-top:10px;margin-bottom:4px;flex-wrap:wrap;">
          <div style="background:#111418;border:1px solid #232836;border-left:3px solid {_role_color};
                      padding:10px 16px;border-radius:0 4px 4px 0;flex:1;min-width:220px;">
            <div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:0.2em;
                        text-transform:uppercase;color:#6b7385;margin-bottom:6px;">Authorship Role</div>
            <div style="font-family:Bebas Neue,sans-serif;font-size:18px;color:{_role_color};
                        letter-spacing:0.05em;">{_fa_role}</div>
            <div style="margin-top:6px;height:4px;background:#1a1e28;border-radius:2px;">
              <div style="height:4px;width:{_bar_w}%;background:{_role_color};border-radius:2px;
                          transition:width 0.3s;"></div>
            </div>
            <div style="font-family:DM Mono,monospace;font-size:10px;color:#6b7385;margin-top:4px;">
              {_fa_share}% first-author papers
            </div>
          </div>
          <div style="background:#111418;border:1px solid #232836;border-left:3px solid #ff47a4;
                      padding:10px 16px;border-radius:0 4px 4px 0;flex:1;min-width:220px;">
            <div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:0.2em;
                        text-transform:uppercase;color:#6b7385;margin-bottom:6px;">Citation Impact</div>
            <div style="display:flex;gap:16px;align-items:flex-end;">
              <div>
                <div style="font-family:Bebas Neue,sans-serif;font-size:28px;color:#e8ff47;line-height:1;">{_fa_avg_cit}</div>
                <div style="font-family:DM Mono,monospace;font-size:9px;color:#6b7385;">as first author</div>
              </div>
              <div style="color:#2a3045;font-size:20px;padding-bottom:4px;">vs</div>
              <div>
                <div style="font-family:Bebas Neue,sans-serif;font-size:28px;color:#47c8ff;line-height:1;">{_co_avg_cit_sel}</div>
                <div style="font-family:DM Mono,monospace;font-size:9px;color:#6b7385;">as co-author</div>
              </div>
              <div style="margin-left:8px;padding-bottom:4px;">
                <div style="font-family:Bebas Neue,sans-serif;font-size:20px;color:{_adv_color};">{_adv_sign}{_adv:.1f}</div>
                <div style="font-family:DM Mono,monospace;font-size:9px;color:#6b7385;">Δ avg cit</div>
              </div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        # Trends
        t1, t2 = st.columns(2)

        with t1:
            st.markdown("<div class='section-label'>Citations by Year</div>", unsafe_allow_html=True)
            cy = adf.groupby("year")["citations"].sum().reset_index()
            fig_cy = go.Figure(go.Scatter(
                x=cy["year"], y=cy["citations"], mode="lines+markers",
                line=dict(color=COLORS[1], width=2),
                marker=dict(color=COLORS[1], size=6),
                fill="tozeroy", fillcolor="rgba(71,200,255,0.08)",
                hovertemplate="<b>%{x}</b><br>%{y} citations<extra></extra>",
            ))
            fig_cy.update_layout(**THEME, height=260, xaxis=YEAR_AXIS, yaxis=AXIS)
            st.plotly_chart(fig_cy, use_container_width=True, config={"displayModeBar": False})

        with t2:
            st.markdown("<div class='section-label'>Publications by Year</div>", unsafe_allow_html=True)
            py = adf.groupby("year").size().reset_index(name="papers")

            fig_py = go.Figure(go.Bar(
                x=py["year"],
                y=py["papers"],
                marker_color="rgba(232,255,71,0.45)",
                hovertemplate="<b>%{x}</b><br>%{y} papers<extra></extra>",
            ))

            fig_py.update_layout(
                **THEME,
                height=260,
                xaxis=YEAR_AXIS,
                yaxis=dict(**AXIS, dtick=1, title="Papers"),
                bargap=0.25
            )
            st.plotly_chart(fig_py, use_container_width=True, config={"displayModeBar": False})

        # Top journals + keywords
        jcol, kcol = st.columns([1.4, 1.6])

        with jcol:
            st.markdown("<div class='section-label'>Top Journals</div>", unsafe_allow_html=True)
            jtop = adf["journal"].fillna("—").value_counts().head(10).reset_index()
            jtop.columns = ["journal", "papers"]
            jtop["journal_short"] = jtop["journal"].apply(lambda x: str(x)[:50] + "…" if len(str(x)) > 50 else str(x))
            fig_jt = go.Figure(go.Bar(
                x=jtop["papers"], y=jtop["journal_short"], orientation="h",
                marker_color=COLORS[0],
                hovertemplate="<b>%{y}</b><br>%{x} papers<extra></extra>",
            ))
            fig_jt.update_layout(**THEME, height=320,
                xaxis=dict(
                **AXIS,
                title="Papers",
                range=[0, max(1, int(jtop["papers"].max())) + 0.5],
                tickmode="linear",
                tick0=0,
                dtick=1,
                ),  
                yaxis=dict(**AXIS_CAT, autorange="reversed"), bargap=0.25)
            st.plotly_chart(fig_jt, use_container_width=True, config={"displayModeBar": False})

        with kcol:
            st.markdown("<div class='section-label'>Top Keywords</div>", unsafe_allow_html=True)
            kws = []
            for lst in adf["kw_list"]:
                if isinstance(lst, list):
                    kws.extend(lst)
            kw_top = Counter([k for k in kws if k]).most_common(25)
            if not kw_top:
                st.info("No keyword data for this author.")
            else:
                kw_html = "".join([f"<span class='kw-tag'>{k}</span>" for k, _ in kw_top])
                st.markdown(f"<div style='line-height:1.9'>{kw_html}</div>", unsafe_allow_html=True)

            # Quartile breakdown for this author
            if adf["quartile"].notna().any():
                st.markdown("<div class='section-label' style='margin-top:14px;'>Quartile Breakdown</div>", unsafe_allow_html=True)
                aq = adf["quartile"].dropna().value_counts().reindex(["Q1","Q2","Q3","Q4"]).fillna(0)
                aq_colors = [QUARTILE_COLORS[q][0] for q in ["Q1","Q2","Q3","Q4"]]
                fig_aq = go.Figure(go.Bar(
                    x=["Q1","Q2","Q3","Q4"], y=aq.values.tolist(),
                    marker_color=aq_colors,
                    hovertemplate="<b>%{x}</b><br>%{y} papers<extra></extra>",
                ))
                fig_aq.update_layout(
                    **THEME,
                    height=180,
                    bargap=0.2,
                    xaxis=AXIS,
                    yaxis=dict(
                        **AXIS,
                        title="Papers",
                        rangemode="tozero",
                        tickmode="linear",
                        tick0=0,
                        dtick=1,
                    )
                )
                st.plotly_chart(fig_aq, use_container_width=True, config={"displayModeBar": False})

        # Top papers (by citations)
        st.markdown("<div class='section-label' style='margin-top:18px;'>Top Papers</div>", unsafe_allow_html=True)
        top_p = (
            adf.sort_values("citations", ascending=False)
            .drop_duplicates(subset=["title", "year"])
            .head(10)
        )

        border_cols = ["#e8ff47", "#47c8ff", "#ff6b47", "#a47fff", "#47ffb8"] * 10
        for idx, (_, row) in enumerate(top_p.iterrows()):
            authors_str = fmt_authors(row.get("authors", ""))
            kws = row["kw_list"][:5] if row["kw_list"] else []
            kw_html = "".join([f"<span class='kw-tag'>{k}</span>" for k in kws])
            doi_str = str(row.get("doi", "")).split(";")[0].split(",")[0].strip()
            doi_str_clean = doi_str.split("\n")[0].strip()
            doi_link = f'<a href="https://doi.org/{doi_str_clean}" target="_blank" style="color:#6b7385;font-size:10px;font-family:DM Mono,monospace;text-decoration:none;">↗ {doi_str_clean[:40]}</a>' if doi_str_clean and doi_str_clean.lower() not in ("nan", "none", "", "n/a", "-") else ""
            scopus_url = str(row.get("scopus_link", "")).strip()
            scopus_link = f'<a href="{scopus_url}" target="_blank" style="color:#47c8ff;font-size:10px;font-family:DM Mono,monospace;text-decoration:none;margin-left:12px;">↗ Scopus</a>' if scopus_url and scopus_url != "nan" else ""
            q_badge = quartile_full_display(row)
            card_color = "#a47fff" if "conference_or_book" in str(row.get("quartile_status","")) else border_cols[idx % 5]

            st.markdown(f"""
            <div style="background:#111418;border:1px solid #1e2230;border-left:3px solid {card_color};
                        padding:16px 20px;margin-bottom:8px;border-radius:0 4px 4px 0;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
                    <div style="flex:1;min-width:0;">
                        <div style="font-size:14px;line-height:1.5;color:#e8eaf0;margin-bottom:5px;font-weight:400;">{row['title']}</div>
                        <div style="font-size:12px;color:{card_color};font-style:italic;margin-bottom:6px;">{authors_str}</div>
                        <div style="font-family:DM Mono,monospace;font-size:10px;color:#6b7385;margin-bottom:8px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
                            <span>{int(row['year'])}</span>
                            <span style="color:#2a3045;">·</span>
                            <span>{str(row['journal'])[:60]}{'…' if len(str(row['journal']))>60 else ''}</span>
                            <span style="color:#2a3045;">·</span>
                            <span style="color:#9aa0b0;">{row['area_clean']}</span>
                        </div>
                        <div style="margin-bottom:4px;">{q_badge}{kw_html}</div>
                        <div style="line-height:1;">{doi_link}{scopus_link}</div>
                    </div>
                    <div style="text-align:right;white-space:nowrap;min-width:65px;">
                        <div style="font-family:Bebas Neue,sans-serif;font-size:38px;color:{card_color};line-height:1;">{row['citations']}</div>
                        <div style="font-family:DM Mono,monospace;font-size:9px;color:#6b7385;letter-spacing:0.08em;">CITED</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — SEARCH
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "🔍 SEARCH":
    s1, s2 = st.columns([3, 1])
    with s1:
        query = st.text_input("", placeholder="🔍  Search by title, author, journal, keyword, abstract…",
                              label_visibility="collapsed")
    with s2:
        sort_by = st.selectbox("Sort by", ["citations ↓", "year ↓", "year ↑", "title ↑"],
                               label_visibility="collapsed")

    search_df = fdf.copy()
    search_df["kw_list"] = search_df["keywords_author"].apply(
        lambda x: [k.strip() for k in str(x).split(";") if k.strip()] if pd.notna(x) else []
    )
    if query:
        q = query.lower()
        search_df = search_df[
            search_df["title"].str.lower().str.contains(q, na=False) |
            search_df["authors"].str.lower().str.contains(q, na=False) |
            search_df["journal"].str.lower().str.contains(q, na=False) |
            search_df["keywords_author"].str.lower().str.contains(q, na=False) |
            search_df.get("abstract", pd.Series(dtype=str)).str.lower().str.contains(q, na=False)
        ]

    sort_map = {"citations ↓": ("citations", False), "year ↓": ("year", False),
                "year ↑": ("year", True), "title ↑": ("title", True)}
    sc, sa = sort_map[sort_by]
    search_df = search_df.sort_values(sc, ascending=sa)

    st.markdown(f"""
    <div style="display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap;align-items:center;">
        <span class="info-pill">Found: <b style="color:#e8ff47;">{len(search_df)}</b></span>
        <span class="info-pill">Citations: <b style="color:#47c8ff;">{search_df['citations'].sum():,}</b></span>
        <span class="info-pill">Avg: <b style="color:#ff6b47;">{search_df['citations'].mean():.1f}</b>/paper</span>
    </div>""", unsafe_allow_html=True)

    # Beautiful card-based results
    border_cols = ["#e8ff47", "#47c8ff", "#ff6b47", "#a47fff", "#47ffb8"] * 40
    for idx, (_, row) in enumerate(search_df.head(20).iterrows()):
        authors_str = fmt_authors(row.get("authors", ""))
        kws = row["kw_list"][:5] if row["kw_list"] else []
        kw_html = "".join([f"<span class='kw-tag'>{k}</span>" for k in kws])
        doi_str = str(row.get("doi", "")).split(";")[0].split(",")[0].strip()
        doi_str_clean = doi_str.split("\n")[0].strip()
        doi_link = f'<a href="https://doi.org/{doi_str_clean}" target="_blank" style="color:#6b7385;font-size:10px;font-family:DM Mono,monospace;text-decoration:none;">↗ {doi_str_clean[:40]}</a>' if doi_str_clean and doi_str_clean.lower() not in ("nan", "none", "", "n/a", "-") else ""
        scopus_url = str(row.get("scopus_link", "")).strip()
        scopus_link = f'<a href="{scopus_url}" target="_blank" style="color:#47c8ff;font-size:10px;font-family:DM Mono,monospace;text-decoration:none;margin-left:12px;">↗ Scopus</a>' if scopus_url and scopus_url != "nan" else ""
        oa_badge = '<span style="background:#1a2e1a;color:#47ffb8;font-family:DM Mono,monospace;font-size:9px;padding:2px 7px;border-radius:2px;border:1px solid #47ffb8;letter-spacing:0.1em;">OPEN ACCESS</span>' if row["open_access_bool"] else ""
        q_badge = quartile_full_display(row)
        card_color = "#a47fff" if "conference_or_book" in str(row.get("quartile_status","")) else border_cols[idx % 5]

        st.markdown(f"""
        <div style="background:#111418;border:1px solid #1e2230;border-left:3px solid {card_color};
                    padding:16px 20px;margin-bottom:8px;border-radius:0 4px 4px 0;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
                <div style="flex:1;min-width:0;">
                    <div style="font-size:14px;line-height:1.5;color:#e8eaf0;margin-bottom:5px;font-weight:400;">{row['title']}</div>
                    <div style="font-size:12px;color:{card_color};font-style:italic;margin-bottom:6px;">{authors_str}</div>
                    <div style="font-family:DM Mono,monospace;font-size:10px;color:#6b7385;margin-bottom:8px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
                        <span>{int(row['year'])}</span>
                        <span style="color:#2a3045;">·</span>
                        <span>{str(row['journal'])[:60]}{'…' if len(str(row['journal']))>60 else ''}</span>
                        <span style="color:#2a3045;">·</span>
                        <span style="color:#9aa0b0;">{row['area_clean']}</span>
                    </div>
                    <div style="margin-bottom:4px;">{q_badge}{oa_badge}{kw_html}</div>
                    <div style="line-height:1;">{doi_link}{scopus_link}</div>
                </div>
                <div style="text-align:right;white-space:nowrap;min-width:65px;">
                    <div style="font-family:Bebas Neue,sans-serif;font-size:38px;color:{card_color};line-height:1;">{row['citations']}</div>
                    <div style="font-family:DM Mono,monospace;font-size:9px;color:#6b7385;letter-spacing:0.08em;">CITED</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    if len(search_df) > 20:
        st.markdown(f"<p style='font-family:DM Mono,monospace;font-size:11px;color:#6b7385;text-align:center;'>Showing 20 of {len(search_df)} results. Download CSV for full list.</p>",
                    unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    d1, d2 = st.columns([1, 1])
    with d1:
        st.download_button("⬇ Download filtered CSV", data=to_csv_bytes(search_df),
                           file_name="publications_filtered.csv", mime="text/csv")
    with d2:
        dedup_df = search_df.dropna(subset=["doi"]).drop_duplicates(subset=["doi"])
        st.download_button("⬇ Download dedup CSV", data=to_csv_bytes(dedup_df),
                           file_name="publications_dedup.csv", mime="text/csv")
# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — JOURNALS
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "📰 JOURNALS":
    j1, j2 = st.columns([2, 1])
    with j1:
        journal_mode = st.radio("Rank by", ["Publications", "Citations"], horizontal=True, key="journal_mode")
    with j2:
        top_n_j = st.slider("Top N journals", 5, 30, 15)

    jstats = fdf.groupby("journal").agg(
        publications=("citations", "count"), total_citations=("citations", "sum")
    ).reset_index()
    jstats["avg_citations"] = (jstats["total_citations"] / jstats["publications"]).round(1)

    if journal_mode == "Publications":
        js = jstats.sort_values("publications", ascending=False).head(top_n_j)
        xc, xl, bc = "publications", "Publications", COLORS[0]
    else:
        js = jstats.sort_values("total_citations", ascending=False).head(top_n_j)
        xc, xl, bc = "total_citations", "Citations", COLORS[1]

    js = js.copy()
    js["journal_short"] = js["journal"].apply(lambda x: x[:55] + "…" if len(str(x)) > 55 else x)
    st.markdown(f"<div class='section-label'>Top Journals by {journal_mode}</div>", unsafe_allow_html=True)
    fig_j = go.Figure(go.Bar(
        x=js[xc], y=js["journal_short"], orientation="h", marker_color=bc,
        customdata=js[["publications", "total_citations", "avg_citations"]].values,
        hovertemplate="<b>%{y}</b><br>Publications: %{customdata[0]}<br>Citations: %{customdata[1]}<br>Avg: %{customdata[2]:.1f}<extra></extra>",
    ))
    fig_j.update_layout(**THEME, height=max(320, top_n_j * 28),
        xaxis=dict(**AXIS, title=xl), yaxis=dict(**AXIS_CAT, autorange="reversed"), bargap=0.25)
    st.plotly_chart(fig_j, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div class='section-label' style='margin-top:8px;'>Bradford Concentration</div>", unsafe_allow_html=True)
    j_all = jstats.sort_values("publications", ascending=False).reset_index(drop=True)
    j_all["cum_pct"] = j_all["publications"].cumsum() / j_all["publications"].sum() * 100
    b1, b2, b3 = st.columns(3)
    for col, pct, color in [(b1, 25, COLORS[0]), (b2, 50, COLORS[1]), (b3, 75, COLORS[2])]:
        n = min((j_all["cum_pct"] <= pct).sum() + 1, len(j_all))
        with col:
            st.markdown(f"""
            <div class="hindex-box" style="--accent-color:{color};">
                <div class="hindex-num" style="color:{color};">{n}</div>
                <div class="hindex-label">journals</div>
                <div class="hindex-sub">cover {pct}% of publications</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    fig_brad = go.Figure(go.Scatter(
        x=list(range(1, len(j_all)+1)), y=j_all["cum_pct"], mode="lines",
        line=dict(color=COLORS[0], width=2), fill="tozeroy", fillcolor="rgba(232,255,71,0.06)",
        hovertemplate="Top %{x} journals<br>%{y:.1f}%<extra></extra>",
    ))
    for t in [25, 50, 75]:
        fig_brad.add_hline(y=t, line_dash="dash", line_color="#232836",
            annotation_text=f"{t}%", annotation_font_color="#6b7385", annotation_font_size=10)
    fig_brad.update_layout(**THEME, height=280,
        xaxis=dict(**AXIS, title="Number of journals"),
        yaxis=dict(**AXIS, title="Cumulative % of publications", range=[0, 100]))
    st.plotly_chart(fig_brad, use_container_width=True, config={"displayModeBar": False})

    # ── Quartile Distribution ─────────────────────────────────────────────────
    if fdf["quartile"].notna().any():
        st.markdown("<div class='section-label' style='margin-top:8px;'>Quartile Distribution</div>", unsafe_allow_html=True)

        qd1, qd2 = st.columns(2)

        q_counts = fdf["quartile"].dropna().value_counts().reindex(["Q1", "Q2", "Q3", "Q4"]).fillna(0)
        q_colors_list = [QUARTILE_COLORS[q][0] for q in ["Q1", "Q2", "Q3", "Q4"]]

        with qd1:
            fig_qpie = go.Figure(go.Pie(
                labels=q_counts.index.tolist(),
                values=q_counts.values.tolist(),
                hole=0.6,
                marker=dict(colors=q_colors_list, line=dict(color="#0a0c10", width=2)),
                hovertemplate="<b>%{label}</b><br>%{value} papers (%{percent})<extra></extra>",
                textinfo="none",
                sort=False,
            ))
            fig_qpie.update_layout(**THEME, height=280, showlegend=True,
                legend=dict(font=dict(size=11, color="#e8eaf0"), bgcolor="rgba(0,0,0,0)",
                            orientation="h", x=0.1, y=-0.1))
            st.plotly_chart(fig_qpie, use_container_width=True, config={"displayModeBar": False})

        with qd2:
            # Q breakdown by year
            q_year = fdf[fdf["quartile"].notna()].groupby(["year", "quartile"]).size().unstack(fill_value=0)
            q_year = q_year.reindex(columns=["Q1", "Q2", "Q3", "Q4"], fill_value=0)
            fig_qy = go.Figure()
            for q, color in zip(["Q1", "Q2", "Q3", "Q4"], q_colors_list):
                if q in q_year.columns:
                    fig_qy.add_trace(go.Bar(
                        name=q, x=q_year.index.tolist(), y=q_year[q].tolist(),
                        marker_color=color,
                        hovertemplate=f"<b>{q}</b> %{{x}}<br>%{{y}} papers<extra></extra>",
                    ))
            fig_qy.update_layout(**THEME, height=280, barmode="stack", bargap=0.15,
                xaxis=YEAR_AXIS,
                yaxis=AXIS,
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color="#e8eaf0"),
                            orientation="h", x=0, y=1.12))
            st.plotly_chart(fig_qy, use_container_width=True, config={"displayModeBar": False})

        # Quick KPI pills
        total_q = q_counts.sum()
        q1_n = int(q_counts.get("Q1", 0))
        q1_pct = int(q1_n / total_q * 100) if total_q else 0
        q1q2_n = int(q_counts.get("Q1", 0) + q_counts.get("Q2", 0))
        q1q2_pct = int(q1q2_n / total_q * 100) if total_q else 0
        st.markdown(f"""
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:4px;margin-bottom:16px;">
            <span class="info-pill">Q1 papers: <b style="color:#e8ff47;">{q1_n}</b> ({q1_pct}%)</span>
            <span class="info-pill">Q1+Q2: <b style="color:#47c8ff;">{q1q2_n}</b> ({q1q2_pct}%)</span>
            <span class="info-pill">With quartile data: <b style="color:#a47fff;">{int(total_q)}</b></span>
        </div>""", unsafe_allow_html=True)

        # Top journals by quartile
        st.markdown("<div class='section-label'>Top Q1 Journals</div>", unsafe_allow_html=True)
        q1_journals = (
            fdf[fdf["quartile"] == "Q1"]
            .groupby("journal").agg(publications=("citations", "count"), total_citations=("citations", "sum"))
            .reset_index()
            .sort_values("publications", ascending=False)
            .head(10)
        )
        if not q1_journals.empty:
            q1_journals["journal_short"] = q1_journals["journal"].apply(lambda x: x[:55] + "…" if len(str(x)) > 55 else x)
            fig_q1j = go.Figure(go.Bar(
                x=q1_journals["publications"], y=q1_journals["journal_short"], orientation="h",
                marker_color=QUARTILE_COLORS["Q1"][0],
                customdata=q1_journals["total_citations"].values,
                hovertemplate="<b>%{y}</b><br>%{x} publications<br>%{customdata} citations<extra></extra>",
            ))
            fig_q1j.update_layout(**THEME, height=max(240, len(q1_journals) * 28),
                xaxis=dict(**AXIS, title="Publications"),
                yaxis=dict(**AXIS_CAT, autorange="reversed"), bargap=0.25)
            st.plotly_chart(fig_q1j, use_container_width=True, config={"displayModeBar": False})



    # настройки читаемости
    last_k_years = st.slider("Lookback years", 3, 8, 4)
    min_total_pubs = st.number_input("Min total pubs per journal", min_value=1, value=3, step=1)
    top_n = st.slider("Show top N declining", 5, 30, 15)

    # текущий верхний год в данных
    y_max = int(fdf["year"].max()) if fdf["year"].notna().any() else 2026
    y_min = y_max - last_k_years + 1

    # Build a set of known conference names so we don't show them as "declining journals"
    _conf_names = set(fdf["conference"].dropna().unique())

    rows = []
    for j, g in fdf.dropna(subset=["journal", "year"]).groupby("journal"):
        # Skip entries that are actually conference proceedings
        if j in _conf_names:
            continue
        total = len(g)
        if total < min_total_pubs:
            continue

        yg = g[g["year"].between(y_min, y_max)].groupby("year").size().reindex(range(y_min, y_max + 1), fill_value=0)
        if yg.sum() == 0:
            continue

        # линейный тренд на окне last_k_years
        x = np.arange(len(yg))
        y = yg.values.astype(float)
        # slope в "публикаций на год"
        slope = np.polyfit(x, y, 1)[0]

        rows.append({
            "journal": j,
            "slope": slope,
            "pubs_last_k": int(yg.sum()),
            "last_year_pubs": int(yg.iloc[-1]),
            "series": yg
        })

    trend_df = pd.DataFrame(rows)
    if trend_df.empty:
        st.info("Not enough data with current settings.")
    else:
        # берём только падающие
        trend_df = trend_df.sort_values("slope").reset_index(drop=True)
        declining = trend_df[trend_df["slope"] < 0].head(top_n).copy()

        if declining.empty:
            st.success("No declining journals found in the selected window.")
        else:
            # 1) Бар-чарт по slope
            fig_bar = go.Figure(go.Bar(
                x=declining["slope"],
                y=declining["journal"].apply(lambda s: s[:55] + "…" if len(str(s)) > 55 else str(s)),
                orientation="h",
                hovertemplate="<b>%{y}</b><br>Slope: %{x:.2f} pubs/year<extra></extra>"
            ))
            fig_bar.update_layout(**THEME, height=max(360, len(declining)*26), xaxis=AXIS, yaxis=dict(**AXIS_CAT, autorange="reversed"))
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

            # 2) Детализация: выбираем журнал и рисуем линию
            pick = st.selectbox("Show trend for journal", declining["journal"].tolist(), index=0)
            s = declining.loc[declining["journal"] == pick, "series"].values[0]

            fig_line = go.Figure(go.Scatter(
                x=list(s.index),
                y=list(s.values),
                mode="lines+markers",
                fill="tozeroy",
                hovertemplate="<b>%{x}</b><br>%{y} papers<extra></extra>"
            ))
            fig_line.update_layout(
                **THEME, height=260,
                xaxis=YEAR_AXIS,
                yaxis=dict(**AXIS, title="Papers"),
            )
            st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})

            st.markdown(
                f"<p style='font-family:DM Mono,monospace;font-size:10px;color:#6b7385;'>"
                f"Window: {y_min}–{y_max}. Negative slope means decreasing publications per year in this window."
                f"</p>",
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — CO-AUTHORSHIP
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "🤝 CO-AUTHORSHIP":
    coauth_df = fdf[fdf["n_authors"] > 0].copy()
    coauth_df["authorship_type"] = coauth_df["n_authors"].apply(
        lambda x: "Single" if x == 1 else ("2–3" if x <= 3 else ("4–6" if x <= 6 else "7+")))

    ca1, ca2 = st.columns(2)
    with ca1:
        st.markdown("<div class='section-label'>Authors per Paper</div>", unsafe_allow_html=True)
        nac = coauth_df["n_authors"].value_counts().sort_index().reset_index()
        nac.columns = ["n_authors", "papers"]
        nac = nac[nac["n_authors"] <= 20]
        fig_ca1 = go.Figure(go.Bar(x=nac["n_authors"], y=nac["papers"], marker_color=COLORS[0],
            hovertemplate="<b>%{x} authors</b><br>%{y} papers<extra></extra>"))
        fig_ca1.update_layout(**THEME, height=280, bargap=0.15,
            xaxis=dict(**AXIS, title="Number of authors"), yaxis=dict(**AXIS, title="Papers"))
        st.plotly_chart(fig_ca1, use_container_width=True, config={"displayModeBar": False})

    with ca2:
        st.markdown("<div class='section-label'>Single vs Multi-author</div>", unsafe_allow_html=True)
        tc2 = coauth_df["authorship_type"].value_counts().reset_index()
        tc2.columns = ["type", "count"]
        tc2["type"] = pd.Categorical(tc2["type"], categories=["Single", "2–3", "4–6", "7+"], ordered=True)
        tc2 = tc2.sort_values("type")
        fig_ca2 = go.Figure(go.Pie(labels=tc2["type"], values=tc2["count"], hole=0.6,
            marker=dict(colors=COLORS[:4], line=dict(color="#0a0c10", width=3)),
            hovertemplate="<b>%{label}</b><br>%{value} (%{percent})<extra></extra>", textinfo="none"))
        fig_ca2.update_layout(**THEME, height=280, showlegend=True,
            legend=dict(font=dict(size=11, color="#e8eaf0"), bgcolor="rgba(0,0,0,0)", orientation="h", x=0.1, y=-0.1))
        st.plotly_chart(fig_ca2, use_container_width=True, config={"displayModeBar": False})

    single_pct = int((coauth_df["n_authors"] == 1).mean() * 100)
    st.markdown(f"""
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:8px;">
        <span class="info-pill">Single-author: <b style="color:#e8ff47;">{single_pct}%</b></span>
        <span class="info-pill">Multi-author: <b style="color:#47c8ff;">{100-single_pct}%</b></span>
        <span class="info-pill">Avg: <b style="color:#ff6b47;">{coauth_df['n_authors'].mean():.1f}</b> authors/paper</span>
        <span class="info-pill">Median: <b style="color:#a47fff;">{coauth_df['n_authors'].median():.0f}</b></span>
        <span class="info-pill">Max: <b style="color:#47ffb8;">{int(coauth_df['n_authors'].max())}</b></span>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-label' style='margin-top:24px;'>Avg Authors per Paper — Trend</div>", unsafe_allow_html=True)
    at = coauth_df.groupby("year")["n_authors"].mean().reset_index()
    fig_at = go.Figure(go.Scatter(x=at["year"], y=at["n_authors"].round(2), mode="lines+markers",
        line=dict(color=COLORS[2], width=2), marker=dict(color=COLORS[2], size=5),
        hovertemplate="<b>%{x}</b><br>Avg %{y:.1f} authors/paper<extra></extra>"))
    fig_at.update_layout(**THEME, height=240, xaxis=YEAR_AXIS, yaxis=dict(**AXIS, title="Avg authors"))
    st.plotly_chart(fig_at, use_container_width=True, config={"displayModeBar": False})
    st.markdown("<div class='section-label' style='margin-top:24px;'>Co-authorship Network</div>", unsafe_allow_html=True)

    g1, g2, g3 = st.columns([1.2, 1.2, 1.6])
    with g1:
        min_edge_weight = st.slider("Min co-authored papers (edge)", 1, 10, 2, key="net_min_w")
    with g2:
        max_authors_per_paper = st.slider("Ignore papers with > N authors", 5, 60, 25, step=5, key="net_max_team")
    with g3:
        max_nodes = st.slider("Max nodes (top by collaborations)", 20, 250, 120, step=10, key="net_max_nodes")
    st.markdown("<div class='section-label'>Network Mode</div>", unsafe_allow_html=True)

    net_mode = st.radio(
        "",
        ["Global Network", "Ego Network"],
        horizontal=True,
        key="network_mode_toggle"
    )

    if net_mode == "Global Network":
    # твой существующий код глобальной сети
        edges_df = build_coauthor_edges(
            fdf,  # важно: сеть строим по текущему фильтру
            min_edge_weight=min_edge_weight,
            max_authors_per_paper=max_authors_per_paper,
        )

        if edges_df.empty:
            st.info("No co-authorship edges with current settings.")
        else:
            G = nx.Graph()
            for _, r in edges_df.iterrows():
                G.add_edge(r["a"], r["b"], weight=int(r["w"]))

            # Ограничим сеть, чтобы не была каша: берем top nodes по weighted-degree
            wd = dict(G.degree(weight="weight"))
            top_nodes = sorted(wd, key=lambda n: wd[n], reverse=True)[:max_nodes]
            Gs = G.subgraph(top_nodes).copy()
            # ── Centralities ─────────────────────────────────────────────────────────
            # Betweenness (bridge score). Weighted version: treat strong ties as "shorter distance"
            # distance = 1 / weight
            for u, v, d in Gs.edges(data=True):
                w = d.get("weight", 1) or 1
                d["distance"] = 1.0 / w

            btw = nx.betweenness_centrality(Gs, weight="distance", normalized=True)
            deg = dict(Gs.degree())                     # number of neighbors
            wdeg = dict(Gs.degree(weight="weight"))     # strength of collaborations

                    # ── Communities (greedy modularity) ───────────────────────────────
            communities = list(nx.algorithms.community.greedy_modularity_communities(Gs, weight="weight"))

            # node -> community id
            node_group_map = {}
            for i, comm in enumerate(communities):
                for n in comm:
                    node_group_map[n] = i

            # colors per community
            palette = COLORS  # твоя палитра
            node_color_map = {n: palette[node_group_map.get(n, 0) % len(palette)] for n in Gs.nodes()}
            # node size: weighted degree (больше — крупнее)
            wd_s = dict(Gs.degree(weight="weight"))
            if wd_s:
                mx = max(wd_s.values())
                node_size_map = {n: 10 + (28 * wd_s[n] / mx) for n in wd_s}  # 10..38
            else:
                node_size_map = None

            mB, mC = st.columns([1.2, 1.6])
            with mB:
                top_bridges = st.slider("Show top bridge authors", 5, 30, 12, key="net_top_bridges")
            with mC:
                bridge_cut = st.slider("Bridge highlight threshold (percentile)", 50, 99, 85, key="net_bridge_pct")

            # ── Node size map ───────────────────────────────────────────────────────
            nodes_list = list(Gs.nodes())

            vals = [wdeg.get(n, 0.0) for n in nodes_list]

            mx = max(vals) if vals else 1.0
            mx = mx if mx > 0 else 1.0

            node_size_map = {n: 10 + 28 * (wdeg.get(n, 0.0) / mx)
                            for n in nodes_list}
            fig_net = plot_network_plotly(
                Gs,
                node_size_map=node_size_map,
                node_color_map=node_color_map,
                node_group_map=node_group_map,
                title="Nodes = authors · Colors = communities · Edge weight = #shared papers",
            )
            st.plotly_chart(fig_net, use_container_width=True, config={"displayModeBar": False})
            st.markdown("<div class='section-label' style='margin-top:14px;'>Community Summary</div>", unsafe_allow_html=True)

            wd_s = dict(Gs.degree(weight="weight"))
            rows = []
            for cid, comm in enumerate(communities):
                members = list(comm)
                members_sorted = sorted(members, key=lambda x: wd_s.get(x, 0), reverse=True)
                top_members = ", ".join(members_sorted[:5]) + ("…" if len(members_sorted) > 5 else "")
                rows.append({
                    "community": cid,
                    "size": len(members),
                    "top_members": top_members,
                })

            cdf = pd.DataFrame(rows).sort_values(["size"], ascending=False)
            st.dataframe(cdf, use_container_width=True, hide_index=True)
            # Quick stats pills
            comps = nx.number_connected_components(Gs)
            density = nx.density(Gs) if Gs.number_of_nodes() > 1 else 0
            st.markdown(f"""
            <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:6px;">
                <span class="info-pill">Nodes: <b style="color:#e8ff47;">{Gs.number_of_nodes()}</b></span>
                <span class="info-pill">Edges: <b style="color:#47c8ff;">{Gs.number_of_edges()}</b></span>
                <span class="info-pill">Components: <b style="color:#ff6b47;">{comps}</b></span>
                <span class="info-pill">Density: <b style="color:#a47fff;">{density:.3f}</b></span>
            </div>
            """, unsafe_allow_html=True)
    if net_mode == "Ego Network":

        st.markdown("<div class='section-label'>Ego Network</div>", unsafe_allow_html=True)

        # список авторов из текущего фильтра
        all_authors = sorted(
            list(set(
                a.strip()
                for authors in fdf["authors"].dropna()
                for a in str(authors).split(";")
                if a.strip()
            ))
        )

        ego_author = st.selectbox("Select author", all_authors, key="ego_select")

        # строим глобальный граф (без ограничения top_nodes)
        edges_df = build_coauthor_edges(
            fdf,
            min_edge_weight=1,
            max_authors_per_paper=50
        )

        G_full = nx.Graph()
        for _, r in edges_df.iterrows():
            G_full.add_edge(r["a"], r["b"], weight=int(r["w"]))

        if ego_author not in G_full:
            st.info("Selected author has no co-authorship edges.")
        else:
            # ego graph (1-hop neighbors)
            G_ego = nx.ego_graph(G_full, ego_author, radius=1)

            # centrality внутри ego
            wdeg_ego = dict(G_ego.degree(weight="weight"))

            # size = weighted degree
            mx = max(wdeg_ego.values()) if wdeg_ego else 1
            node_size_map = {n: 12 + 30 * (wdeg_ego[n] / mx) for n in G_ego.nodes()}

            # цвет: ego — жёлтый, остальные — голубые
            node_color_map = {}
            for n in G_ego.nodes():
                if n == ego_author:
                    node_color_map[n] = "#e8ff47"
                else:
                    node_color_map[n] = "#47c8ff"

            fig_ego = plot_network_plotly(
                G_ego,
                node_size_map=node_size_map,
                node_color_map=node_color_map,
                node_group_map=None,
                title=f"Ego Network: {ego_author}"
            )

            st.plotly_chart(fig_ego, use_container_width=True, config={"displayModeBar": False})

            # Метрики ego
            ego_degree = G_full.degree(ego_author)
            ego_strength = G_full.degree(ego_author, weight="weight")

            st.markdown(f"""
            <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:8px;">
                <span class="info-pill">Direct co-authors: <b style="color:#e8ff47;">{ego_degree}</b></span>
                <span class="info-pill">Total collaborations: <b style="color:#47c8ff;">{ego_strength}</b></span>
                <span class="info-pill">Ego network size: <b style="color:#ff6b47;">{G_ego.number_of_nodes()}</b></span>
            </div>
            """, unsafe_allow_html=True)
            role, why, m = detect_role_in_team(G_full, ego_author)

            st.markdown("<div class='section-label' style='margin-top:14px;'>Role Detected</div>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="hindex-box" style="--accent-color:#e8ff47;">
            <div class="hindex-num" style="font-size:44px;color:#e8ff47;">{role}</div>
            <div class="hindex-sub">{why}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:8px;">
            <span class="info-pill">Degree: <b style="color:#e8ff47;">{m.get('degree')}</b></span>
            <span class="info-pill">Strength: <b style="color:#47c8ff;">{m.get('weighted_degree')}</b></span>
            <span class="info-pill">Clustering: <b style="color:#a47fff;">{m.get('clustering')}</b></span>
            <span class="info-pill">Betweenness (local): <b style="color:#ff6b47;">{m.get('betweenness_local')}</b></span>
            <span class="info-pill">Groups nearby: <b style="color:#47ffb8;">{m.get('neighbor_groups')}</b></span>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — INDEXES
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "📈 INDEXES":
    h = calc_h_index(fdf["citations"])
    g = calc_g_index(fdf["citations"])
    i10 = (fdf["citations"] >= 10).sum()

    hi1, hi2, hi3 = st.columns(3)
    for col, num, label, sub, color in [
        (hi1, h, "h-index", f"{h} papers with ≥ {h} citations", "#e8ff47"),
        (hi2, g, "g-index", f"top {g} papers avg ≥ {g} citations", "#47c8ff"),
        (hi3, i10, "i10-index", "papers with ≥ 10 citations", "#ff6b47"),
    ]:
        with col:
            st.markdown(f"""
            <div class="hindex-box" style="--accent-color:{color};">
                <div class="hindex-num" style="color:{color};">{num}</div>
                <div class="hindex-label">{label}</div>
                <div class="hindex-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-label' style='margin-top:28px;'>Citation Rank Plot</div>", unsafe_allow_html=True)
    sorted_c = fdf["citations"].sort_values(ascending=False).reset_index(drop=True)
    rank = list(range(1, len(sorted_c)+1))
    max_r = min(len(rank), int(sorted_c.max()) if sorted_c.max() > 0 else 1)
    fig_h = go.Figure()
    fig_h.add_trace(go.Scatter(x=rank, y=sorted_c.tolist(), mode="lines",
        line=dict(color=COLORS[0], width=2), name="Citations",
        hovertemplate="Rank %{x}<br>%{y} citations<extra></extra>"))
    fig_h.add_trace(go.Scatter(x=list(range(1, max_r+1)), y=list(range(1, max_r+1)),
        mode="lines", line=dict(color="#2a3045", width=1, dash="dash"), name="y=x", hoverinfo="skip"))
    fig_h.add_vline(x=h, line_color="#e8ff47", line_dash="dot", line_width=1)
    fig_h.add_annotation(x=h, y=float(sorted_c.max())*0.85, text=f"h = {h}",
        font=dict(color="#e8ff47", size=13, family="Bebas Neue"),
        showarrow=False, bgcolor="#0a0c10", borderpad=4)
    fig_h.update_layout(**THEME, height=320, xaxis=dict(**AXIS, title="Paper rank"),
        yaxis=dict(**AXIS, title="Citations"),
        legend=dict(font=dict(color="#e8eaf0"), bgcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar": False})

    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("<div class='section-label'>Cumulative h-index</div>", unsafe_allow_html=True)
        window_years = sorted(fdf["year"].dropna().unique().tolist())
        h_cum = [{"year": y, "h": calc_h_index(fdf[fdf["year"] <= y]["citations"])} for y in window_years]
        hdf = pd.DataFrame(h_cum)
        fig_hc = go.Figure(go.Scatter(x=hdf["year"], y=hdf["h"], mode="lines+markers",
            line=dict(color=COLORS[3], width=2), fill="tozeroy", fillcolor="rgba(164,127,255,0.08)",
            marker=dict(color=COLORS[3], size=6),
            hovertemplate="<b>Up to %{x}</b><br>h-index = %{y}<extra></extra>"))
        fig_hc.update_layout(**THEME, height=260, xaxis=YEAR_AXIS, yaxis=dict(**AXIS, title="h-index"))
        st.plotly_chart(fig_hc, use_container_width=True, config={"displayModeBar": False})

    with c_right:
        st.markdown("<div class='section-label'>Rolling 5-Year h-index</div>", unsafe_allow_html=True)
        rolling_h = [{"year": y, "h": calc_h_index(fdf[(fdf["year"] >= y-4) & (fdf["year"] <= y)]["citations"])}
                     for y in window_years if len(fdf[(fdf["year"] >= y-4) & (fdf["year"] <= y)]) > 0]
        rdf = pd.DataFrame(rolling_h)
        fig_rh = go.Figure(go.Bar(x=rdf["year"], y=rdf["h"],
            marker_color=[COLORS[0] if y >= 2020 else "rgba(232,255,71,0.3)" for y in rdf["year"]],
            hovertemplate="<b>%{x} (5yr)</b><br>h-index = %{y}<extra></extra>"))
        fig_rh.update_layout(**THEME, height=260, bargap=0.2, xaxis=YEAR_AXIS, yaxis=dict(**AXIS, title="5yr h-index"))
        st.plotly_chart(fig_rh, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — CONFERENCES & FUNDING
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "🎯 CONFERENCES & FUNDING":
    cf1, cf2 = st.columns(2)

    with cf1:
        st.markdown("<div class='section-label'>Top Conferences by Papers</div>", unsafe_allow_html=True)
        conf_df = fdf[fdf["conference"].notna()].copy()
        top_n_conf = st.slider("Top N conferences", 5, 20, 10, key="conf_slider")
        conf_counts = conf_df["conference"].value_counts().head(top_n_conf).reset_index()
        conf_counts.columns = ["conference", "count"]
        conf_counts["conf_short"] = conf_counts["conference"].apply(lambda x: x[:50] + "…" if len(x) > 50 else x)
        fig_conf = go.Figure(go.Bar(
            x=conf_counts["count"], y=conf_counts["conf_short"], orientation="h",
            marker_color=COLORS[0],
            hovertext=conf_counts["conference"],
            hovertemplate="<b>%{hovertext}</b><br>%{x} papers<extra></extra>",
        ))
        fig_conf.update_layout(**THEME, height=300,
            xaxis=AXIS, yaxis=dict(**AXIS_CAT, autorange="reversed"), bargap=0.25)
        st.plotly_chart(fig_conf, use_container_width=True, config={"displayModeBar": False})

    with cf2:
        st.markdown("<div class='section-label'>Conference Papers by Year</div>", unsafe_allow_html=True)
        conf_year = conf_df.groupby("year").size().reset_index(name="count")
        all_year_df = fdf.groupby("year").size().reset_index(name="total")
        conf_merged = conf_year.merge(all_year_df, on="year", how="right").fillna(0)
        conf_merged["pct"] = (conf_merged["count"] / conf_merged["total"] * 100).round(1)
        fig_cy = go.Figure()
        fig_cy.add_trace(go.Bar(
            x=conf_merged["year"], y=conf_merged["count"],
            marker_color="rgba(232,255,71,0.35)", name="Conference papers",
            hovertemplate="<b>%{x}</b><br>%{y} conf papers<extra></extra>",
        ))
        fig_cy.add_trace(go.Scatter(
            x=conf_merged["year"], y=conf_merged["pct"],
            mode="lines+markers", name="% of total", yaxis="y2",
            line=dict(color=COLORS[1], width=2), marker=dict(size=5),
            hovertemplate="<b>%{x}</b><br>%{y:.1f}% of total<extra></extra>",
        ))
        fig_cy.update_layout(**THEME, height=300, bargap=0.2,
            xaxis=YEAR_AXIS,
            yaxis=dict(**AXIS, title="Papers"),
            yaxis2=dict(overlaying="y", side="right", title="% of total",
                        tickfont=dict(color="#47c8ff"), title_font=dict(color="#47c8ff"),
                        gridcolor="rgba(0,0,0,0)"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e8eaf0"),
                        x=0, y=1.1, orientation="h"))
        st.plotly_chart(fig_cy, use_container_width=True, config={"displayModeBar": False})

    n_conf_papers = conf_df.shape[0]
    n_unique_confs = conf_df["conference"].nunique()
    top_conf = conf_df["conference"].value_counts().index[0] if n_unique_confs > 0 else "—"
    top_conf_short = top_conf[:60] + "…" if len(top_conf) > 60 else top_conf
    st.markdown(f"""
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:28px;">
        <span class="info-pill">Conference papers: <b style="color:#e8ff47;">{n_conf_papers}</b></span>
        <span class="info-pill">Unique conferences: <b style="color:#47c8ff;">{n_unique_confs}</b></span>
        <span class="info-pill">Top: <b style="color:#ff6b47;">{top_conf_short}</b></span>
    </div>""", unsafe_allow_html=True)

    # ── Funding ───────────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Top Funding Organizations</div>", unsafe_allow_html=True)
    fn1, fn2 = st.columns([2, 1])

    fund_rows = []
    for _, row in fdf.iterrows():
        for f in row["funder_list"]:
            fund_rows.append({"funder": f, "citations": row["citations"], "year": row["year"]})
    fund_df = pd.DataFrame(fund_rows) if fund_rows else pd.DataFrame(columns=["funder", "citations", "year"])

    with fn2:
        top_n_fund = st.slider("Top N funders", 5, 20, 12, key="fund_slider")

    with fn1:
        if not fund_df.empty:
            fund_counts = fund_df.groupby("funder").agg(
                papers=("citations", "count"),
                total_citations=("citations", "sum")
            ).reset_index()
            fund_counts = fund_counts.sort_values("papers", ascending=False).head(top_n_fund)
            fund_counts["funder_short"] = fund_counts["funder"].apply(lambda x: x[:52] + "…" if len(x) > 52 else x)
            fig_fund = go.Figure(go.Bar(
                x=fund_counts["papers"], y=fund_counts["funder_short"], orientation="h",
                marker=dict(color=fund_counts["papers"],
                            colorscale=[[0, "rgba(164,127,255,0.3)"], [1, "#a47fff"]], showscale=False),
                customdata=fund_counts["total_citations"].values,
                hovertemplate="<b>%{y}</b><br>%{x} papers<br>%{customdata} citations<extra></extra>",
            ))
            fig_fund.update_layout(**THEME, height=max(300, top_n_fund * 30),
                xaxis=AXIS, yaxis=dict(**AXIS_CAT, autorange="reversed"), bargap=0.25)
            st.plotly_chart(fig_fund, use_container_width=True, config={"displayModeBar": False})

    if not fund_df.empty:
        st.markdown("<div class='section-label' style='margin-top:8px;'>Funded vs Unfunded Papers per Year</div>",
                    unsafe_allow_html=True)
        funded_years = fdf[fdf["funder_list"].apply(len) > 0].groupby("year").size().reset_index(name="funded")
        all_years_df2 = fdf.groupby("year").size().reset_index(name="total")
        funded_merged = funded_years.merge(all_years_df2, on="year", how="right").fillna(0)
        funded_merged["unfunded"] = funded_merged["total"] - funded_merged["funded"]
        fig_ft = go.Figure()
        fig_ft.add_trace(go.Bar(name="Funded", x=funded_merged["year"], y=funded_merged["funded"],
            marker_color=COLORS[3], hovertemplate="<b>%{x}</b><br>%{y} funded<extra></extra>"))
        fig_ft.add_trace(go.Bar(name="No funding data", x=funded_merged["year"], y=funded_merged["unfunded"],
            marker_color="#1e2230", hovertemplate="<b>%{x}</b><br>%{y} no data<extra></extra>"))
        fig_ft.update_layout(**THEME, height=260, bargap=0.15, barmode="stack",
            xaxis=YEAR_AXIS, yaxis=AXIS,
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e8eaf0"),
                        x=0, y=1.1, orientation="h"))
        st.plotly_chart(fig_ft, use_container_width=True, config={"displayModeBar": False})

        n_funded = fdf[fdf["funder_list"].apply(len) > 0].shape[0]
        fund_pct = int(n_funded / len(fdf) * 100) if len(fdf) else 0
        st.markdown(f"""
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:8px;">
            <span class="info-pill">Funded papers: <b style="color:#a47fff;">{n_funded}</b> ({fund_pct}%)</span>
            <span class="info-pill">Unique funders: <b style="color:#47ffb8;">{fund_df['funder'].nunique()}</b></span>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — FIND A SUPERVISOR
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "🎓 FIND A SUPERVISOR":
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div class='section-label'>Research Topic Advisor Finder</div>
        <p style="font-family:'DM Mono',monospace;font-size:12px;color:#9aa0b0;margin-top:8px;">
            Enter your research topic or keywords. The system will match you with faculty
            members whose publications best align with your interests.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Build supervisor index from fdf ────────────────────────────────────────
    def build_supervisor_index(source_df):
        """
        For each author in the (filtered) dataset, collect:
          - all keywords, subject areas, paper titles, abstracts
          - publication count, citation count, h-index
          - recent activity (last 3 years)
          - top topics
        Returns a dict: author -> profile dict
        """
        profiles = {}

        for _, row in source_df.iterrows():
            authors_raw = row.get("authors", "")
            if pd.isna(authors_raw) or not str(authors_raw).strip():
                continue

            kws = row.get("kw_list", []) or []
            area = str(row.get("area_clean", "")) or ""
            title = str(row.get("title", "")) or ""
            abstract = str(row.get("abstract", "")) or ""
            cites = int(row.get("citations", 0) or 0)
            year = row.get("year")

            for name in str(authors_raw).split(";"):
                name = name.strip()
                if not name:
                    continue
                if name not in profiles:
                    profiles[name] = {
                        "keywords": Counter(),
                        "areas": Counter(),
                        "titles": [],
                        "abstracts": [],
                        "citations": 0,
                        "papers": 0,
                        "years": [],
                    }
                p = profiles[name]
                for k in kws:
                    if k:
                        p["keywords"][k.lower()] += 1
                if area and area != "Unknown":
                    p["areas"][area] += 1
                if title and title != "nan":
                    p["titles"].append(title.lower())
                if abstract and abstract != "nan":
                    p["abstracts"].append(abstract.lower())
                p["citations"] += cites
                p["papers"] += 1
                if pd.notna(year):
                    p["years"].append(int(year))

        return profiles

    supervisor_profiles = build_supervisor_index(fdf)

    # ── Only show authors who are in the current fdf (respects filters/exclusions) ──
    fdf_authors = set()
    for v in fdf["authors"].dropna():
        for a in str(v).split(";"):
            fdf_authors.add(a.strip())

    supervisor_profiles = {k: v for k, v in supervisor_profiles.items() if k in fdf_authors}

    # Use session_state directly — no st.form (forms cause tab jump to Overview on Enter)
    if "_sv_last_query" not in st.session_state:
        st.session_state["_sv_last_query"] = ""

    def _sv_commit():
        st.session_state["_sv_last_query"] = st.session_state["_sv_input_box"]

    st.text_input(
        "Research topic or keywords",
        placeholder="e.g. machine learning, drug resistance, sustainable energy...",
        key="_sv_input_box",
        on_change=_sv_commit,
    )
    topic_query = st.session_state["_sv_last_query"]
    top_n_sv = 7

    area_options = ["All areas"] + sorted([
        a for a in fdf["area_clean"].dropna().unique() if a != "Unknown"
    ])
    area_filter = st.selectbox("Filter by subject area", area_options, key="sv_area")
    min_papers_sv = 3

    if topic_query.strip():
        query_terms = [t.strip().lower() for t in topic_query.replace(",", " ").split() if t.strip()]

        def score_author(name, profile):
            import math
            kw_score = 0.0
            title_score = 0.0
            boost_log = []
            has_kw_match = False

            area_text = " ".join(profile["areas"].keys()).lower()

            for term in query_terms:
                kw_hits = sum(v for k, v in profile["keywords"].items() if term in k)
                if kw_hits:
                    kw_score += kw_hits * 10.0
                    has_kw_match = True
                    boost_log.append(f"keyword '{term}' ×{kw_hits}")

                title_hits = sum(1 for t in profile["titles"] if term in t)
                if title_hits:
                    title_score += title_hits * 3.0
                    boost_log.append(f"title '{term}' ×{title_hits}")

                if term in area_text:
                    boost_log.append(f"area match '{term}'")

            # No keyword match = excluded entirely
            if not has_kw_match:
                return 0.0, []

            score = kw_score + title_score

            # Citation and recency are additive tiebreakers only
            if profile["citations"] > 0:
                score += math.log1p(profile["citations"]) * 0.5

            current_year = 2026
            recent = sum(1 for y in profile["years"] if y >= current_year - 3)
            if recent > 0:
                score += recent * 0.3

            return score, boost_log

        # Filter by area
        candidates = {
            name: prof for name, prof in supervisor_profiles.items()
            if prof["papers"] >= min_papers_sv
        }
        if area_filter != "All areas":
            candidates = {
                name: prof for name, prof in candidates.items()
                if area_filter in prof["areas"]
            }

        # Only authors with keyword match pass
        scored = []
        for name, prof in candidates.items():
            s, log = score_author(name, prof)
            if s > 0:
                scored.append((name, prof, s, log))

        scored.sort(key=lambda x: x[2], reverse=True)
        top_results = scored[:top_n_sv]

        if not top_results:
            st.markdown("""
            <div style="background:#111418;border:1px solid #232836;border-left:3px solid #6b7385;
                        padding:16px 20px;border-radius:0 4px 4px 0;margin-top:16px;">
                <p style="font-family:'DM Mono',monospace;font-size:12px;color:#6b7385;">
                    No faculty member has published research matching this topic. Try broader or related keywords.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            max_score = top_results[0][2]
            accent_colors = ["#e8ff47", "#47c8ff", "#ff6b47", "#a47fff", "#47ffb8",
                             "#ff47a4", "#ffa447", "#4778ff", "#47ffd4", "#ff4747"]

            st.markdown(f"""
            <div style="font-family:'DM Mono',monospace;font-size:10px;color:#6b7385;
                        margin:12px 0 20px;letter-spacing:0.1em;text-transform:uppercase;">
                Found {len(scored)} matching supervisors · showing top {len(top_results)}
            </div>
            """, unsafe_allow_html=True)

            for rank, (name, prof, score, log) in enumerate(top_results):
                color = accent_colors[rank % len(accent_colors)]
                match_pct = int(score / max_score * 100)

                # Top keywords for this author relevant to query
                relevant_kws = []
                for term in query_terms:
                    for kw, cnt in prof["keywords"].most_common(30):
                        if term in kw and kw not in relevant_kws:
                            relevant_kws.append(kw)
                # Also show top general keywords
                top_kws = [k for k, _ in prof["keywords"].most_common(8) if k not in relevant_kws]
                all_display_kws = relevant_kws[:5] + top_kws[:max(0, 6 - len(relevant_kws[:5]))]

                kw_tags = "".join([
                    "<span style='background:{};border:1px solid {};color:{};padding:2px 8px;"
                    "border-radius:2px;font-size:10px;font-family:DM Mono,monospace;"
                    "display:inline-block;margin:2px;'>{}</span>".format(
                        "#1e2a10" if k in relevant_kws else "#1a1e28",
                        "#e8ff47" if k in relevant_kws else "#2a3045",
                        "#e8ff47" if k in relevant_kws else "#c8cad4",
                        k
                    )
                    for k in all_display_kws
                ])

                top_areas = ", ".join([a for a, _ in prof["areas"].most_common(3)])
                recent_years = sorted(set(prof["years"]))[-3:] if prof["years"] else []
                last_active = max(prof["years"]) if prof["years"] else "—"
                h_sv = calc_h_index(pd.Series([prof["citations"]]))  # simplified
                # Proper h-index: need per-paper citations — use stored data
                author_papers_cites = fdf[fdf["authors"].str.contains(
                    name.replace(".", "\.").replace("(", "\(").replace(")", "\)"),
                    na=False, regex=True
                )]["citations"]
                h_sv = calc_h_index(author_papers_cites)

                # Match bar
                bar_filled = int(match_pct / 100 * 20)
                bar = "█" * bar_filled + "░" * (20 - bar_filled)

                st.markdown(f"""
                <div style="background:#111418;border:1px solid #232836;
                            border-left:4px solid {color};
                            padding:20px 24px;border-radius:0 4px 4px 0;
                            margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;">
                        <div style="flex:1;min-width:200px;">
                            <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                                <span style="font-family:'Bebas Neue',sans-serif;font-size:13px;
                                             color:{color};letter-spacing:0.1em;">#{rank+1}</span>
                                <span style="font-size:16px;font-weight:500;color:#e8eaf0;">{name}</span>
                            </div>
                            <div style="font-family:'DM Mono',monospace;font-size:10px;color:#6b7385;margin-bottom:10px;">
                                {top_areas}
                            </div>
                            <div style="margin-bottom:10px;">{kw_tags}</div>
                            <div style="font-family:'DM Mono',monospace;font-size:10px;color:#4a5060;
                                        letter-spacing:0.05em;">
                            </div>
                        </div>
                        <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;">
                            <div style="text-align:center;min-width:56px;">
                                <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;
                                            line-height:1;color:{color};">{prof['papers']}</div>
                                <div style="font-family:'DM Mono',monospace;font-size:9px;
                                            color:#6b7385;letter-spacing:0.1em;text-transform:uppercase;">papers</div>
                            </div>
                            <div style="text-align:center;min-width:56px;">
                                <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;
                                            line-height:1;color:#47c8ff;">{prof['citations']:,}</div>
                                <div style="font-family:'DM Mono',monospace;font-size:9px;
                                            color:#6b7385;letter-spacing:0.1em;text-transform:uppercase;">citations</div>
                            </div>
                            <div style="text-align:center;min-width:56px;">
                                <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;
                                            line-height:1;color:#a47fff;">{h_sv}</div>
                                <div style="font-family:'DM Mono',monospace;font-size:9px;
                                            color:#6b7385;letter-spacing:0.1em;text-transform:uppercase;">h-index</div>
                            </div>
                            <div style="text-align:center;min-width:56px;">
                                <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;
                                            line-height:1;color:#47ffb8;">{last_active}</div>
                                <div style="font-family:'DM Mono',monospace;font-size:9px;
                                            color:#6b7385;letter-spacing:0.1em;text-transform:uppercase;">last pub</div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Score chart
            st.markdown("<div class='section-label' style='margin-top:24px;'>Match Score Comparison</div>",
                        unsafe_allow_html=True)
            chart_names = [r[0].split(",")[0] for r in top_results]
            chart_scores = [round(r[2] / max_score * 100, 1) for r in top_results]
            fig_sv = go.Figure(go.Bar(
                x=chart_scores,
                y=chart_names,
                orientation="h",
                marker=dict(
                    color=chart_scores,
                    colorscale=[[0, "rgba(232,255,71,0.25)"], [1, "#e8ff47"]],
                    showscale=False,
                ),
                hovertemplate="<b>%{y}</b><br>Match: %{x:.1f}%<extra></extra>",
            ))
            fig_sv.update_layout(**THEME, height=max(200, len(top_results) * 38),
                xaxis=dict(**AXIS, title="Match score (%)", range=[0, 105]),
                yaxis=dict(**AXIS_CAT, autorange="reversed"),
                bargap=0.25)
            st.plotly_chart(fig_sv, use_container_width=True, config={"displayModeBar": False})

    else:
        # Show browse mode when no query entered
        st.markdown("""
        <div style="background:#111418;border:1px solid #232836;padding:32px;
                    border-radius:4px;text-align:center;margin-top:16px;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:#6b7385;
                        letter-spacing:0.1em;margin-bottom:8px;">START YOUR SEARCH</div>
            <p style="font-family:'DM Mono',monospace;font-size:11px;color:#4a5060;">
                Type a research topic above to find the best matching supervisor,<br>
                or browse by subject area using the dropdown.
            </p>
        </div>
        """, unsafe_allow_html=True)



# ══════════════════════════════════════════════════════════════════════════════
# TAB 9 — FACULTY
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "🏛️ FACULTY":
    t_raw = load_teachers()
    if t_raw.empty:
        st.warning("teachers.csv not found. Place it in the same folder as dashboard.py.")
    else:
        # Build author→department lookup
        emp_ids = t_raw["EMP_ID"].tolist() if "EMP_ID" in t_raw.columns else None
        author_dept = build_author_dept_map(
            t_raw["SURNAME"].tolist(), t_raw["NAME"].tolist(),
            t_raw["STAFF_TYPE_EN"].tolist(), t_raw["STATUS_EN"].tolist(),
            t_raw["DEPARTMENT_EN"].tolist(),
            emp_ids=emp_ids,
        )
        # Load manual aliases: normalized scopus name -> "empid:EMP_ID"
        # empid:EMP_ID keys are already in author_dept from build_author_dept_map
        aliases = load_aliases()
        for scopus_norm_key, empid_key in aliases.items():
            if empid_key in author_dept:
                # register the scopus name variant pointing to the same staff info
                author_dept[scopus_norm_key] = author_dept[empid_key]
                # also register initial-based variant
                if "," in scopus_norm_key:
                    parts = scopus_norm_key.split(",", 1)
                    sur = parts[0].strip()
                    ini = next((ch for ch in parts[1].strip() if ch.isalpha()), "")
                    if ini:
                        init_key = f"{sur}, {ini}."
                        if init_key not in author_dept:
                            author_dept[init_key] = author_dept[empid_key]

        # Build once — O(1) fuzzy lookups everywhere below
        fuzzy_map = build_fuzzy_map(author_dept)

        # ── Tag each publication with department(s) of its SDU authors ─────────
        pub_dept_rows = []
        for idx, row in df.iterrows():
            depts_seen = set()
            # Primary: use full names from "Author full names" column
            full_authors = row.get("author_full_list", [])
            if not isinstance(full_authors, list):
                full_authors = []
            # Fallback: parse from "authors" (short format "Lastname, F.")
            authors_raw = row.get("authors", "")
            short_authors = str(authors_raw).split(";") if pd.notna(authors_raw) else []

            # Build candidate key lists: full names first, then short
            candidates = []
            for (lastname, firstname, *_) in full_authors:
                candidates.append(f"{_normalize_str(lastname)}, {_normalize_str(firstname)}")
            for a in short_authors:
                for k in normalize_pub_author(a.strip()):
                    candidates.append(k)

            for key in candidates:
                resolved = _resolve_key(key, author_dept, fuzzy_map)
                info = author_dept.get(resolved) if resolved else None
                if not info:
                    continue
                dept = info["dept"]
                staff_status = info["status"]
                if dept and dept not in depts_seen:
                    dept = info["dept"]
                    staff_status = info["status"]
                    if dept and dept not in depts_seen:
                        depts_seen.add(dept)
                        pub_dept_rows.append({
                            "pub_idx":      idx,
                            "department":   dept,
                            "staff_status": staff_status,
                            "citations":    int(row.get("citations", 0) or 0),
                            "quartile":     str(row.get("quartile", "") or ""),
                            "year":         row.get("year"),
                            "q1": 1 if row.get("quartile") == "Q1" else 0,
                            "q2": 1 if row.get("quartile") == "Q2" else 0,
                            "q3": 1 if row.get("quartile") == "Q3" else 0,
                            "q4": 1 if row.get("quartile") == "Q4" else 0,
                        })

        pub_dept_df = pd.DataFrame(pub_dept_rows)

        # Unique papers with at least one SDU academic author
        matched_pubs = pub_dept_df["pub_idx"].nunique() if not pub_dept_df.empty else 0

        # Active academic staff (normalized match keys)
        def _make_key(surname, name):
            first = next((c for c in _normalize_str(str(name).strip()) if c.isalpha()), '')
            return _normalize_str(str(surname).strip()) + ", " + first + "."

        active = t_raw[t_raw["STAFF_TYPE_EN"] == "Academic"].copy()
        active["match_key"] = active.apply(lambda r: _make_key(r["SURNAME"], r["NAME"]), axis=1)
        active = active.drop_duplicates(subset=["match_key", "DEPARTMENT_EN"])

        # ── Dept filter ────────────────────────────────────────────────────────
        all_depts = sorted(active["DEPARTMENT_EN"].dropna().unique().tolist())
        fac_dept = st.selectbox("Filter by Department", ["All departments"] + all_depts, key="fac_dept")

        if fac_dept == "All departments":
            active_view  = active
            pub_view     = pub_dept_df
            # only pubs that have at least one SDU author
            sdu_pub_idx  = pub_dept_df["pub_idx"].unique() if not pub_dept_df.empty else []
            pub_all_view = df[df.index.isin(sdu_pub_idx)]
            unknown_sdu = detect_unknown_sdu_papers(df, sdu_pub_idx)

        else:
            active_view  = active[active["DEPARTMENT_EN"] == fac_dept]
            pub_view     = pub_dept_df[pub_dept_df["department"] == fac_dept]
            dept_pub_idx = pub_view["pub_idx"].unique()
            pub_all_view = df[df.index.isin(dept_pub_idx)]

        # ── KPI row ────────────────────────────────────────────────────────────
        total_pubs   = len(pub_all_view)
        total_cites  = int(pub_all_view["citations"].sum())
        total_staff  = len(active_view)

        # publishing = staff whose normalized key appears in any pub author
        pub_norm_authors = set()
        for _, prow in pub_all_view.iterrows():
            for (lastname, firstname, *_) in (prow.get("author_full_list") or []):
                key = f"{_normalize_str(lastname)}, {_normalize_str(firstname)}"
                resolved = _resolve_key(key, author_dept, fuzzy_map)
                if resolved:
                    pub_norm_authors.add(resolved)
            for a in str(prow.get("authors","")).split(";"):
                for k in normalize_pub_author(a.strip()):
                    resolved = _resolve_key(k, author_dept, fuzzy_map)
                    if resolved:
                        pub_norm_authors.add(resolved)

        staff_keys      = set(active_view["match_key"])
        publishing      = len(staff_keys & pub_norm_authors)
        pub_rate        = int(publishing / total_staff * 100) if total_staff else 0
        phd_count       = int(active_view["DEGREE_EN"].str.contains("PhD|Doctor", na=False).sum())
        working_count   = int((active_view["STATUS_EN"] == "Working").sum()) if "STATUS_EN" in active_view.columns else total_staff
        not_working     = total_staff - working_count

        # pubs split by staff status
        if not pub_dept_df.empty and "staff_status" in pub_dept_df.columns:
            pubs_by_working    = pub_dept_df[pub_dept_df["staff_status"] == "Working"]["pub_idx"].nunique()
            pubs_by_ex         = pub_dept_df[pub_dept_df["staff_status"] != "Working"]["pub_idx"].nunique()
        else:
            pubs_by_working = total_pubs
            pubs_by_ex      = 0

        total_split = pubs_by_working + pubs_by_ex
        pubs_by_working_pct = round(pubs_by_working / total_split * 100) if total_split else 0
        pubs_by_ex_pct      = round(pubs_by_ex      / total_split * 100) if total_split else 0
        not_working_pct     = round(not_working / total_staff * 100) if total_staff else 0

        fk1, fk2, fk3, fk4, fk5 = st.columns(5)
        for col, label, val, sub, color in [
            (fk1, "Total Pubs",        total_pubs,                   "",                          "#e8eaf0"),
            (fk2, "Citations",         f"{total_cites:,}",           "",                          "#e8ff47"),
            (fk3, "Academic Staff",    total_staff,                  "",                          "#47c8ff"),
            (fk4, "Pubs by Working",   pubs_by_working,              f"{pubs_by_working_pct}% of pubs", "#47ffb8"),
            (fk5, "Pubs by Ex-Staff",  pubs_by_ex,                   f"{pubs_by_ex_pct}% of pubs",  "#ffa447"),
        ]:
            with col:
                st.markdown(f"""
                <div class="metric-card" style="height:110px;display:flex;flex-direction:column;justify-content:center;align-items:center;">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value" style="color:{color};font-size:32px;">{val}</div>
                    {f'<div class="metric-sub">{sub}</div>' if sub else ''}
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        
        unknown_view = unknown_sdu[
            ["title","authors","year","citations","doi","affiliations"]
            ].sort_values("citations", ascending=False)

        st.dataframe(unknown_view)

    
        # ── Dept aggregation ──────────────────────────────────────────────────
        if not pub_dept_df.empty:
            dept_pubs = pub_dept_df.groupby("department").agg(
                papers=("pub_idx", "nunique"),
                citations=("citations", "sum"),
                q1=("q1","sum"), q2=("q2","sum"), q3=("q3","sum"), q4=("q4","sum"),
            ).reset_index()
        else:
            dept_pubs = pd.DataFrame(columns=["department","papers","citations","q1","q2","q3","q4"])

        staff_counts = active.groupby("DEPARTMENT_EN").agg(
            staff=("match_key","count"),
        ).reset_index().rename(columns={"DEPARTMENT_EN":"department"})

        dept_stats = dept_pubs.merge(staff_counts, on="department", how="outer").fillna(0)
        dept_stats["pub_rate"] = (dept_stats["papers"] / dept_stats["staff"].replace(0,1) * 100).round(1)
        dept_stats["dept_short"] = dept_stats["department"].apply(
            lambda x: str(x).replace("Department of ","").replace("School of ","").replace("Center for ","")[:40]
        )

        # ── Row 1: Publications by dept + Publishing rate ─────────────────────
        r1a, r1b = st.columns(2)

        with r1a:
            st.markdown("<div class='section-label'>Publications by Department</div>", unsafe_allow_html=True)
            ds = dept_stats.sort_values("papers", ascending=True)
            fig_dp = go.Figure(go.Bar(
                x=ds["papers"], y=ds["dept_short"], orientation="h",
                marker_color=COLORS[0],
                customdata=ds[["citations","staff"]].values,
                hovertemplate="<b>%{y}</b><br>Papers: %{x}<br>Citations: %{customdata[0]}<br>Staff: %{customdata[1]}<extra></extra>",
            ))
            fig_dp.update_layout(**THEME, height=max(320, len(dept_stats)*30),
                xaxis=dict(**AXIS, title="Papers"),
                yaxis=dict(**AXIS_CAT), bargap=0.25)
            st.plotly_chart(fig_dp, use_container_width=True, config={"displayModeBar": False})

        with r1b:
            st.markdown("<div class='section-label'>Publishing Rate by Department (%)</div>", unsafe_allow_html=True)
            ds2 = dept_stats.sort_values("pub_rate", ascending=True)
            bar_colors = [
                "#e8ff47" if r >= 50 else "#ffa447" if r >= 25 else "#ff6b47"
                for r in ds2["pub_rate"]
            ]
            fig_pr = go.Figure(go.Bar(
                x=ds2["pub_rate"], y=ds2["dept_short"], orientation="h",
                marker_color=bar_colors,
                customdata=ds2[["papers","staff"]].values,
                hovertemplate="<b>%{y}</b><br>%{x:.1f}%<br>%{customdata[0]} papers · %{customdata[1]} staff<extra></extra>",
            ))
            fig_pr.add_vline(x=50, line_dash="dash", line_color="#4a5060",
                annotation_text="50%", annotation_font_color="#6b7385", annotation_font_size=9)
            fig_pr.update_layout(**THEME, height=max(320, len(dept_stats)*30),
                xaxis=dict(**AXIS, title="% of staff with publications", range=[0,105]),
                yaxis=dict(**AXIS_CAT), bargap=0.25)
            st.plotly_chart(fig_pr, use_container_width=True, config={"displayModeBar": False})

        # ── Row 2: Quartiles by dept + Degree breakdown ───────────────────────
        r2a, r2b = st.columns(2)

        with r2a:
            st.markdown("<div class='section-label'>Quartiles by Department</div>", unsafe_allow_html=True)
            ds3 = dept_stats.sort_values("q1", ascending=True)
            fig_dq = go.Figure()
            for q_col, q_label, q_color in [
                ("q1","Q1","#e8ff47"), ("q2","Q2","#47c8ff"),
                ("q3","Q3","#ffa447"), ("q4","Q4","#ff6b47"),
            ]:
                fig_dq.add_trace(go.Bar(
                    name=q_label, x=ds3[q_col], y=ds3["dept_short"],
                    orientation="h", marker_color=q_color,
                    hovertemplate=f"<b>%{{y}}</b><br>{q_label}: %{{x}}<extra></extra>",
                ))
            fig_dq.update_layout(**THEME, height=max(320, len(dept_stats)*30),
                barmode="stack", bargap=0.25,
                xaxis=dict(**AXIS, title="Papers with quartile"),
                yaxis=dict(**AXIS_CAT),
                legend=dict(orientation="h", x=0, y=1.04, bgcolor="rgba(0,0,0,0)",
                            font=dict(size=10, color="#e8eaf0")))
            st.plotly_chart(fig_dq, use_container_width=True, config={"displayModeBar": False})

        with r2b:
            st.markdown("<div class='section-label'>Degree Distribution</div>", unsafe_allow_html=True)
            deg_df = active_view[active_view["DEGREE_EN"].notna() & active_view["DEGREE_EN"].str.strip().ne("")].copy()
            deg_df["DEGREE_EN"] = deg_df["DEGREE_EN"].replace({
                "Candidate of Science": "Cand. Sci.",
                "Doctor of Science": "Dr. Sci.",
                "Doctor by profile": "Dr. (prof.)"
            })
            deg_counts = deg_df["DEGREE_EN"].value_counts().reset_index()
            deg_counts.columns = ["degree", "count"]
            fig_deg = go.Figure(go.Pie(
                labels=deg_counts["degree"], values=deg_counts["count"], hole=0.6,
                marker=dict(colors=COLORS[:len(deg_counts)], line=dict(color="#0a0c10", width=2)),
                hovertemplate="<b>%{label}</b><br>%{value} staff (%{percent})<extra></extra>",
                textinfo="none", sort=False,
            ))
            fig_deg.update_layout(**THEME, height=320, showlegend=True,
                legend=dict(font=dict(size=10, color="#e8eaf0"), bgcolor="rgba(0,0,0,0)",
                            orientation="h", x=0.05, y=-0.12))
            st.plotly_chart(fig_deg, use_container_width=True, config={"displayModeBar": False})

        # ── Row 3: Top publishers + Not publishing ────────────────────────────
        r3a, r3b = st.columns([1.4, 1.6])

        with r3a:
            st.markdown("<div class='section-label'>Top Publishing Staff</div>", unsafe_allow_html=True)
            rank_by = st.radio("Rank by", ["Papers", "Citations", "Q1+Q2"], horizontal=True, key="fac_rank")

            # Build per-author stats for staff in active_view
            fac_author_stats = {}
            for _, row in pub_all_view.iterrows():
                # collect candidate keys: full names first, then short
                candidates = []
                for (lastname, firstname, *_) in (row.get("author_full_list") or []):
                    candidates.append(f"{_normalize_str(lastname)}, {_normalize_str(firstname)}")
                for a in str(row.get("authors","")).split(";"):
                    for k in normalize_pub_author(a.strip()):
                        candidates.append(k)
                seen_norms = set()
                for norm in candidates:
                    resolved = _resolve_key(norm, author_dept, fuzzy_map)
                    if resolved is None or resolved in seen_norms:
                        continue
                    seen_norms.add(resolved)
                    if resolved not in fac_author_stats:
                        fac_author_stats[resolved] = {"papers":0,"citations":0,"q1":0,"q2":0,"position":"","dept":""}
                    fac_author_stats[resolved]["papers"] += 1
                    fac_author_stats[resolved]["citations"] += int(row.get("citations",0) or 0)
                    q = str(row.get("quartile","") or "")
                    if q == "Q1": fac_author_stats[resolved]["q1"] += 1
                    elif q == "Q2": fac_author_stats[resolved]["q2"] += 1

            # Attach position/dept from active
            for _, t in active_view.iterrows():
                k = t["match_key"]
                if k in fac_author_stats:
                    fac_author_stats[k]["position"] = str(t.get("POSITION_EN","") or "")
                    fac_author_stats[k]["dept"]     = str(t.get("DEPARTMENT_EN","") or "")

            rank_col = {"Papers":"papers","Citations":"citations","Q1+Q2":"q1q2"}[rank_by]
            staff_rows = []
            for name, s in fac_author_stats.items():
                s["q1q2"] = s["q1"] + s["q2"]
                s["name"] = name
                staff_rows.append(s)
            staff_rank_df = pd.DataFrame(staff_rows).sort_values(rank_col, ascending=False).head(15)

            if not staff_rank_df.empty:
                staff_rank_df["label"] = staff_rank_df["name"] + "  ·  " + staff_rank_df["dept"].apply(
                    lambda x: x.replace("Department of ","").replace("School of ","")[:25]
                )
                fig_ts = go.Figure(go.Bar(
                    x=staff_rank_df[rank_col], y=staff_rank_df["label"], orientation="h",
                    marker_color=COLORS[0],
                    customdata=staff_rank_df[["papers","citations","q1","q2","position"]].values,
                    hovertemplate="<b>%{y}</b><br>Papers: %{customdata[0]}<br>Citations: %{customdata[1]}<br>Q1: %{customdata[2]} · Q2: %{customdata[3]}<br>%{customdata[4]}<extra></extra>",
                ))
                fig_ts.update_layout(**THEME, height=400,
                    xaxis=dict(**AXIS, title=rank_by),
                    yaxis=dict(**AXIS_CAT, autorange="reversed"), bargap=0.25)
                st.plotly_chart(fig_ts, use_container_width=True, config={"displayModeBar": False})

        with r3b:
            st.markdown("<div class='section-label'>Staff Without Publications</div>", unsafe_allow_html=True)
            pub_authors_set = set(fac_author_stats.keys())
            no_pub_rows = []
            for _, t in active_view.iterrows():
                if t["match_key"] not in pub_authors_set:
                    no_pub_rows.append({"department": str(t.get("DEPARTMENT_EN","") or "")})
            no_pub_dept = (
                pd.DataFrame(no_pub_rows).groupby("department").size()
                .reset_index(name="count").sort_values("count", ascending=True)
            )
            no_pub_dept["dept_short"] = no_pub_dept["department"].apply(
                lambda x: x.replace("Department of ","").replace("School of ","").replace("Center for ","")[:40]
            )
            fig_np = go.Figure(go.Bar(
                x=no_pub_dept["count"], y=no_pub_dept["dept_short"],
                orientation="h", marker_color="#ff6b47",
                hovertemplate="<b>%{y}</b><br>%{x} staff without publications<extra></extra>",
            ))
            fig_np.update_layout(**THEME, height=400,
                xaxis=dict(**AXIS, title="Staff count"),
                yaxis=dict(**AXIS_CAT), bargap=0.3)
            st.plotly_chart(fig_np, use_container_width=True, config={"displayModeBar": False})

        # ── ENHANCED FACULTY ANALYSIS ─────────────────────────────────────────

        st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Advanced Faculty Analytics</div>", unsafe_allow_html=True)

        # ── Heatmap: Publications by Department × Year ────────────────────────
        if not pub_dept_df.empty:
            st.markdown("<div class='section-label' style='margin-top:8px;'>Publication Activity Heatmap (Department × Year)</div>", unsafe_allow_html=True)

            heat_df = (
                pub_dept_df.dropna(subset=["year"])
                .groupby(["department", "year"])["pub_idx"].nunique()
                .reset_index(name="papers")
            )
            heat_df["dept_short"] = heat_df["department"].apply(
                lambda x: str(x).replace("Department of ","").replace("School of ","").replace("Center for ","")[:35]
            )
            heat_pivot = heat_df.pivot(index="dept_short", columns="year", values="papers").fillna(0)
            heat_pivot = heat_pivot[sorted(heat_pivot.columns)]

            # Sort rows by total
            heat_pivot = heat_pivot.loc[heat_pivot.sum(axis=1).sort_values(ascending=False).index]

            fig_heat = go.Figure(go.Heatmap(
                z=heat_pivot.values.tolist(),
                x=[int(c) for c in heat_pivot.columns],
                y=heat_pivot.index.tolist(),
                colorscale=[[0,"#0a0c10"],[0.2,"#1a2e10"],[0.5,"#3a6020"],[0.8,"#88c840"],[1.0,"#e8ff47"]],
                hovertemplate="<b>%{y}</b><br>Year: %{x}<br>Papers: %{z}<extra></extra>",
                showscale=True,
                colorbar=dict(
                    tickfont=dict(color="#e8eaf0", family="DM Mono, monospace", size=10),
                    outlinecolor="#232836", outlinewidth=1,
                    bgcolor="#0a0c10",
                ),
            ))
            _theme_heat = {k: v for k, v in THEME.items() if k != "margin"}
            fig_heat.update_layout(
                **_theme_heat,
                height=max(380, len(heat_pivot) * 28),
                xaxis=dict(**YEAR_AXIS, title="Year"),
                yaxis=dict(**AXIS_CAT, title=""),
                margin=dict(t=20, b=40, l=10, r=80),
            )
            st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})

        # ── Publication Trend by Department ──────────────────────────────────
        if not pub_dept_df.empty:
            st.markdown("<div class='section-label' style='margin-top:8px;'>Publication Trend by Department</div>", unsafe_allow_html=True)

            trend_top_n = st.slider("Show top N departments", 3, 10, 6, key="fac_trend_n")

            top_dept_names = (
                pub_dept_df.groupby("department")["pub_idx"].nunique()
                .sort_values(ascending=False)
                .head(trend_top_n)
                .index.tolist()
            )

            trend_data = (
                pub_dept_df[pub_dept_df["department"].isin(top_dept_names)]
                .dropna(subset=["year"])
                .groupby(["department","year"])["pub_idx"].nunique()
                .reset_index(name="papers")
            )

            fig_trend = go.Figure()
            for i, dept_name in enumerate(top_dept_names):
                sub = trend_data[trend_data["department"] == dept_name].sort_values("year")
                short = str(dept_name).replace("Department of ","").replace("School of ","").replace("Center for ","")[:35]
                fig_trend.add_trace(go.Scatter(
                    x=sub["year"], y=sub["papers"],
                    mode="lines+markers",
                    name=short,
                    line=dict(color=COLORS[i % len(COLORS)], width=2),
                    marker=dict(size=6, color=COLORS[i % len(COLORS)]),
                    hovertemplate=f"<b>{short}</b><br>%{{x}}: %{{y}} papers<extra></extra>",
                ))
            fig_trend.update_layout(
                **THEME,
                height=340,
                xaxis=YEAR_AXIS,
                yaxis=dict(**AXIS, title="Papers"),
                legend=dict(
                    bgcolor="rgba(17,20,24,0.85)", bordercolor="#232836", borderwidth=1,
                    font=dict(size=9, color="#e8eaf0", family="DM Mono, monospace"),
                    orientation="v", x=1.01, y=1, xanchor="left",
                )
            )
            st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

        # ── Department Profile ────────────────────────────────────────────────
        st.markdown("<div class='section-label' style='margin-top:8px;'>Department Deep Dive</div>", unsafe_allow_html=True)

        drill_dept = st.selectbox(
            "Select department to analyze",
            sorted(active["DEPARTMENT_EN"].dropna().unique().tolist()),
            key="drill_dept"
        )

        drill_active = active[active["DEPARTMENT_EN"] == drill_dept]
        drill_pub_idx = pub_dept_df[pub_dept_df["department"] == drill_dept]["pub_idx"].unique() if not pub_dept_df.empty else []
        drill_pubs = df[df.index.isin(drill_pub_idx)]

        d_staff = len(drill_active)
        d_papers = len(drill_pubs)
        d_cites = int(drill_pubs["citations"].sum()) if d_papers > 0 else 0
        d_h = calc_h_index(drill_pubs["citations"]) if d_papers > 0 else 0
        d_q1 = int((drill_pubs["quartile"] == "Q1").sum()) if d_papers > 0 else 0
        d_oa = int(drill_pubs["open_access_bool"].sum()) if d_papers > 0 else 0

        dp1, dp2, dp3, dp4, dp5, dp6 = st.columns(6)
        for col, label, val, color in [
            (dp1, "Staff",      d_staff,              "#e8eaf0"),
            (dp2, "Papers",     d_papers,             "#e8ff47"),
            (dp3, "Citations",  f"{d_cites:,}",       "#47c8ff"),
            (dp4, "h-index",    d_h,                  "#a47fff"),
            (dp5, "Q1 Papers",  d_q1,                 "#47ffb8"),
            (dp6, "Open Access",d_oa,                 "#ff6b47"),
        ]:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value" style="color:{color};font-size:32px;">{val}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        if d_papers > 0:
            dd1, dd2 = st.columns(2)

            with dd1:
                st.markdown("<div class='section-label'>Top Keywords</div>", unsafe_allow_html=True)
                drill_kws = []
                for lst in drill_pubs["kw_list"]:
                    if isinstance(lst, list):
                        drill_kws.extend(lst)
                drill_kw_top = Counter([k.lower().strip() for k in drill_kws if k]).most_common(20)
                if drill_kw_top:
                    kw_names = [k.title() for k, _ in drill_kw_top]
                    kw_vals  = [v for _, v in drill_kw_top]
                    fig_dkw = go.Figure(go.Bar(
                        x=kw_vals[::-1], y=kw_names[::-1], orientation="h",
                        marker_color=COLORS[0],
                        hovertemplate="<b>%{y}</b><br>%{x} papers<extra></extra>",
                    ))
                    fig_dkw.update_layout(
                        **THEME, height=max(280, len(drill_kw_top)*22),
                        xaxis=dict(**AXIS, title="Frequency", dtick=1),
                        yaxis=dict(**AXIS_CAT), bargap=0.25,
                    )
                    st.plotly_chart(fig_dkw, use_container_width=True, config={"displayModeBar": False})

            with dd2:
                st.markdown("<div class='section-label'>Citations by Year</div>", unsafe_allow_html=True)
                if drill_pubs["year"].notna().any():
                    dc_trend = drill_pubs.groupby("year").agg(
                        papers=("citations","count"),
                        citations=("citations","sum"),
                    ).reset_index()
                    fig_dct = go.Figure()
                    fig_dct.add_trace(go.Bar(
                        x=dc_trend["year"], y=dc_trend["papers"],
                        name="Papers", marker_color="rgba(232,255,71,0.3)",
                        yaxis="y", hovertemplate="<b>%{x}</b><br>%{y} papers<extra></extra>",
                    ))
                    fig_dct.add_trace(go.Scatter(
                        x=dc_trend["year"], y=dc_trend["citations"],
                        name="Citations", mode="lines+markers",
                        line=dict(color=COLORS[1], width=2),
                        marker=dict(size=6, color=COLORS[1]),
                        yaxis="y2",
                        hovertemplate="<b>%{x}</b><br>%{y} citations<extra></extra>",
                    ))
                    fig_dct.update_layout(
                        **THEME, height=320, bargap=0.2,
                        xaxis=YEAR_AXIS,
                        yaxis=dict(**AXIS, title="Papers", dtick=1),
                        yaxis2=dict(overlaying="y", side="right", title="Citations",
                                    tickfont=dict(color="#47c8ff"), title_font=dict(color="#47c8ff"),
                                    gridcolor="rgba(0,0,0,0)"),
                        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e8eaf0"),
                                    x=0, y=1.1, orientation="h"),
                    )
                    st.plotly_chart(fig_dct, use_container_width=True, config={"displayModeBar": False})

            # ── Quartile breakdown ────────────────────────────────────────────
            if drill_pubs["quartile"].notna().any():
                dq1, dq2 = st.columns(2)
                q_counts_d = drill_pubs["quartile"].dropna().value_counts().reindex(["Q1","Q2","Q3","Q4"]).fillna(0)
                q_colors_d = [QUARTILE_COLORS[q][0] for q in ["Q1","Q2","Q3","Q4"]]

                with dq1:
                    st.markdown("<div class='section-label'>Quartile Distribution</div>", unsafe_allow_html=True)
                    fig_dqpie = go.Figure(go.Pie(
                        labels=q_counts_d.index.tolist(),
                        values=q_counts_d.values.tolist(),
                        hole=0.6,
                        marker=dict(colors=q_colors_d, line=dict(color="#0a0c10", width=2)),
                        hovertemplate="<b>%{label}</b><br>%{value} papers (%{percent})<extra></extra>",
                        textinfo="none", sort=False,
                    ))
                    fig_dqpie.update_layout(**THEME, height=260, showlegend=True,
                        legend=dict(font=dict(size=11, color="#e8eaf0"), bgcolor="rgba(0,0,0,0)",
                                    orientation="h", x=0.1, y=-0.1))
                    st.plotly_chart(fig_dqpie, use_container_width=True, config={"displayModeBar": False})

                with dq2:
                    st.markdown("<div class='section-label'>Quartile by Year</div>", unsafe_allow_html=True)
                    dq_year = drill_pubs[drill_pubs["quartile"].notna()].groupby(["year","quartile"]).size().unstack(fill_value=0)
                    dq_year = dq_year.reindex(columns=["Q1","Q2","Q3","Q4"], fill_value=0)
                    dq_year.index = dq_year.index.astype(int).astype(str)
                    fig_dqy = go.Figure()
                    for q, color in zip(["Q1","Q2","Q3","Q4"], q_colors_d):
                        if q in dq_year.columns:
                            fig_dqy.add_trace(go.Bar(
                                name=q, x=dq_year.index.tolist(), y=dq_year[q].tolist(),
                                marker_color=color,
                                hovertemplate=f"<b>{q}</b> %{{x}}<br>%{{y}} papers<extra></extra>",
                            ))
                    fig_dqy.update_layout(**THEME, height=260, barmode="stack", bargap=0.15,
                        xaxis=dict(**AXIS_CAT, title="Year"),
                        yaxis=dict(**AXIS, dtick=1),
                        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color="#e8eaf0"),
                                    orientation="h", x=0, y=1.12))
                    st.plotly_chart(fig_dqy, use_container_width=True, config={"displayModeBar": False})

            # Top papers for this department
            st.markdown("<div class='section-label' style='margin-top:8px;'>Top Papers</div>", unsafe_allow_html=True)
            drill_top = drill_pubs.nlargest(5, "citations")
            for i, (_, row) in enumerate(drill_top.iterrows()):
                authors_str = fmt_authors(row.get("authors", ""))
                kws = row["kw_list"][:4] if row["kw_list"] else []
                kw_html = "".join([f"<span class='kw-tag'>{k}</span>" for k in kws])
                doi_str = str(row.get("doi", "")).split(";")[0].split(",")[0].strip()
                doi_str_clean = doi_str.split("\n")[0].strip()
                doi_link = f'<a href="https://doi.org/{doi_str_clean}" target="_blank" style="color:#6b7385;font-size:10px;font-family:DM Mono,monospace;text-decoration:none;">↗ {doi_str_clean[:40]}</a>' if doi_str_clean and doi_str_clean.lower() not in ("nan","none","","n/a","-") else ""
                bc = [COLORS[0], COLORS[1], COLORS[2], COLORS[3], COLORS[4]][i % 5]
                q_b = quartile_full_display(row)
                st.markdown(f"""
                <div style="background:#111418;border:1px solid #1e2230;border-left:3px solid {bc};
                            padding:14px 18px;margin-bottom:8px;border-radius:0 4px 4px 0;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
                        <div style="flex:1;">
                            <div style="font-size:13px;line-height:1.5;color:#e8eaf0;margin-bottom:4px;">{row['title']}</div>
                            <div style="font-size:11px;color:{bc};font-style:italic;margin-bottom:5px;">{authors_str}</div>
                            <div style="font-family:DM Mono,monospace;font-size:10px;color:#6b7385;margin-bottom:6px;">
                                {int(row['year'])} · {str(row['journal'])[:55]}{'…' if len(str(row['journal']))>55 else ''}
                            </div>
                            <div>{q_b}{kw_html}</div>
                            <div style="margin-top:4px;">{doi_link}</div>
                        </div>
                        <div style="text-align:right;min-width:60px;">
                            <div style="font-family:Bebas Neue,sans-serif;font-size:36px;color:{bc};line-height:1;">{row['citations']}</div>
                            <div style="font-family:DM Mono,monospace;font-size:9px;color:#6b7385;">CITED</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

            # Staff list for this department
            st.markdown("<div class='section-label' style='margin-top:8px;'>Department Staff</div>", unsafe_allow_html=True)
            drill_staff_rows = []
            for _, t in drill_active.iterrows():
                k = t["match_key"]
                s = fac_author_stats.get(k, {"papers":0,"citations":0,"q1":0,"q2":0,"q1q2":0})
                drill_staff_rows.append({
                    "Name":      str(t["SURNAME"]) + " " + str(t["NAME"]),
                    "Status":   str(t.get("STATUS_EN","") or ""),
                    "Position":  str(t.get("POSITION_EN","") or ""),
                    "Degree":    str(t.get("DEGREE_EN","") or ""),
                    "Papers":    s.get("papers",0),
                    "Citations": s.get("citations",0),
                    "Q1":        s.get("q1",0),
                })
            drill_staff_df = pd.DataFrame(drill_staff_rows).sort_values(["Status", "Papers"], ascending=[False, False])

            def _staff_row_color(row):
                if row["Status"] != "Working":
                    return ["background-color:#1a1020; color:#9a7a9a"] * len(row)
                return [""] * len(row)

            st.dataframe(
                drill_staff_df.style.apply(_staff_row_color, axis=1),
                use_container_width=True, height=320, hide_index=True
            )
            st.markdown(
                "<div style='font-family:DM Mono,monospace;font-size:10px;color:#6b7385;margin-top:6px;'>"
                "🟣 No longer working &nbsp;&nbsp; ⬜ Currently working</div>",
                unsafe_allow_html=True
            )

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:48px;padding-top:20px;border-top:1px solid #232836;display:flex;justify-content:space-between;">
    <p style="font-family:DM Mono,monospace;font-size:11px;color:#6b7385;">Data source: Scopus</p>
    <p style="font-family:DM Mono,monospace;font-size:11px;color:#6b7385;">SDU University · Data Analytics Lab</p>
</div>
""", unsafe_allow_html=True)