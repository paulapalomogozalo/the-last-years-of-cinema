import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Last 100 Years of Cinema",
    page_icon="🎞️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Colour palette ────────────────────────────────────────────────────────────
CREAM      = "#FAFAF7"
DARK       = "#1C1C1C"
GOLD       = "#C9A84C"
GOLD_LIGHT = "#E8D5A3"
MUTED      = "#6B6B6B"
ACCENT2    = "#3D5A80"
ACCENT3    = "#8B4513"
PALETTE    = [GOLD, ACCENT2, ACCENT3, "#5C7A6B", "#A67C9B", "#7A8C5C", "#9B6B4A", "#4A7A8C"]
CHART_BG   = "#F5F5F0"
GRID_COLOR = "#E0DDD5"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Sans+3:wght@300;400;600&display=swap');

    [data-testid="stAppViewContainer"] {{
        background-color: {CREAM};
        font-family: 'Source Sans 3', sans-serif;
    }}
    [data-testid="stSidebar"] {{ display: none; }}
    [data-testid="stHeader"] {{ background: transparent; }}
    .block-container {{ padding: 0 4rem 4rem 4rem; max-width: 1200px; margin: auto; }}

    h1, h2, h3 {{ font-family: 'Playfair Display', serif; color: {DARK}; }}

    .masthead {{
        border-top: 3px solid {DARK};
        border-bottom: 1px solid {DARK};
        padding: 8px 0 6px 0;
        margin-bottom: 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .masthead-title {{
        font-family: 'Playfair Display', serif;
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: {MUTED};
    }}
    .masthead-author {{
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.75rem;
        color: {MUTED};
    }}
    .hero-title {{
        font-family: 'Playfair Display', serif;
        font-size: 4.2rem;
        font-weight: 900;
        line-height: 1.05;
        color: {DARK};
        margin: 2rem 0 1rem 0;
    }}
    .hero-subtitle {{
        font-family: 'Source Sans 3', sans-serif;
        font-size: 1.2rem;
        color: {MUTED};
        font-weight: 300;
        line-height: 1.7;
        max-width: 700px;
        margin-bottom: 2rem;
        border-left: 3px solid {GOLD};
        padding-left: 1rem;
    }}
    .act-label {{
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.75rem;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: {GOLD};
        font-weight: 600;
        margin-bottom: 4px;
    }}
    .act-title {{
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: {DARK};
        margin: 0 0 0.5rem 0;
        border-bottom: 2px solid {GOLD};
        padding-bottom: 0.4rem;
    }}
    .act-intro {{
        font-family: 'Source Sans 3', sans-serif;
        font-size: 1rem;
        color: {MUTED};
        line-height: 1.8;
        margin-bottom: 1.5rem;
        max-width: 750px;
    }}
    .insight-pill {{
        background: {GOLD_LIGHT};
        border-left: 4px solid {GOLD};
        border-radius: 0 6px 6px 0;
        padding: 14px 18px;
        margin: 12px 0;
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.92rem;
        color: {DARK};
        line-height: 1.6;
    }}
    .stat-block {{
        text-align: center;
        padding: 20px 10px;
        border-top: 2px solid {DARK};
        border-bottom: 1px solid {GRID_COLOR};
    }}
    .stat-number {{
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        font-weight: 900;
        color: {GOLD};
        line-height: 1;
    }}
    .stat-label {{
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.78rem;
        color: {MUTED};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 4px;
    }}
    .pull-quote {{
        font-family: 'Playfair Display', serif;
        font-size: 1.55rem;
        font-style: italic;
        color: {DARK};
        border-top: 2px solid {GOLD};
        border-bottom: 2px solid {GOLD};
        padding: 22px 0;
        margin: 28px 0;
        text-align: center;
        line-height: 1.45;
    }}
    .divider {{
        border: none;
        border-top: 1px solid {GRID_COLOR};
        margin: 3rem 0;
    }}
    .footer-line {{
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.78rem;
        color: {MUTED};
        text-align: center;
        border-top: 1px solid {DARK};
        padding-top: 1rem;
        margin-top: 3rem;
    }}
</style>
""", unsafe_allow_html=True)


# ── Load & prepare data ───────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("tmdb_5000_movies.csv", sep=";", encoding="latin1")
    df["budget"]       = pd.to_numeric(df["budget"], errors="coerce")
    df["revenue"]      = pd.to_numeric(df["revenue"], errors="coerce")
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce")
    df["vote_count"]   = pd.to_numeric(df["vote_count"], errors="coerce")
    df["runtime"]      = pd.to_numeric(df["runtime"], errors="coerce")
    df["popularity"]   = (
        pd.to_numeric(df["popularity"].astype(str).str.replace(".", "", regex=False), errors="coerce") / 1000
    )
    df["year"]   = pd.to_datetime(df["release_date"], dayfirst=True, errors="coerce").dt.year
    df["decade"] = (df["year"] // 10 * 10).astype("Int64")

    def parse_genres(x):
        try:    return [d["name"] for d in json.loads(x)]
        except: return []

    df["genres_list"]   = df["genres"].apply(parse_genres)
    df["primary_genre"] = df["genres_list"].apply(lambda g: g[0] if g else "Unknown")

    df_fin = df[(df["budget"] > 1_000_000) & (df["revenue"] > 0)].copy()
    df_fin["roi"]        = (df_fin["revenue"] - df_fin["budget"]) / df_fin["budget"] * 100
    df_fin["profit"]     = df_fin["revenue"] - df_fin["budget"]
    df_fin["vote_count"] = df_fin["vote_count"].fillna(0)
    df_fin["decade"]     = (df_fin["year"] // 10 * 10).astype("Int64")

    return df, df_fin

df, df_fin = load_data()

CHART_LAYOUT = dict(
    paper_bgcolor=CHART_BG,
    plot_bgcolor=CHART_BG,
    font=dict(family="Source Sans 3, sans-serif", color=DARK, size=12),
    margin=dict(t=50, b=40, l=40, r=20),
)

# ═══════════════════════════════════════════════════════════════════════════════
# MASTHEAD
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class='masthead'>
    <span class='masthead-title'>Data Visualisation · ICADE E-8</span>
    <span class='masthead-author'>Paula Palomo Gozalo &nbsp;·&nbsp; 202408411</span>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class='hero-title'>The Last 100 Years<br>of Cinema</div>
<div class='hero-subtitle'>
    From Snow White to Avatar — a data-driven journey through Hollywood's rise, 
    the explosion of blockbusters, the genres that conquered the world, 
    and the small films that beat them all.
</div>
""", unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown("""<div class='stat-block'>
        <div class='stat-number'>4,809</div>
        <div class='stat-label'>Films analysed</div>
    </div>""", unsafe_allow_html=True)
with s2:
    st.markdown("""<div class='stat-block'>
        <div class='stat-number'>100+</div>
        <div class='stat-label'>Years of history</div>
    </div>""", unsafe_allow_html=True)
with s3:
    top_roi = df_fin["roi"].max()
    st.markdown(f"""<div class='stat-block'>
        <div class='stat-number'>{top_roi:,.0f}%</div>
        <div class='stat-label'>Highest ever ROI</div>
    </div>""", unsafe_allow_html=True)
with s4:
    st.markdown("""<div class='stat-block'>
        <div class='stat-number'>$380M</div>
        <div class='stat-label'>Largest budget on record</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ACT I — THE BIRTH OF BLOCKBUSTERS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class='act-label'>Act I</div>
<div class='act-title'>The Birth of Blockbusters</div>
<div class='act-intro'>
    For most of the 20th century, making a movie cost a fraction of what it does today.
    Then the 1970s arrived — and everything changed. Jaws. Star Wars. Raiders of the Lost Ark.
    Studios discovered that audiences would pay to feel something enormous.
    Budgets have never looked back.
</div>
""", unsafe_allow_html=True)

budget_decade = (
    df_fin[df_fin["decade"] >= 1930]
    .groupby("decade")["budget"]
    .median()
    .reset_index()
)
budget_decade["decade"]   = budget_decade["decade"].astype(int)
budget_decade["budget_M"] = budget_decade["budget"] / 1_000_000

fig_budget = go.Figure()
fig_budget.add_trace(go.Scatter(
    x=budget_decade["decade"],
    y=budget_decade["budget_M"],
    mode="lines+markers",
    fill="tozeroy",
    fillcolor="rgba(201,168,76,0.18)",
    line=dict(color=GOLD, width=2.5),
    marker=dict(color=GOLD, size=9, line=dict(color=DARK, width=1.5)),
    hovertemplate="<b>%{x}s</b><br>Median budget: $%{y:.1f}M<extra></extra>",
))
fig_budget.update_layout(
    **CHART_LAYOUT,
    height=360,
    xaxis=dict(title="Decade", gridcolor=GRID_COLOR, dtick=10),
    yaxis=dict(title="Median Production Budget ($M)", gridcolor=GRID_COLOR),
    showlegend=False,
)
st.plotly_chart(fig_budget, use_container_width=True)

st.markdown(f"""
<div class='insight-pill'>
    📌 <strong>The turning point was the 1970s.</strong> Before then, median budgets sat below $10M.
    By the 1990s they had tripled. The blockbuster era didn't just change cinema —
    it turned filmmaking into a high-stakes financial gamble.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ACT II — THE GENRE WARS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class='act-label'>Act II</div>
<div class='act-title'>The Genre Wars</div>
<div class='act-intro'>
    Every decade, audiences fall in love with something different.
    Drama has always been the backbone of cinema. But Action surged,
    Comedy peaked and faded, and Science Fiction quietly became a titan.
    This is how genres have fought for dominance since 1980.
</div>
""", unsafe_allow_html=True)

rows_g = []
for _, row in df.dropna(subset=["decade"]).iterrows():
    for g in row["genres_list"]:
        rows_g.append({"decade": int(row["decade"]), "genre": g})
df_g = pd.DataFrame(rows_g)
top8 = df_g["genre"].value_counts().head(8).index.tolist()
df_g_top = df_g[df_g["genre"].isin(top8)]
genre_decade = df_g_top.groupby(["decade","genre"]).size().reset_index(name="count")
genre_decade = genre_decade[genre_decade["decade"] >= 1980]

fig_genre = px.area(
    genre_decade,
    x="decade", y="count", color="genre",
    color_discrete_sequence=PALETTE,
    labels={"decade": "Decade", "count": "Number of Films", "genre": "Genre"},
    template=None,
)
fig_genre.update_layout(
    **CHART_LAYOUT,
    height=400,
    xaxis=dict(title="Decade", dtick=10, gridcolor=GRID_COLOR),
    yaxis=dict(title="Number of Films", gridcolor=GRID_COLOR),
    legend=dict(bgcolor=CHART_BG, bordercolor=GRID_COLOR, borderwidth=1,
                title_text="Genre", font=dict(size=11)),
    hovermode="x unified",
)
st.plotly_chart(fig_genre, use_container_width=True)

col_g1, col_g2 = st.columns(2)
with col_g1:
    st.markdown(f"""
    <div class='insight-pill'>
        📌 <strong>Drama never dies.</strong> It has dominated every single decade,
        peaking in the 2000s with nearly 1,000 films. It is the genre Hollywood always returns to.
    </div>""", unsafe_allow_html=True)
with col_g2:
    st.markdown(f"""
    <div class='insight-pill'>
        📌 <strong>Action exploded from the 1980s onwards</strong>, tracking the rise of franchise cinema.
        By the 2010s, Action and Adventure together rival Drama for the first time in history.
    </div>""", unsafe_allow_html=True)

st.markdown("#### Where the money went — total box office by genre")

rows_t = []
for _, row in df_fin.dropna(subset=["decade"]).iterrows():
    for g in row["genres_list"]:
        rows_t.append({"genre": g, "revenue": row["revenue"], "roi": row["roi"]})
df_t = pd.DataFrame(rows_t)
genre_rev = df_t.groupby("genre").agg(
    total_revenue=("revenue","sum"),
    median_roi=("roi","median"),
    count=("revenue","count"),
).reset_index().query("count >= 20")

fig_tree = px.treemap(
    genre_rev,
    path=["genre"],
    values="total_revenue",
    color="median_roi",
    color_continuous_scale=[[0, "#D4C5A9"], [0.5, GOLD], [1, ACCENT2]],
    hover_data={"median_roi":":.0f","count":True},
)
fig_tree.update_traces(
    textfont=dict(family="Playfair Display, serif", size=13),
    hovertemplate="<b>%{label}</b><br>Total Revenue: $%{value:,.0f}<br>Median ROI: %{color:.0f}%<extra></extra>",
)
fig_tree.update_layout(
    paper_bgcolor=CHART_BG,
    margin=dict(t=10, b=10, l=10, r=10),
    height=380,
    coloraxis_colorbar=dict(title="Median ROI (%)", tickfont=dict(family="Source Sans 3")),
)
st.plotly_chart(fig_tree, use_container_width=True)

st.markdown(f"""
<div class='insight-pill'>
    📌 <strong>Animation and Adventure dominate box office revenue</strong> despite not being the most
    common genres. Drama may rule in volume, but it is spectacle that fills seats.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ACT III — DOES MONEY BUY SUCCESS?
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class='act-label'>Act III</div>
<div class='act-title'>Does Money Buy Success?</div>
<div class='act-intro'>
    Hollywood's most persistent belief: spend more, earn more.
    The data tells a more complicated story. Yes, bigger budgets tend to earn bigger revenues —
    but the relationship is far noisier than studios would like to admit.
    And when it comes to what audiences actually think of a film? Money buys almost nothing.
</div>
""", unsafe_allow_html=True)

col_m1, col_m2 = st.columns(2)

with col_m1:
    df_scatter = df_fin.query("budget < 3.5e8 and revenue < 2.8e9").copy()
    df_scatter["budget_M"]  = df_scatter["budget"] / 1e6
    df_scatter["revenue_M"] = df_scatter["revenue"] / 1e6

    fig_scatter = px.scatter(
        df_scatter,
        x="budget_M", y="revenue_M",
        color="primary_genre",
        hover_name="title",
        hover_data={"budget_M":":.0f","revenue_M":":.0f","vote_average":True,"year":True,"primary_genre":False},
        color_discrete_sequence=PALETTE,
        opacity=0.6,
        labels={"budget_M":"Budget ($M)","revenue_M":"Revenue ($M)","primary_genre":"Genre"},
        template=None,
    )
    max_v = df_scatter["budget_M"].max()
    fig_scatter.add_trace(go.Scatter(
        x=[0, max_v], y=[0, max_v],
        mode="lines",
        line=dict(color=DARK, dash="dash", width=1),
        name="Break-even",
        hoverinfo="skip",
    ))
    fig_scatter.update_layout(
        **CHART_LAYOUT, height=380,
        title=dict(text="Budget vs. Box Office Revenue", font=dict(family="Playfair Display", size=15)),
        xaxis=dict(title="Production Budget ($M)", gridcolor=GRID_COLOR),
        yaxis=dict(title="Box Office Revenue ($M)", gridcolor=GRID_COLOR),
        legend=dict(bgcolor=CHART_BG, font=dict(size=10)),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    corr = df_fin[["budget","revenue"]].corr().iloc[0,1]
    st.markdown(f"""
    <div class='insight-pill'>
        📐 Budget–Revenue correlation: <strong>r = {corr:.2f}</strong>.
        Moderate — not the whole story. Many expensive films sit below the break-even line.
    </div>""", unsafe_allow_html=True)

with col_m2:
    df_fin["budget_tier"] = pd.cut(
        df_fin["budget"],
        bins=[0, 10e6, 50e6, 100e6, 200e6, df_fin["budget"].max()+1],
        labels=["Micro\n(<$10M)","Low\n($10–50M)","Mid\n($50–100M)","High\n($100–200M)","Blockbuster\n(>$200M)"]
    )
    tier_rating = (
        df_fin.dropna(subset=["budget_tier","vote_average"])
        .groupby("budget_tier", observed=True)["vote_average"]
        .mean().reset_index()
    )

    fig_tier = go.Figure(go.Bar(
        x=tier_rating["budget_tier"].astype(str),
        y=tier_rating["vote_average"],
        marker_color=[GOLD_LIGHT, GOLD_LIGHT, GOLD, GOLD_LIGHT, GOLD_LIGHT],
        marker_line_color=GOLD,
        marker_line_width=1.5,
        text=tier_rating["vote_average"].round(2),
        textposition="outside",
        textfont=dict(color=DARK, size=11),
    ))
    fig_tier.update_layout(
        **CHART_LAYOUT, height=380,
        title=dict(text="Does Budget Improve Ratings?", font=dict(family="Playfair Display", size=15)),
        xaxis=dict(title="Budget Tier", gridcolor=GRID_COLOR),
        yaxis=dict(title="Average Audience Rating", range=[5.5, 7.2], gridcolor=GRID_COLOR),
    )
    st.plotly_chart(fig_tier, use_container_width=True)

    st.markdown(f"""
    <div class='insight-pill'>
        📌 Audience ratings barely move across budget tiers.
        <strong>Micro-budget films score almost as highly as $200M+ blockbusters.</strong>
        Critical acclaim is not for sale.
    </div>""", unsafe_allow_html=True)

st.markdown(f"""
<div class='pull-quote'>
    "The most expensive film ever made is not the most loved.<br>
    The most loved film ever made is rarely the most expensive."
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ACT IV — THE HIDDEN GEMS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class='act-label'>Act IV</div>
<div class='act-title'>The Hidden Gems</div>
<div class='act-intro'>
    If blockbusters are risky bets, then small films are Hollywood's best-kept secret.
    Some of the most profitable movies ever made cost almost nothing.
    Here are the films that turned pocket money into gold.
</div>
""", unsafe_allow_html=True)

gems = df_fin[(df_fin["budget"] < 10e6)].nlargest(15, "roi")[
    ["title","budget","revenue","roi","primary_genre","year"]
].copy()
gems["budget_M"]  = gems["budget"] / 1e6
gems["revenue_M"] = gems["revenue"] / 1e6
gems["roi_label"] = gems["roi"].apply(lambda x: f"{x:,.0f}%")

fig_gems = go.Figure(go.Bar(
    y=gems["title"],
    x=gems["roi"],
    orientation="h",
    marker=dict(
        color=gems["roi"],
        colorscale=[[0, GOLD_LIGHT],[1, GOLD]],
        line=dict(color=DARK, width=0.5),
    ),
    text=gems["roi_label"],
    textposition="outside",
    textfont=dict(color=DARK, size=10),
    customdata=gems[["budget_M","revenue_M","year","primary_genre"]].values,
    hovertemplate=(
        "<b>%{y}</b><br>Budget: $%{customdata[0]:.1f}M<br>"
        "Revenue: $%{customdata[1]:.1f}M<br>Year: %{customdata[2]}<br>"
        "Genre: %{customdata[3]}<br>ROI: %{x:,.0f}%<extra></extra>"
    ),
))
fig_gems.update_layout(
    **CHART_LAYOUT, height=520,
    xaxis=dict(title="Return on Investment (%)", gridcolor=GRID_COLOR),
    yaxis=dict(title="", gridcolor=GRID_COLOR, autorange="reversed"),
    showlegend=False,
)
st.plotly_chart(fig_gems, use_container_width=True)

g1, g2, g3 = st.columns(3)
with g1:
    st.markdown(f"""
    <div class='insight-pill'>
        🏆 <strong>Snow White (1937)</strong> cost $1.5M and grossed $185M —
        a 12,000%+ ROI. Disney's first feature film remains the most
        profitable in history by this measure.
    </div>""", unsafe_allow_html=True)
with g2:
    st.markdown(f"""
    <div class='insight-pill'>
        🔪 <strong>Horror is the master genre of ROI.</strong> Saw, Insidious,
        Paranormal Activity 2 — all cost under $3M and returned over 5,000%.
        Fear is cheap to sell.
    </div>""", unsafe_allow_html=True)
with g3:
    st.markdown(f"""
    <div class='insight-pill'>
        💡 <strong>The pattern is clear:</strong> the films that beat the system
        are not the ones with the biggest stars or effects budgets.
        They are the ones with the sharpest ideas.
    </div>""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ACT V — IS HOLLYWOOD LOSING THE WORLD?
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class='act-label'>Act V</div>
<div class='act-title'>Is Hollywood Losing the World?</div>
<div class='act-intro'>
    For most of cinema history, English was the only language that mattered globally.
    But the 2000s brought a quiet revolution: French, Spanish, Chinese and Korean films
    began earning audiences beyond their borders.
    The world is not just watching Hollywood anymore — it is making its own stories.
</div>
""", unsafe_allow_html=True)

lang_map = {
    "en":"English","fr":"French","es":"Spanish","zh":"Chinese",
    "de":"German","hi":"Hindi","ja":"Japanese","ko":"Korean",
    "it":"Italian","ru":"Russian","cn":"Chinese (Cantonese)",
}
df_lang = df[df["decade"] >= 1980].copy()
df_lang["language"] = df_lang["original_language"].map(lang_map).fillna("Other")
lang_decade = df_lang.groupby(["decade","language"]).size().reset_index(name="count")
lang_decade["decade"] = lang_decade["decade"].astype(int)
lang_top = ["English","French","Spanish","Chinese","German","Hindi","Korean","Japanese"]
lang_decade_top = lang_decade[lang_decade["language"].isin(lang_top)]

fig_lang = px.line(
    lang_decade_top,
    x="decade", y="count", color="language",
    markers=True,
    color_discrete_sequence=PALETTE,
    labels={"decade":"Decade","count":"Number of Films","language":"Language"},
    template=None,
)
fig_lang.update_layout(
    **CHART_LAYOUT, height=380,
    xaxis=dict(title="Decade", dtick=10, gridcolor=GRID_COLOR),
    yaxis=dict(title="Number of Films", gridcolor=GRID_COLOR),
    legend=dict(bgcolor=CHART_BG, font=dict(size=11)),
    hovermode="x unified",
)
st.plotly_chart(fig_lang, use_container_width=True)

df["is_english"]      = df["original_language"] == "en"
df["language_group"]  = df["is_english"].map({True:"English-language films", False:"Non-English films"})
df_valid = df[(df["vote_average"] > 0) & (df["vote_count"] >= 50)]

fig_violin = px.violin(
    df_valid,
    x="language_group", y="vote_average",
    color="language_group",
    color_discrete_map={
        "English-language films": GOLD_LIGHT,
        "Non-English films": ACCENT2,
    },
    box=True,
    labels={"language_group":"","vote_average":"Audience Rating"},
    template=None,
)
fig_violin.update_layout(
    **CHART_LAYOUT, height=360,
    showlegend=False,
    title=dict(text="Do Non-English Films Rate Higher?", font=dict(family="Playfair Display", size=15)),
    yaxis=dict(title="Audience Rating (out of 10)", gridcolor=GRID_COLOR),
)
st.plotly_chart(fig_violin, use_container_width=True)

st.markdown(f"""
<div class='insight-pill'>
    📌 <strong>Non-English films consistently earn higher audience ratings than English-language ones.</strong>
    World cinema isn't just catching up with Hollywood —
    in the eyes of audiences, it has already surpassed it.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CONCLUSION
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class='act-label'>Conclusion</div>
<div class='act-title'>What the Data Tells Us</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([1,1])
with c1:
    st.markdown(f"""
    <div style='font-family: Source Sans 3, sans-serif; font-size: 1rem;
                color: {DARK}; line-height: 1.9; padding-right: 2rem;'>
    A hundred years of cinema data converge on a few uncomfortable truths for Hollywood.<br><br>
    <strong>Budgets have exploded</strong> — but the returns have not grown proportionally.
    The blockbuster era made films bigger, louder and more expensive.
    It did not make them better.<br><br>
    <strong>Audiences are not fooled</strong> by spending. Ratings barely budge
    whether a film cost $1M or $300M. The best-rated films in this dataset
    are not the most expensive ones.<br><br>
    <strong>The real winners</strong> are often the ones nobody expected:
    a horror film shot in a house, a Greek wedding comedy,
    a 1930s animated fairy tale. Small ideas with sharp execution
    have outperformed blockbusters by thousands of percent.<br><br>
    And as the world catches up, Hollywood's monopoly on storytelling
    is quietly dissolving. The next hundred years may look very different.
    </div>
    """, unsafe_allow_html=True)

with c2:
    df_fin["size_group"] = df_fin["budget"].apply(
        lambda x: "Small Budget (<$10M)" if x < 10e6
        else ("Large Budget (>$50M)" if x > 50e6 else None)
    )
    df_roi_comp = df_fin.dropna(subset=["size_group"]).copy()
    df_roi_comp = df_roi_comp[df_roi_comp["roi"] < 3000]

    fig_final = px.histogram(
        df_roi_comp,
        x="roi", color="size_group",
        nbins=50,
        barmode="overlay",
        opacity=0.75,
        color_discrete_map={
            "Small Budget (<$10M)": GOLD,
            "Large Budget (>$50M)": ACCENT2,
        },
        labels={"roi":"Return on Investment (%)","size_group":""},
        template=None,
    )
    fig_final.update_layout(
        **CHART_LAYOUT, height=400,
        title=dict(text="ROI Distribution: Small vs. Large Budget", font=dict(family="Playfair Display", size=14)),
        xaxis=dict(title="ROI (%)", gridcolor=GRID_COLOR),
        yaxis=dict(title="Number of Films", gridcolor=GRID_COLOR),
        legend=dict(bgcolor=CHART_BG, font=dict(size=11), orientation="h", y=1.08),
    )
    st.plotly_chart(fig_final, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='footer-line'>
    Paula Palomo Gozalo · 202408411 &nbsp;·&nbsp; Data Visualisation · ICADE E-8
    &nbsp;·&nbsp; Dataset: TMDB 5000 Movies (Kaggle)
</div>
""", unsafe_allow_html=True)
