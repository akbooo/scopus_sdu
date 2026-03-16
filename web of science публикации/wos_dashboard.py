import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from collections import Counter
import numpy as np

st.set_page_config(
    page_title="WoS Research Analytics",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&family=Space+Grotesk:wght@300;400;600&display=swap');

html, body, [class*="css"] { background-color: #080b12; color: #e4e8f0; }
h1, h2, h3 { font-family: 'Bebas Neue', sans-serif; letter-spacing: 0.05em; }

[data-testid="stSidebar"] { background-color: #0e1117 !important; border-right: 1px solid #1e2535; }
[data-testid="stSidebar"] * { color: #e4e8f0 !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stMultiSelect label { color: #e4e8f0 !important; }

[data-baseweb="select"] * { color: #e4e8f0 !important; }
[data-baseweb="select"] [data-baseweb="tag"] { background: #1e2535 !important; }
[data-baseweb="select"] [data-baseweb="tag"] span { color: #47f7c8 !important; }
[data-baseweb="menu"] { background-color: #0e1117 !important; }
[data-baseweb="option"] { background-color: #e4e8f0 !important; color: #080b12 !important; }
[data-baseweb="option"]:hover { background-color: #47f7c8 !important; }
[data-baseweb="popover"] { background-color: #e4e8f0 !important; }
[data-baseweb="popover"] * { color: #080b12 !important; }
ul[role="listbox"] { background-color: #e4e8f0 !important; }
ul[role="listbox"] li, ul[role="listbox"] li span { color: #080b12 !important; }

.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"],
[data-testid="stThumbValue"] { color: #e4e8f0 !important; }

[data-testid="stSidebar"] .stCheckbox label p {
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
}

[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: none !important;
    color: #4a5568 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 2px 0 !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    color: #47f7c8 !important;
    background: transparent !important;
}

[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p { color: #e4e8f0 !important; }

.stTextInput input {
    background-color: #0e1117 !important; color: #e4e8f0 !important;
    border: 1px solid #1e2535 !important; border-radius: 4px !important;
}
.stTextInput input:focus { border-color: #47f7c8 !important; box-shadow: none !important; }
.stTextInput input::placeholder { color: #4a5568 !important; }

.stTabs [data-baseweb="tab-list"] {
    background-color: #080b12 !important; border-bottom: 1px solid #1e2535 !important; gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background-color: #0e1117 !important;
    border: 1px solid #1e2535 !important; border-radius: 2px 2px 0 0 !important;
    font-family: 'DM Mono', monospace !important; font-size: 10px !important;
    letter-spacing: 0.15em !important; text-transform: uppercase !important; padding: 8px 20px !important;
}
.stTabs [data-baseweb="tab"] span,
.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] div { color: #4a5568 !important; }
.stTabs [aria-selected="true"] {
    background-color: #1e2535 !important; border-bottom-color: #1e2535 !important;
}
.stTabs [aria-selected="true"] span,
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] div { color: #47f7c8 !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 24px !important; }

.stDownloadButton button {
    background-color: #0e1117 !important; color: #47f7c8 !important;
    border: 1px solid #47f7c8 !important;
    font-family: 'DM Mono', monospace !important; font-size: 11px !important;
    letter-spacing: 0.1em !important; border-radius: 2px !important; padding: 6px 16px !important;
}
.stDownloadButton button:hover { background-color: #47f7c8 !important; color: #080b12 !important; }

.metric-card {
    background: #0e1117; border: 1px solid #1e2535;
    padding: 20px 24px; border-radius: 4px; text-align: center;
}
.metric-label {
    font-family: 'DM Mono', monospace; font-size: 10px;
    letter-spacing: 0.2em; text-transform: uppercase; color: #4a5568; margin-bottom: 6px;
}
.metric-value { font-family: 'Bebas Neue', sans-serif; font-size: 48px; line-height: 1; }
.metric-sub { font-family: 'DM Mono', monospace; font-size: 12px; color: #4a5568; margin-top: 4px; }

.section-label {
    font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.25em;
    text-transform: uppercase; color: #4a5568;
    border-bottom: 1px solid #1e2535; padding-bottom: 8px; margin-bottom: 20px;
}
.filter-header {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #4a5568;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid #1e2535;
}
.kw-tag {
    display: inline-block; padding: 3px 9px; margin: 2px;
    border-radius: 2px; font-family: 'DM Mono', monospace;
    font-size: 10px; letter-spacing: 0.05em;
    background: #141b28; border: 1px solid #1e2e45; color: #a0aabb;
}
.paper-row {
    background: #0e1117; border: 1px solid #1e2535;
    border-left: 3px solid #47f7c8;
    padding: 16px 20px; margin-bottom: 10px; border-radius: 0 4px 4px 0;
}
.hindex-box {
    background: #0e1117; border: 1px solid #1e2535; padding: 24px 28px;
    border-radius: 4px; text-align: center; position: relative; overflow: hidden;
}
.hindex-box::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 3px; height: 100%; background: var(--accent-color, #47f7c8);
}
.hindex-num { font-family: 'Bebas Neue', sans-serif; font-size: 64px; line-height: 1; }
.hindex-label { font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; color: #4a5568; margin-top: 4px; }

div[role="radiogroup"] { gap: 0.5rem; }
div[role="radiogroup"] > label {
    padding: 0.55rem 1rem; border-radius: 999px;
    background: #0e1117 !important; transition: 0.2s ease;
    border: 1px solid #1e2535 !important;
}
div[role="radiogroup"] > label:hover { border-color: #47f7c8 !important; background: #141b28 !important; }
div[role="radiogroup"] > label[aria-checked="true"] {
    background: #47f7c8 !important; border-color: #47f7c8 !important;
}
div[role="radiogroup"] > label[aria-checked="true"] * { color: #080b12 !important; font-weight: 600 !important; }
div[role="radiogroup"] > label * { color: #e4e8f0 !important; }
/* Extra specificity to override Streamlit defaults */
[data-testid="stRadio"] { background: transparent !important; }
[data-testid="stRadio"] div[role="radiogroup"] label { background: #0e1117 !important; }
[data-testid="stRadio"] div[role="radiogroup"] label * { color: #e4e8f0 !important; }
[data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] { background: #47f7c8 !important; }
[data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] * { color: #080b12 !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# ── PLOTLY THEME ───────────────────────────────────────────────────────────────
THEME = dict(
    paper_bgcolor="#080b12", plot_bgcolor="#080b12",
    font=dict(family="DM Mono, monospace", color="#e4e8f0", size=11),
    margin=dict(t=20, b=40, l=10, r=10),
)
AXIS = dict(gridcolor="#1a2030", linecolor="#1e2535", tickcolor="#1e2535",
            tickfont=dict(color="#e4e8f0"), title_font=dict(color="#e4e8f0"), tickformat="d")
AXIS_CAT = dict(gridcolor="#1a2030", linecolor="#1e2535", tickcolor="#1e2535",
                tickfont=dict(color="#e4e8f0"), title_font=dict(color="#e4e8f0"))
YEAR_AXIS = dict(gridcolor="#1a2030", linecolor="#1e2535", tickcolor="#1e2535",
                 tickfont=dict(color="#e4e8f0"), title_font=dict(color="#e4e8f0"),
                 tickmode="linear", dtick=1, tickformat="d")
COLORS = ["#47f7c8", "#f7e147", "#f76b47", "#a47fff", "#47c8ff",
          "#ff47a4", "#ffa447", "#4778ff", "#ff4747", "#47ffd4"]

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("fdf.csv")
    df.columns = [c.strip() for c in df.columns]

    # Focus on journal/book publications only
    df = df[df["Publication Type"].isin(["J", "B", "S"])].copy()

    df = df.rename(columns={
        "Article Title": "title",
        "Authors": "authors",
        "Source Title": "journal",
        "Publication Year": "year",
        "Times Cited, WoS Core": "citations_wos",
        "Times Cited, All Databases": "citations_all",
        "180 Day Usage Count": "usage_180",
        "Since 2013 Usage Count": "usage_2013",
        "Document Type": "doc_type",
        "Author Keywords": "keywords",
        "DOI": "doi",
        "Abstract": "abstract",
        "Conference Title": "conference",
        "Grant Number": "grant_number",
        "ISSN": "issn",
        "Language": "language",
    })

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["citations_wos"] = pd.to_numeric(df["citations_wos"], errors="coerce").fillna(0).astype(int)
    df["citations_all"] = pd.to_numeric(df["citations_all"], errors="coerce").fillna(0).astype(int)
    df["usage_180"] = pd.to_numeric(df["usage_180"], errors="coerce").fillna(0).astype(int)

    def parse_kw(s):
        if pd.isna(s): return []
        return [k.strip() for k in str(s).split(";") if k.strip()]
    df["kw_list"] = df["keywords"].apply(parse_kw) if "keywords" in df.columns else [[]] * len(df)

    def parse_authors(s):
        if pd.isna(s): return []
        return [a.strip() for a in str(s).split(";") if a.strip()]
    df["author_list"] = df["authors"].apply(parse_authors)
    df["n_authors"] = df["author_list"].apply(len)

    return df

df = load_data()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def calc_h_index(series):
    cites = sorted(series.tolist(), reverse=True)
    h = 0
    for i, c in enumerate(cites):
        if c >= i + 1: h = i + 1
        else: break
    return h

def calc_g_index(series):
    cites = sorted(series.tolist(), reverse=True)
    g, cs = 0, 0
    for i, c in enumerate(cites):
        cs += c
        if cs >= (i + 1) ** 2: g = i + 1
    return g

def fmt_authors(s, n=5):
    parts = [a.strip() for a in str(s).split(";") if a.strip()]
    if not parts: return "—"
    if len(parts) > n: return ", ".join(parts[:n]) + " et al."
    return ", ".join(parts)

def tier_badge(cite):
    if cite >= 50:
        return "<span style='background:#f7e147;color:#1a1a00;font-family:DM Mono,monospace;font-size:10px;font-weight:700;padding:2px 8px;border-radius:2px;'>🔥 TOP</span>"
    if cite >= 15:
        return "<span style='background:#47c8ff;color:#001a22;font-family:DM Mono,monospace;font-size:10px;font-weight:700;padding:2px 8px;border-radius:2px;'>⭐ HOT</span>"
    if cite >= 3:
        return "<span style='background:#1e2535;color:#47f7c8;font-family:DM Mono,monospace;font-size:10px;font-weight:700;padding:2px 8px;border-radius:2px;border:1px solid #47f7c8'>✓ OK</span>"
    return "<span style='background:#111420;color:#4a5568;font-family:DM Mono,monospace;font-size:10px;padding:2px 8px;border-radius:2px;border:1px solid #1e2535'>— LOW</span>"

# ── PRECOMPUTE ─────────────────────────────────────────────────────────────────
year_counts = df.groupby("year").size().sort_index(ascending=False)
all_years = [y for y in year_counts.index.tolist() if pd.notna(y)]

author_counter = Counter()
for lst in df["author_list"]:
    for a in lst:
        author_counter[a] += 1

journal_counter = df["journal"].dropna().value_counts()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 style='color:#47f7c8;font-size:28px;letter-spacing:0.05em;"
        "font-family:Bebas Neue,sans-serif;'>FILTERS</h2>",
        unsafe_allow_html=True,
    )

    # Year filter
    st.markdown("<div class='filter-header'>Year</div>", unsafe_allow_html=True)
    YEAR_SHOW = 6
    if "show_all_years" not in st.session_state:
        st.session_state.show_all_years = False
    if "selected_years" not in st.session_state:
        st.session_state.selected_years = set()

    display_years = all_years if st.session_state.show_all_years else all_years[:YEAR_SHOW]
    for y in display_years:
        if pd.notna(y):
            cnt = year_counts.get(y, 0)
            checked = st.checkbox(f"{int(y)}  ({cnt})", key=f"yr_{y}",
                                  value=(y in st.session_state.selected_years))
            if checked: st.session_state.selected_years.add(y)
            else: st.session_state.selected_years.discard(y)

    if len(all_years) > YEAR_SHOW:
        lbl = "Show less ↑" if st.session_state.show_all_years else f"Show more ↓"
        if st.button(lbl, key="btn_years"):
            st.session_state.show_all_years = not st.session_state.show_all_years

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Document type filter
    st.markdown("<div class='filter-header'>Document Type</div>", unsafe_allow_html=True)
    if "selected_doctypes" not in st.session_state:
        st.session_state.selected_doctypes = set()
    top_doctypes = df["doc_type"].dropna().value_counts().head(8)
    for dt, cnt in top_doctypes.items():
        short = dt[:30] + "…" if len(dt) > 30 else dt
        checked = st.checkbox(f"{short}  ({cnt})", key=f"dt_{dt}",
                              value=(dt in st.session_state.selected_doctypes))
        if checked: st.session_state.selected_doctypes.add(dt)
        else: st.session_state.selected_doctypes.discard(dt)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Citations range
    st.markdown("<div class='filter-header'>Min. Citations (WoS)</div>", unsafe_allow_html=True)
    min_cite = st.slider("", 0, 100, 0, label_visibility="collapsed", key="min_cite_slider")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("↺ Reset all filters", key="reset_btn"):
        st.session_state.selected_years = set()
        st.session_state.selected_doctypes = set()
        st.session_state.min_cite_slider = 0
        st.rerun()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-family:DM Mono,monospace;font-size:10px;color:#4a5568;'>Source: Web of Science</p>",
        unsafe_allow_html=True,
    )

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
mask = pd.Series([True] * len(df), index=df.index)

if st.session_state.selected_years:
    mask &= df["year"].isin(st.session_state.selected_years)

if st.session_state.selected_doctypes:
    mask &= df["doc_type"].isin(st.session_state.selected_doctypes)

mask &= df["citations_wos"] >= min_cite

fdf = df[mask].copy()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:8px 0 28px">
    <p style="font-family:DM Mono,monospace;font-size:11px;letter-spacing:0.2em;text-transform:uppercase;color:#4a5568;">
        Web of Science · Research Analytics
    </p>
    <h1 style="font-size:64px;line-height:0.95;margin:8px 0 0;">
        PUBLICATION <span style="color:#47f7c8;">DASHBOARD</span>
    </h1>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
h_idx = calc_h_index(fdf["citations_wos"])
g_idx = calc_g_index(fdf["citations_wos"])
top_cited = int((fdf["citations_wos"] >= 50).sum())

k1, k2, k3, k4, k5, k6 = st.columns(6)
kpis = [
    (k1, "Publications",    len(fdf),                               f"Indexed in WoS",    "#e4e8f0"),
    (k2, "Citations",       f"{fdf['citations_wos'].sum():,}",       f"WoS Core",          "#47f7c8"),
    (k3, "Avg / Paper",     f"{fdf['citations_wos'].mean():.1f}",   "Citations per paper", "#f7e147"),
    (k4, "h-index",         h_idx,                                  "Hirsch index",        "#a47fff"),
    (k5, "g-index",         g_idx,                                  "g-index",             "#47c8ff"),
    (k6, "Top Papers",      top_cited,                              "≥50 citations",        "#f76b47"),
]
for col, label, val, sub, color in kpis:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color};">{val}</div>
            <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

# ── NAVIGATION ────────────────────────────────────────────────────────────────
st.markdown("<div style='border-top:2px solid #1e2535;margin-bottom:24px;'></div>", unsafe_allow_html=True)
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "📊 OVERVIEW"

tab = st.radio(
    "nav",
    ["📊 OVERVIEW", "👤 AUTHORS", "📰 JOURNALS", "🔍 PAPERS", "📈 INDEXES", "🤝 CO-AUTHORSHIP"],
    horizontal=True,
    key="active_tab",
    label_visibility="collapsed",
)
st.markdown("<div style='border-top:2px solid #47f7c8;margin-top:12px;margin-bottom:24px;'></div>",
            unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if tab == "📊 OVERVIEW":

    ov1, ov2 = st.columns([2, 1])
    with ov1:
        st.markdown("<div class='section-label'>Publications by Year</div>", unsafe_allow_html=True)
        yc = fdf.groupby("year").size().reset_index(name="count")
        yc = yc[yc["year"].notna()]
        yc["year"] = yc["year"].astype(int)
        fig = go.Figure(go.Bar(
            x=yc["year"], y=yc["count"],
            marker_color=COLORS[0],
            hovertemplate="<b>%{x}</b><br>%{y} publications<extra></extra>",
        ))
        fig.update_layout(**THEME, height=300, bargap=0.15, xaxis=YEAR_AXIS, yaxis=AXIS)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with ov2:
        st.markdown("<div class='section-label'>Document Types</div>", unsafe_allow_html=True)
        tc = fdf["doc_type"].dropna().value_counts().head(8).reset_index()
        tc.columns = ["type", "count"]
        fig2 = go.Figure(go.Pie(
            labels=tc["type"], values=tc["count"], hole=0.62,
            marker=dict(colors=COLORS[:len(tc)], line=dict(color="#080b12", width=2)),
            hovertemplate="<b>%{label}</b><br>%{value} papers (%{percent})<extra></extra>",
            textinfo="none",
        ))
        fig2.update_layout(**THEME, height=300, showlegend=True,
            legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.2,
                        font=dict(size=10, color="#e4e8f0"), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    ov3, ov4 = st.columns(2)
    with ov3:
        st.markdown("<div class='section-label'>Citation Trend by Year</div>", unsafe_allow_html=True)
        ct = fdf[fdf["year"].notna()].groupby("year").agg(
            papers=("citations_wos", "count"),
            citations=("citations_wos", "sum"),
        ).reset_index()
        ct["year"] = ct["year"].astype(int)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=ct["year"], y=ct["papers"], name="Papers",
            marker_color="rgba(71,247,200,0.25)", yaxis="y",
            hovertemplate="<b>%{x}</b><br>%{y} papers<extra></extra>",
        ))
        fig3.add_trace(go.Scatter(
            x=ct["year"], y=ct["citations"], name="Citations",
            mode="lines+markers", line=dict(color=COLORS[1], width=2),
            marker=dict(size=6, color=COLORS[1]), yaxis="y2",
            hovertemplate="<b>%{x}</b><br>%{y} citations<extra></extra>",
        ))
        fig3.update_layout(
            **THEME, height=300, bargap=0.2,
            xaxis=YEAR_AXIS,
            yaxis=dict(**AXIS, title="Papers"),
            yaxis2=dict(overlaying="y", side="right", title="Citations",
                        tickfont=dict(color=COLORS[1]), title_font=dict(color=COLORS[1]),
                        gridcolor="rgba(0,0,0,0)"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e4e8f0"),
                        x=0, y=1.1, orientation="h"),
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with ov4:
        st.markdown("<div class='section-label'>Citation Distribution</div>", unsafe_allow_html=True)
        fdf_copy = fdf.copy()
        def cite_bin(c):
            if c == 0: return "0 (uncited)"
            if c <= 3: return "1–3"
            if c <= 15: return "4–15"
            if c <= 50: return "16–50"
            return "50+"
        fdf_copy["cite_bin"] = fdf_copy["citations_wos"].apply(cite_bin)
        labels = ["0 (uncited)", "1–3", "4–15", "16–50", "50+"]
        bc = fdf_copy["cite_bin"].value_counts().reindex(labels).fillna(0).reset_index()
        bc.columns = ["bin", "count"]
        fig4 = go.Figure(go.Bar(
            x=bc["bin"], y=bc["count"],
            marker_color=[COLORS[3], COLORS[2], COLORS[4], COLORS[1], COLORS[0]],
            hovertemplate="<b>%{x}</b><br>%{y} papers<extra></extra>",
        ))
        fig4.update_layout(**THEME, height=300, bargap=0.2,
                           xaxis=AXIS_CAT, yaxis=AXIS)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

    # Top papers table
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Most Cited Papers</div>", unsafe_allow_html=True)
    top10 = fdf.nlargest(10, "citations_wos")
    for i, (_, row) in enumerate(top10.iterrows()):
        cite = int(row["citations_wos"])
        doi_str = str(row.get("doi", "") or "").strip()
        doi_link = ""
        if doi_str and doi_str.lower() not in ("nan", "none", "", "n/a"):
            doi_link = f'<a href="https://doi.org/{doi_str}" target="_blank" style="color:#4a5568;font-size:10px;font-family:DM Mono,monospace;text-decoration:none;">↗ {doi_str[:45]}</a>'
        bc_color = COLORS[i % len(COLORS)]
        st.markdown(f"""
        <div style="background:#0e1117;border:1px solid #1e2535;border-left:3px solid {bc_color};
                    padding:14px 18px;margin-bottom:8px;border-radius:0 4px 4px 0;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
                <div style="flex:1;">
                    <div style="font-size:13px;line-height:1.5;color:#e4e8f0;margin-bottom:4px;">{row['title']}</div>
                    <div style="font-size:11px;color:{bc_color};font-style:italic;margin-bottom:5px;">{fmt_authors(row.get('authors',''))}</div>
                    <div style="font-family:DM Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:6px;">
                        {int(row['year']) if pd.notna(row['year']) else '?'} · {str(row.get('journal',''))[:60]}
                    </div>
                    <div>{tier_badge(cite)}</div>
                    <div style="margin-top:4px;">{doi_link}</div>
                </div>
                <div style="text-align:right;min-width:60px;">
                    <div style="font-family:Bebas Neue,sans-serif;font-size:40px;color:{bc_color};line-height:1;">{cite}</div>
                    <div style="font-family:DM Mono,monospace;font-size:9px;color:#4a5568;">CITED</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.download_button(
        "⬇ Download filtered data (CSV)",
        fdf[["title", "authors", "journal", "year", "citations_wos", "citations_all", "doc_type", "doi"]].to_csv(index=False).encode("utf-8"),
        file_name="wos_filtered.csv",
        mime="text/csv",
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — AUTHORS
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "👤 AUTHORS":

    # Build per-author stats
    rows = []
    for _, row in fdf.iterrows():
        for author in row["author_list"]:
            rows.append({
                "author": author,
                "citations": int(row["citations_wos"]),
                "year": row["year"],
                "title": row["title"],
                "journal": row.get("journal", ""),
                "doi": row.get("doi", ""),
            })
    adf = pd.DataFrame(rows)

    if adf.empty:
        st.info("No author data for current filters.")
    else:
        author_stats = (
            adf.groupby("author")
            .agg(papers=("title", "count"), citations=("citations", "sum"))
            .reset_index()
        )
        author_stats["avg_cite"] = (author_stats["citations"] / author_stats["papers"]).round(1)
        author_stats["h_index"] = author_stats["author"].apply(
            lambda a: calc_h_index(adf[adf["author"] == a]["citations"])
        )

        au1, au2 = st.columns([1, 1])
        with au1:
            st.markdown("<div class='section-label'>Top Authors by Citations</div>", unsafe_allow_html=True)
            top_au = author_stats.nlargest(20, "citations")
            fig_au = go.Figure(go.Bar(
                x=top_au["citations"],
                y=top_au["author"],
                orientation="h",
                marker_color=COLORS[0],
                hovertemplate="<b>%{y}</b><br>%{x} citations<extra></extra>",
            ))
            fig_au.update_layout(**THEME, height=520,
                                 xaxis=AXIS, yaxis=dict(**AXIS_CAT, autorange="reversed"),
                                 bargap=0.25)
            st.plotly_chart(fig_au, use_container_width=True, config={"displayModeBar": False})

        with au2:
            st.markdown("<div class='section-label'>Top Authors by Papers</div>", unsafe_allow_html=True)
            top_pp = author_stats.nlargest(20, "papers")
            fig_pp = go.Figure(go.Bar(
                x=top_pp["papers"],
                y=top_pp["author"],
                orientation="h",
                marker_color=COLORS[1],
                hovertemplate="<b>%{y}</b><br>%{x} papers<extra></extra>",
            ))
            fig_pp.update_layout(**THEME, height=520,
                                 xaxis=AXIS, yaxis=dict(**AXIS_CAT, autorange="reversed"),
                                 bargap=0.25)
            st.plotly_chart(fig_pp, use_container_width=True, config={"displayModeBar": False})

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-label'>Author Deep Dive</div>", unsafe_allow_html=True)

        top_authors_list = author_stats.nlargest(200, "citations")["author"].tolist()
        sel_author = st.selectbox("Select author", top_authors_list, key="sel_author")

        if sel_author:
            aut_pubs = adf[adf["author"] == sel_author].copy()
            a_stats = author_stats[author_stats["author"] == sel_author].iloc[0]
            a_h = calc_h_index(aut_pubs["citations"])
            a_g = calc_g_index(aut_pubs["citations"])

            ac1, ac2, ac3, ac4 = st.columns(4)
            for c, lbl, v, col in [
                (ac1, "Papers",    a_stats["papers"],    "#e4e8f0"),
                (ac2, "Citations", a_stats["citations"], "#47f7c8"),
                (ac3, "h-index",   a_h,                 "#a47fff"),
                (ac4, "g-index",   a_g,                 "#f7e147"),
            ]:
                with c:
                    st.markdown(f"""
                    <div class="hindex-box" style="--accent-color:{col}">
                        <div class="hindex-num" style="color:{col}">{v}</div>
                        <div class="hindex-label">{lbl}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            # Year trend for this author
            if aut_pubs["year"].notna().any():
                ay = aut_pubs.groupby("year").agg(papers=("citations", "count"), cites=("citations", "sum")).reset_index()
                ay["year"] = ay["year"].astype(int)
                fig_ay = go.Figure()
                fig_ay.add_trace(go.Bar(x=ay["year"], y=ay["papers"], name="Papers",
                                        marker_color="rgba(71,247,200,0.3)", yaxis="y",
                                        hovertemplate="<b>%{x}</b><br>%{y} papers<extra></extra>"))
                fig_ay.add_trace(go.Scatter(x=ay["year"], y=ay["cites"], name="Citations",
                                            mode="lines+markers", line=dict(color=COLORS[1], width=2),
                                            marker=dict(size=6), yaxis="y2",
                                            hovertemplate="<b>%{x}</b><br>%{y} citations<extra></extra>"))
                fig_ay.update_layout(
                    **THEME, height=240, bargap=0.2,
                    xaxis=YEAR_AXIS,
                    yaxis=dict(**AXIS, title="Papers", dtick=1),
                    yaxis2=dict(overlaying="y", side="right", title="Citations",
                                tickfont=dict(color=COLORS[1]), title_font=dict(color=COLORS[1]),
                                gridcolor="rgba(0,0,0,0)"),
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e4e8f0"), x=0, y=1.12, orientation="h"),
                )
                st.plotly_chart(fig_ay, use_container_width=True, config={"displayModeBar": False})

            # Top papers
            for i, (_, row) in enumerate(aut_pubs.nlargest(5, "citations").iterrows()):
                bc_color = COLORS[i % len(COLORS)]
                cite = int(row["citations"])
                doi_str = str(row.get("doi", "") or "").strip()
                doi_link = f'<a href="https://doi.org/{doi_str}" target="_blank" style="color:#4a5568;font-size:10px;font-family:DM Mono,monospace;text-decoration:none;">↗ {doi_str[:40]}</a>' if doi_str and doi_str.lower() not in ("nan","none","") else ""
                st.markdown(f"""
                <div style="background:#0e1117;border:1px solid #1e2535;border-left:3px solid {bc_color};
                            padding:12px 16px;margin-bottom:6px;border-radius:0 4px 4px 0;">
                    <div style="display:flex;justify-content:space-between;gap:16px;">
                        <div style="flex:1;">
                            <div style="font-size:13px;color:#e4e8f0;line-height:1.4;">{row['title']}</div>
                            <div style="font-family:DM Mono,monospace;font-size:10px;color:#4a5568;margin-top:4px;">
                                {int(row['year']) if pd.notna(row['year']) else '?'} · {str(row.get('journal',''))[:50]}
                            </div>
                            <div style="margin-top:4px;">{doi_link}</div>
                        </div>
                        <div style="text-align:right;min-width:50px;">
                            <div style="font-family:Bebas Neue,sans-serif;font-size:36px;color:{bc_color};line-height:1;">{cite}</div>
                            <div style="font-family:DM Mono,monospace;font-size:9px;color:#4a5568;">CITED</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — JOURNALS
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "📰 JOURNALS":

    j1, j2 = st.columns(2)

    with j1:
        st.markdown("<div class='section-label'>Top Journals by Publications</div>", unsafe_allow_html=True)
        jc = fdf["journal"].dropna().value_counts().head(20).reset_index()
        jc.columns = ["journal", "count"]
        fig_j1 = go.Figure(go.Bar(
            x=jc["count"], y=jc["journal"], orientation="h",
            marker_color=COLORS[0],
            hovertemplate="<b>%{y}</b><br>%{x} papers<extra></extra>",
        ))
        fig_j1.update_layout(**THEME, height=560,
                              xaxis=AXIS, yaxis=dict(**AXIS_CAT, autorange="reversed"), bargap=0.25)
        st.plotly_chart(fig_j1, use_container_width=True, config={"displayModeBar": False})

    with j2:
        st.markdown("<div class='section-label'>Top Journals by Total Citations</div>", unsafe_allow_html=True)
        jcite = (
            fdf.dropna(subset=["journal"])
            .groupby("journal")["citations_wos"].sum()
            .nlargest(20)
            .reset_index()
        )
        jcite.columns = ["journal", "citations"]
        fig_j2 = go.Figure(go.Bar(
            x=jcite["citations"], y=jcite["journal"], orientation="h",
            marker_color=COLORS[1],
            hovertemplate="<b>%{y}</b><br>%{x} citations<extra></extra>",
        ))
        fig_j2.update_layout(**THEME, height=560,
                              xaxis=AXIS, yaxis=dict(**AXIS_CAT, autorange="reversed"), bargap=0.25)
        st.plotly_chart(fig_j2, use_container_width=True, config={"displayModeBar": False})

    # Journal deep dive
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>Journal Deep Dive</div>", unsafe_allow_html=True)

    journals_list = fdf["journal"].dropna().value_counts().head(100).index.tolist()
    sel_journal = st.selectbox("Select journal", journals_list, key="sel_journal")
    if sel_journal:
        j_pubs = fdf[fdf["journal"] == sel_journal].copy()
        ja, jb, jc2, jd = st.columns(4)
        for c, lbl, v, col in [
            (ja, "Papers",      len(j_pubs),                          "#e4e8f0"),
            (jb, "Citations",   j_pubs["citations_wos"].sum(),        "#47f7c8"),
            (jc2,"Avg/Paper",   f"{j_pubs['citations_wos'].mean():.1f}","#f7e147"),
            (jd, "Max Cited",   j_pubs["citations_wos"].max(),        "#f76b47"),
        ]:
            with c:
                st.markdown(f"""
                <div class="hindex-box" style="--accent-color:{col}">
                    <div class="hindex-num" style="color:{col};font-size:36px;">{v}</div>
                    <div class="hindex-label">{lbl}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        j_year = j_pubs[j_pubs["year"].notna()].groupby("year").agg(
            papers=("citations_wos", "count"), citations=("citations_wos", "sum")
        ).reset_index()
        j_year["year"] = j_year["year"].astype(int)
        fig_jy = go.Figure()
        fig_jy.add_trace(go.Bar(x=j_year["year"], y=j_year["papers"], name="Papers",
                                marker_color="rgba(71,247,200,0.3)",
                                hovertemplate="<b>%{x}</b><br>%{y} papers<extra></extra>"))
        fig_jy.add_trace(go.Scatter(x=j_year["year"], y=j_year["citations"], name="Citations",
                                    mode="lines+markers", line=dict(color=COLORS[1], width=2),
                                    marker=dict(size=6), yaxis="y2",
                                    hovertemplate="<b>%{x}</b><br>%{y} citations<extra></extra>"))
        fig_jy.update_layout(
            **THEME, height=260, bargap=0.2,
            xaxis=YEAR_AXIS,
            yaxis=dict(**AXIS, title="Papers", dtick=1),
            yaxis2=dict(overlaying="y", side="right", title="Citations",
                        tickfont=dict(color=COLORS[1]), title_font=dict(color=COLORS[1]),
                        gridcolor="rgba(0,0,0,0)"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e4e8f0"), x=0, y=1.12, orientation="h"),
        )
        st.plotly_chart(fig_jy, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PAPERS SEARCH
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "🔍 PAPERS":

    sc1, sc2, sc3 = st.columns([2, 1, 1])
    with sc1:
        query = st.text_input("🔎 Search by title, author, journal...", placeholder="e.g. machine learning", key="search_query")
    with sc2:
        sort_by = st.selectbox("Sort by", ["Citations (WoS) ↓", "Citations (All DB) ↓", "Year ↓", "Year ↑"], key="sort_by")
    with sc3:
        n_results = st.selectbox("Show", [25, 50, 100, 200], key="n_results")

    sdf = fdf.copy()
    if query:
        q = query.lower()
        sdf = sdf[
            sdf["title"].fillna("").str.lower().str.contains(q) |
            sdf["authors"].fillna("").str.lower().str.contains(q) |
            sdf["journal"].fillna("").str.lower().str.contains(q)
        ]

    sort_map = {
        "Citations (WoS) ↓":    ("citations_wos", False),
        "Citations (All DB) ↓": ("citations_all", False),
        "Year ↓":               ("year", False),
        "Year ↑":               ("year", True),
    }
    sc, asc = sort_map[sort_by]
    sdf = sdf.sort_values(sc, ascending=asc).head(n_results)

    st.markdown(
        f"<div class='section-label'>Results: {len(sdf)} papers</div>",
        unsafe_allow_html=True,
    )

    for i, (_, row) in enumerate(sdf.iterrows()):
        cite = int(row["citations_wos"])
        bc_color = COLORS[i % len(COLORS)]
        doi_str = str(row.get("doi", "") or "").strip()
        doi_link = f'<a href="https://doi.org/{doi_str}" target="_blank" style="color:#4a5568;font-size:10px;font-family:DM Mono,monospace;text-decoration:none;">↗ {doi_str[:45]}</a>' if doi_str and doi_str.lower() not in ("nan","none","") else ""
        abstr = str(row.get("abstract", "") or "")
        abstr_snippet = abstr[:200] + "…" if len(abstr) > 200 else abstr

        st.markdown(f"""
        <div style="background:#0e1117;border:1px solid #1e2535;border-left:3px solid {bc_color};
                    padding:14px 18px;margin-bottom:8px;border-radius:0 4px 4px 0;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
                <div style="flex:1;">
                    <div style="font-size:13px;line-height:1.5;color:#e4e8f0;margin-bottom:4px;">{row['title']}</div>
                    <div style="font-size:11px;color:{bc_color};font-style:italic;margin-bottom:5px;">{fmt_authors(row.get('authors',''))}</div>
                    <div style="font-family:DM Mono,monospace;font-size:10px;color:#4a5568;margin-bottom:6px;">
                        {int(row['year']) if pd.notna(row.get('year')) else '?'} · {str(row.get('journal',''))[:65]}
                    </div>
                    {"<div style='font-size:11px;color:#6b7a90;margin-bottom:6px;line-height:1.5;'>"+abstr_snippet+"</div>" if abstr_snippet.strip() else ""}
                    <div style="margin-top:4px;">{tier_badge(cite)} &nbsp; {doi_link}</div>
                </div>
                <div style="text-align:right;min-width:60px;">
                    <div style="font-family:Bebas Neue,sans-serif;font-size:40px;color:{bc_color};line-height:1;">{cite}</div>
                    <div style="font-family:DM Mono,monospace;font-size:9px;color:#4a5568;">CITED</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — INDEXES
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "📈 INDEXES":

    idx1, idx2, idx3 = st.columns(3)

    h_idx2 = calc_h_index(fdf["citations_wos"])
    g_idx2 = calc_g_index(fdf["citations_wos"])
    # i10 index
    i10 = int((fdf["citations_wos"] >= 10).sum())

    for c, lbl, v, col in [
        (idx1, "h-index",  h_idx2, COLORS[0]),
        (idx2, "g-index",  g_idx2, COLORS[1]),
        (idx3, "i10-index",i10,    COLORS[2]),
    ]:
        with c:
            st.markdown(f"""
            <div class="hindex-box" style="--accent-color:{col};">
                <div class="hindex-num" style="color:{col};">{v}</div>
                <div class="hindex-label">{lbl}</div>
                <div class="hindex-sub">
                    {"h papers with ≥h citations" if "h-index" in lbl else
                     "max g where top g papers have ≥g² citations" if "g-index" in lbl else
                     "papers with ≥10 citations"}
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # Lorenz-style citation accumulation curve
    st.markdown("<div class='section-label'>Citation Accumulation (Lorenz Curve)</div>", unsafe_allow_html=True)
    sorted_cites = np.array(sorted(fdf["citations_wos"].tolist()))
    cum_papers = np.arange(1, len(sorted_cites) + 1) / len(sorted_cites) * 100
    cum_cites = np.cumsum(sorted_cites) / sorted_cites.sum() * 100
    fig_lc = go.Figure()
    fig_lc.add_trace(go.Scatter(
        x=cum_papers, y=cum_cites, mode="lines",
        line=dict(color=COLORS[0], width=2),
        fill="tozeroy", fillcolor="rgba(71,247,200,0.05)",
        hovertemplate="Top %{x:.1f}% papers → %{y:.1f}% of citations<extra></extra>",
        name="Observed"
    ))
    fig_lc.add_trace(go.Scatter(
        x=[0, 100], y=[0, 100], mode="lines",
        line=dict(color="#4a5568", width=1, dash="dot"),
        name="Equal distribution",
    ))
    fig_lc.update_layout(**THEME, height=320,
                          xaxis=dict(**AXIS, title="% of papers (low → high)"),
                          yaxis=dict(**AXIS, title="% of citations"),
                          legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e4e8f0")))
    st.plotly_chart(fig_lc, use_container_width=True, config={"displayModeBar": False})

    i1, i2 = st.columns(2)
    with i1:
        # h-index evolution over time
        st.markdown("<div class='section-label'>h-index Evolution (by year)</div>", unsafe_allow_html=True)
        years_sorted = sorted([y for y in fdf["year"].dropna().unique() if y >= 2010], reverse=False)
        h_ev = []
        for yr in years_sorted:
            subset = fdf[fdf["year"] <= yr]["citations_wos"]
            h_ev.append({"year": int(yr), "h": calc_h_index(subset)})
        h_ev_df = pd.DataFrame(h_ev)
        if not h_ev_df.empty:
            fig_hev = go.Figure(go.Scatter(
                x=h_ev_df["year"], y=h_ev_df["h"],
                mode="lines+markers", line=dict(color=COLORS[0], width=2),
                marker=dict(size=8, color=COLORS[0]),
                hovertemplate="<b>%{x}</b><br>h-index: %{y}<extra></extra>",
            ))
            fig_hev.update_layout(**THEME, height=280, xaxis=YEAR_AXIS, yaxis=AXIS)
            st.plotly_chart(fig_hev, use_container_width=True, config={"displayModeBar": False})

    with i2:
        # Usage vs citations scatter
        st.markdown("<div class='section-label'>Usage (180d) vs Citations</div>", unsafe_allow_html=True)
        scatter_df = fdf[fdf["usage_180"] > 0].copy()
        if not scatter_df.empty:
            fig_sc = go.Figure(go.Scatter(
                x=scatter_df["usage_180"],
                y=scatter_df["citations_wos"],
                mode="markers",
                marker=dict(
                    size=6, color=scatter_df["citations_wos"],
                    colorscale=[[0, "#1a2535"], [0.5, "#47c8ff"], [1, "#47f7c8"]],
                    showscale=False, opacity=0.7,
                ),
                hovertemplate="<b>Usage 180d:</b> %{x}<br><b>Citations WoS:</b> %{y}<extra></extra>",
            ))
            fig_sc.update_layout(**THEME, height=280,
                                  xaxis=dict(**AXIS, title="Usage (180 days)"),
                                  yaxis=dict(**AXIS, title="Citations (WoS)"))
            st.plotly_chart(fig_sc, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — CO-AUTHORSHIP NETWORK
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "🤝 CO-AUTHORSHIP":

    st.markdown("<div class='section-label'>Co-authorship Network</div>", unsafe_allow_html=True)

    nc1, nc2 = st.columns([1, 3])
    with nc1:
        min_collab = st.slider("Min. shared papers", 1, 10, 2, key="min_collab")
        max_nodes = st.slider("Max nodes to show", 20, 200, 80, key="max_nodes")

    with nc2:
        # Build graph
        pair_counts: Counter = Counter()
        for _, row in fdf.iterrows():
            authors_list = row["author_list"]
            if len(authors_list) < 2 or len(authors_list) > 20:
                continue
            for i in range(len(authors_list)):
                for j in range(i + 1, len(authors_list)):
                    key = tuple(sorted((authors_list[i], authors_list[j])))
                    pair_counts[key] += 1

        edges = [(a, b, w) for (a, b), w in pair_counts.items() if w >= min_collab]

        if not edges:
            st.info("No co-authorship pairs found with the current settings. Try reducing 'Min. shared papers'.")
        else:
            G = nx.Graph()
            for a, b, w in edges:
                G.add_edge(a, b, weight=w)

            # Keep only top nodes by degree
            top_nodes = sorted(G.nodes(), key=lambda n: G.degree(n, weight="weight"), reverse=True)[:max_nodes]
            G_sub = G.subgraph(top_nodes).copy()

            if G_sub.number_of_nodes() == 0:
                st.info("No nodes to display.")
            else:
                pos = nx.spring_layout(G_sub, k=0.5, iterations=60, seed=42)
                degrees = dict(G_sub.degree(weight="weight"))
                max_deg = max(degrees.values()) if degrees else 1

                # Build traces
                edge_traces = []
                for u, v, d in G_sub.edges(data=True):
                    x0, y0 = pos[u]
                    x1, y1 = pos[v]
                    w = d.get("weight", 1)
                    edge_traces.append(go.Scatter(
                        x=[x0, x1, None], y=[y0, y1, None],
                        mode="lines",
                        line=dict(width=0.5 + 3 * (w / (max(d.get("weight", 1) for _, _, d in G_sub.edges(data=True)) or 1)),
                                  color="rgba(71,247,200,0.18)"),
                        hoverinfo="none",
                    ))

                nodes_list = list(G_sub.nodes())
                nx_x = [pos[n][0] for n in nodes_list]
                nx_y = [pos[n][1] for n in nodes_list]
                sizes = [8 + 22 * (degrees.get(n, 1) / max_deg) for n in nodes_list]
                hover_texts = [
                    f"{n}<br>Co-authors: {G_sub.degree(n)}<br>Collaborations: {int(degrees.get(n,1))}"
                    for n in nodes_list
                ]

                node_trace = go.Scatter(
                    x=nx_x, y=nx_y, mode="markers+text",
                    text=[n.split(",")[0] if "," in n else n.split()[-1] for n in nodes_list],
                    textfont=dict(size=8, color="#e4e8f0"),
                    textposition="top center",
                    hovertext=hover_texts,
                    hoverinfo="text",
                    marker=dict(
                        size=sizes,
                        color=[degrees.get(n, 1) for n in nodes_list],
                        colorscale=[[0, "#1a2535"], [0.4, "#47c8ff"], [1, "#47f7c8"]],
                        showscale=True,
                        colorbar=dict(title="Collabs", tickfont=dict(color="#e4e8f0"),
                                      title_font=dict(color="#e4e8f0")),
                        line=dict(width=1, color="#080b12"),
                        opacity=0.9,
                    ),
                )

                fig_net = go.Figure(data=edge_traces + [node_trace])
                fig_net.update_layout(
                    **THEME, height=580,
                    xaxis=dict(visible=False), yaxis=dict(visible=False),
                    showlegend=False,
                )
                st.plotly_chart(fig_net, use_container_width=True, config={"displayModeBar": False})

                st.markdown(
                    f"<div style='font-family:DM Mono,monospace;font-size:10px;color:#4a5568;margin-top:-12px;'>"
                    f"Showing {G_sub.number_of_nodes()} nodes, {G_sub.number_of_edges()} edges · "
                    f"min. {min_collab} shared paper(s)</div>",
                    unsafe_allow_html=True,
                )

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:48px;padding-top:20px;border-top:1px solid #1e2535;
            display:flex;justify-content:space-between;">
    <p style="font-family:DM Mono,monospace;font-size:11px;color:#4a5568;">Data source: Web of Science</p>
    <p style="font-family:DM Mono,monospace;font-size:11px;color:#4a5568;">Research Analytics Dashboard</p>
</div>
""", unsafe_allow_html=True)
