"""
Beauty Influencer Cosmetics Analytics Dashboard
================================================
Interactive Streamlit dashboard for analyzing cosmetic brand mentions,
sentiment, and trends across top YouTube beauty influencers.
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ──────────────────────────────────────────────
# Page configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Beauty Influencer Analytics",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #C2185B;
        margin-bottom: 0;
    }
    .sub-title {
        font-size: 1rem;
        color: #888;
        margin-top: 0;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #FCE4EC, #F8BBD9);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #880E4F;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #555;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #AD1457;
        border-bottom: 2px solid #F48FB1;
        padding-bottom: 0.3rem;
        margin: 1.5rem 0 1rem 0;
    }
    .sentiment-positive { color: #2E7D32; font-weight: 600; }
    .sentiment-negative { color: #C62828; font-weight: 600; }
    .sentiment-neutral  { color: #F57F17; font-weight: 600; }
    div[data-testid="stSidebarContent"] { background-color: #FFF0F5; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Data loading
# ──────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"

SENTIMENT_COLORS = {
    "positive": "#4CAF50",
    "neutral":  "#FFC107",
    "negative": "#F44336",
}


@st.cache_data
def load_analyzed_data():
    with open(DATA_DIR / "analyzed_data.json", "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def load_csvs():
    return {
        "brands":      pd.read_csv(DATA_DIR / "data_brands.csv"),
        "categories":  pd.read_csv(DATA_DIR / "data_categories.csv"),
        "ingredients": pd.read_csv(DATA_DIR / "data_ingredients.csv"),
        "sentiments":  pd.read_csv(DATA_DIR / "data_sentiments.csv"),
        "youtubers":   pd.read_csv(DATA_DIR / "data_youtubers.csv"),
    }


analyzed_data = load_analyzed_data()
dfs = load_csvs()

all_youtubers = sorted(dfs["brands"]["youtuber"].unique().tolist())
all_brands    = sorted(dfs["brands"]["brand"].unique().tolist())

# ──────────────────────────────────────────────
# Sidebar filters
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💄 Filters")
    st.markdown("---")

    selected_youtubers = st.multiselect(
        "👤 YouTubers",
        options=all_youtubers,
        default=all_youtubers,
        help="Select one or more YouTubers to filter all charts",
    )

    st.markdown("---")
    selected_sentiments = st.multiselect(
        "😊 Sentiment",
        options=["positive", "neutral", "negative"],
        default=["positive", "neutral", "negative"],
    )

    st.markdown("---")
    top_n_brands = st.slider("🏷️ Top N Brands to show", 5, 25, 15)

    st.markdown("---")
    st.markdown("### 📂 About")
    st.markdown("""
This dashboard analyzes cosmetic brand mentions and sentiment across
**top YouTube beauty influencers**.

**Data**: 20 YouTubers · 200 videos · 375 brand mentions

**Sentiment method**: TextBlob NLP + beauty keyword matching
""")

# ──────────────────────────────────────────────
# Apply filters to DataFrames
# ──────────────────────────────────────────────
if not selected_youtubers:
    selected_youtubers = all_youtubers

df_brands      = dfs["brands"][dfs["brands"]["youtuber"].isin(selected_youtubers)]
df_categories  = dfs["categories"][dfs["categories"]["youtuber"].isin(selected_youtubers)]
df_ingredients = dfs["ingredients"][dfs["ingredients"]["youtuber"].isin(selected_youtubers)]
df_sentiments  = dfs["sentiments"][
    dfs["sentiments"]["youtuber"].isin(selected_youtubers) &
    dfs["sentiments"]["label"].isin(selected_sentiments)
]
df_youtubers   = dfs["youtubers"][dfs["youtubers"]["youtuber"].isin(selected_youtubers)]

# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
st.markdown('<p class="main-title">💄 Beauty Influencer Cosmetics Analytics</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Brand mentions, sentiment analysis & ingredient trends across top YouTube beauty channels</p>', unsafe_allow_html=True)

# ──────────────────────────────────────────────
# KPI Cards
# ──────────────────────────────────────────────
total_yt    = len(df_youtubers)
total_vid   = int(df_youtubers["videos_analyzed"].sum()) if not df_youtubers.empty else 0
total_brd   = df_brands["brand"].nunique() if not df_brands.empty else 0
total_sent  = len(df_sentiments)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("👤 YouTubers", total_yt)
with col2:
    st.metric("🎬 Videos Analyzed", total_vid)
with col3:
    st.metric("🏷️ Unique Brands", total_brd)
with col4:
    st.metric("💬 Sentiment Data Points", total_sent)

st.divider()

# ──────────────────────────────────────────────
# Tabs
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "🏷️ Brand Deep Dive",
    "🧪 Ingredients",
    "👤 YouTuber Profiles",
])


# ══════════════════════════════════════════════
# TAB 1 — Overview
# ══════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([3, 2])

    # Top Brands bar chart
    with col_left:
        st.markdown('<p class="section-header">🏆 Top Mentioned Brands</p>', unsafe_allow_html=True)
        if not df_brands.empty:
            brand_totals = (
                df_brands.groupby("brand")["count"]
                .sum()
                .sort_values(ascending=False)
                .head(top_n_brands)
                .reset_index()
            )
            fig_brands = px.bar(
                brand_totals,
                x="count", y="brand",
                orientation="h",
                color="count",
                color_continuous_scale="RdPu",
                labels={"count": "Total Mentions", "brand": "Brand"},
                title=f"Top {top_n_brands} Brands by Mention Count",
            )
            fig_brands.update_layout(
                height=480,
                yaxis={"autorange": "reversed"},
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(fig_brands, use_container_width=True)
        else:
            st.info("No brand data for selected filters.")

    # Category distribution donut
    with col_right:
        st.markdown('<p class="section-header">📂 Product Categories</p>', unsafe_allow_html=True)
        if not df_categories.empty:
            cat_totals = (
                df_categories.groupby("category")["count"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            fig_cat = px.pie(
                cat_totals,
                names="category",
                values="count",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                title="Category Distribution",
            )
            fig_cat.update_traces(textposition="outside", textinfo="percent+label")
            fig_cat.update_layout(
                height=480,
                showlegend=False,
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No category data for selected filters.")

    # YouTuber Subscribers bar
    st.markdown('<p class="section-header">📈 YouTuber Channel Stats</p>', unsafe_allow_html=True)
    if not df_youtubers.empty:
        yt_sorted = df_youtubers.sort_values("subscribers", ascending=False)
        fig_yt = px.bar(
            yt_sorted,
            x="youtuber", y="subscribers",
            color="subscribers",
            color_continuous_scale="Pinkyl",
            labels={"subscribers": "Subscribers", "youtuber": ""},
            title="Subscribers by YouTuber",
            text="subscribers",
        )
        fig_yt.update_traces(
            texttemplate="%{text:.2s}",
            textposition="outside",
        )
        fig_yt.update_layout(
            height=380,
            coloraxis_showscale=False,
            xaxis_tickangle=-35,
            margin=dict(l=10, r=10, t=40, b=80),
        )
        st.plotly_chart(fig_yt, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 2 — Brand Deep Dive
# ══════════════════════════════════════════════
with tab2:
    # Brand Sentiment
    st.markdown('<p class="section-header">😊 Brand Sentiment Analysis</p>', unsafe_allow_html=True)

    if not df_sentiments.empty:
        brand_sent_avg = (
            df_sentiments.groupby("brand")
            .agg(avg_score=("avg_score", "mean"), mentions=("mention_count", "sum"))
            .reset_index()
            .sort_values("avg_score", ascending=True)
            .tail(top_n_brands)
        )
        brand_sent_avg["sentiment_label"] = brand_sent_avg["avg_score"].apply(
            lambda s: "positive" if s > 0.08 else "negative" if s < -0.08 else "neutral"
        )
        brand_sent_avg["color"] = brand_sent_avg["sentiment_label"].map(SENTIMENT_COLORS)

        fig_sent = go.Figure(go.Bar(
            x=brand_sent_avg["avg_score"],
            y=brand_sent_avg["brand"],
            orientation="h",
            marker_color=brand_sent_avg["color"],
            text=brand_sent_avg["avg_score"].round(2),
            textposition="outside",
            customdata=brand_sent_avg[["mentions", "sentiment_label"]],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Avg Sentiment: %{x:.3f}<br>"
                "Total Mentions: %{customdata[0]}<br>"
                "Label: %{customdata[1]}<extra></extra>"
            ),
        ))
        fig_sent.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig_sent.update_layout(
            height=max(400, len(brand_sent_avg) * 28),
            title="Average Sentiment Score per Brand",
            xaxis_title="Sentiment Score  (← Negative | Positive →)",
            margin=dict(l=10, r=60, t=40, b=10),
        )
        st.plotly_chart(fig_sent, use_container_width=True)

        # Sentiment distribution pie
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<p class="section-header">📊 Sentiment Distribution</p>', unsafe_allow_html=True)
            sent_counts = df_sentiments["label"].value_counts().reset_index()
            sent_counts.columns = ["label", "count"]
            sent_counts["color"] = sent_counts["label"].map(SENTIMENT_COLORS)
            fig_sd = px.pie(
                sent_counts,
                names="label", values="count",
                color="label",
                color_discrete_map=SENTIMENT_COLORS,
                hole=0.4,
                title="Sentiment Breakdown",
            )
            fig_sd.update_layout(height=320, margin=dict(t=40, b=10))
            st.plotly_chart(fig_sd, use_container_width=True)

        with col_b:
            st.markdown('<p class="section-header">🏅 Top Positive Brands</p>', unsafe_allow_html=True)
            top_pos = (
                df_sentiments[df_sentiments["label"] == "positive"]
                .groupby("brand")["avg_score"]
                .mean()
                .sort_values(ascending=False)
                .head(8)
                .reset_index()
            )
            if not top_pos.empty:
                fig_pos = px.bar(
                    top_pos, x="avg_score", y="brand",
                    orientation="h",
                    color="avg_score",
                    color_continuous_scale=[[0, "#A5D6A7"], [1, "#1B5E20"]],
                    labels={"avg_score": "Avg Sentiment", "brand": ""},
                    title="Most Positively Received Brands",
                )
                fig_pos.update_layout(
                    height=320,
                    coloraxis_showscale=False,
                    yaxis={"autorange": "reversed"},
                    margin=dict(l=10, r=10, t=40, b=10),
                )
                st.plotly_chart(fig_pos, use_container_width=True)
            else:
                st.info("No positive sentiment data.")
    else:
        st.info("No sentiment data for selected filters.")

    # YouTuber × Brand Heatmap
    st.markdown('<p class="section-header">🔥 YouTuber × Brand Heatmap</p>', unsafe_allow_html=True)
    if not df_brands.empty:
        top_brands_list = (
            df_brands.groupby("brand")["count"].sum()
            .nlargest(15).index.tolist()
        )
        top_yt_list = (
            df_brands.groupby("youtuber")["count"].sum()
            .nlargest(15).index.tolist()
        )
        pivot = (
            df_brands[df_brands["brand"].isin(top_brands_list) &
                      df_brands["youtuber"].isin(top_yt_list)]
            .pivot_table(index="youtuber", columns="brand", values="count",
                         aggfunc="sum", fill_value=0)
        )
        if not pivot.empty:
            fig_heat = px.imshow(
                pivot,
                color_continuous_scale="RdPu",
                aspect="auto",
                title="Brand Mentions Heatmap (Top 15 YouTubers × Top 15 Brands)",
                labels=dict(x="Brand", y="YouTuber", color="Mentions"),
            )
            fig_heat.update_xaxes(tickangle=-40)
            fig_heat.update_layout(
                height=max(400, len(pivot) * 35),
                margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(fig_heat, use_container_width=True)

    # Brand overlap — brands mentioned by N+ YouTubers
    st.markdown('<p class="section-header">🤝 Cross-Influencer Brand Overlap</p>', unsafe_allow_html=True)
    if not df_brands.empty:
        overlap = (
            df_brands.groupby("brand")["youtuber"].nunique()
            .sort_values(ascending=False)
            .head(20)
            .reset_index()
        )
        overlap.columns = ["brand", "youtuber_count"]
        overlap["color"] = overlap["youtuber_count"].apply(
            lambda x: "#1B5E20" if x >= 10 else "#388E3C" if x >= 6 else "#81C784"
        )
        fig_overlap = go.Figure(go.Bar(
            x=overlap["brand"],
            y=overlap["youtuber_count"],
            marker_color=overlap["color"],
            text=overlap["youtuber_count"],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Mentioned by %{y} YouTubers<extra></extra>",
        ))
        fig_overlap.update_layout(
            height=380,
            title="Brands Mentioned by the Most YouTubers",
            yaxis_title="Number of YouTubers",
            xaxis_tickangle=-35,
            margin=dict(l=10, r=10, t=40, b=80),
        )
        st.plotly_chart(fig_overlap, use_container_width=True)

    # Sortable data table
    st.markdown('<p class="section-header">📋 Brand Data Table</p>', unsafe_allow_html=True)
    if not df_brands.empty and not df_sentiments.empty:
        brand_table = (
            df_brands.groupby("brand")["count"].sum()
            .reset_index().rename(columns={"count": "total_mentions"})
        )
        sent_table = (
            df_sentiments.groupby("brand")
            .agg(avg_sentiment=("avg_score", "mean"),
                 dominant_label=("label", lambda x: x.mode()[0] if len(x) > 0 else "neutral"))
            .reset_index()
        )
        yt_count_table = (
            df_brands.groupby("brand")["youtuber"].nunique()
            .reset_index().rename(columns={"youtuber": "youtuber_count"})
        )
        merged = brand_table.merge(sent_table, on="brand", how="left")
        merged = merged.merge(yt_count_table, on="brand", how="left")
        merged["avg_sentiment"] = merged["avg_sentiment"].round(3)
        merged = merged.sort_values("total_mentions", ascending=False)
        merged.columns = ["Brand", "Total Mentions", "Avg Sentiment", "Label", "# YouTubers"]
        st.dataframe(merged, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# TAB 3 — Ingredients
# ══════════════════════════════════════════════
with tab3:
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<p class="section-header">🔬 Ingredient Frequency</p>', unsafe_allow_html=True)
        if not df_ingredients.empty:
            ing_totals = (
                df_ingredients.groupby("ingredient")["count"]
                .sum()
                .sort_values(ascending=False)
                .head(20)
                .reset_index()
            )
            fig_ing = px.bar(
                ing_totals,
                x="count", y="ingredient",
                orientation="h",
                color="count",
                color_continuous_scale="YlOrRd",
                labels={"count": "Total Mentions", "ingredient": "Ingredient"},
                title="Most Discussed Skincare Ingredients",
                text="count",
            )
            fig_ing.update_traces(textposition="outside")
            fig_ing.update_layout(
                height=580,
                yaxis={"autorange": "reversed"},
                coloraxis_showscale=False,
                margin=dict(l=10, r=40, t=40, b=10),
            )
            st.plotly_chart(fig_ing, use_container_width=True)
        else:
            st.info("No ingredient data for selected filters.")

    with col_r:
        st.markdown('<p class="section-header">☁️ Ingredient Word Cloud</p>', unsafe_allow_html=True)
        if not df_ingredients.empty:
            try:
                from wordcloud import WordCloud
                import matplotlib.pyplot as plt
                import io

                ing_freq = df_ingredients.groupby("ingredient")["count"].sum().to_dict()
                wc = WordCloud(
                    width=800, height=500,
                    background_color="white",
                    colormap="YlOrRd",
                    max_words=40,
                    prefer_horizontal=0.8,
                ).generate_from_frequencies(ing_freq)

                fig_wc, ax = plt.subplots(figsize=(8, 5))
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                buf = io.BytesIO()
                fig_wc.savefig(buf, format="png", bbox_inches="tight", dpi=120)
                plt.close(fig_wc)
                buf.seek(0)
                st.image(buf, use_container_width=True)
            except ImportError:
                st.info("Install `wordcloud` to see this chart.")
        else:
            st.info("No ingredient data.")

    # Ingredient by YouTuber heatmap
    st.markdown('<p class="section-header">👤 Ingredient Mentions by YouTuber</p>', unsafe_allow_html=True)
    if not df_ingredients.empty:
        top_ings = (
            df_ingredients.groupby("ingredient")["count"]
            .sum().nlargest(12).index.tolist()
        )
        ing_pivot = (
            df_ingredients[df_ingredients["ingredient"].isin(top_ings)]
            .pivot_table(index="youtuber", columns="ingredient", values="count",
                         aggfunc="sum", fill_value=0)
        )
        if not ing_pivot.empty:
            fig_ing_heat = px.imshow(
                ing_pivot,
                color_continuous_scale="YlOrRd",
                aspect="auto",
                title="Ingredient Mentions by YouTuber",
            )
            fig_ing_heat.update_xaxes(tickangle=-35)
            fig_ing_heat.update_layout(
                height=max(360, len(ing_pivot) * 32),
                margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(fig_ing_heat, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 4 — YouTuber Profiles
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-header">👤 Select a YouTuber</p>', unsafe_allow_html=True)

    chosen_yt = st.selectbox(
        "Choose YouTuber for detailed view",
        options=selected_youtubers,
        index=0,
    )

    # Find that YouTuber in the analyzed data
    yt_record = next(
        (y for y in analyzed_data["youtubers"] if y["name"] == chosen_yt),
        None,
    )

    if yt_record:
        summary = yt_record.get("summary", {})
        subs = yt_record.get("subscriber_count", 0)
        views = yt_record.get("view_count", 0)
        n_videos = summary.get("total_videos_analyzed", 0)
        n_transcripts = summary.get("videos_with_transcript", 0)

        # Stats row
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Subscribers",
                  f"{subs / 1_000_000:.1f}M" if subs >= 1_000_000 else f"{subs / 1_000:.0f}K")
        c2.metric("Total Views",
                  f"{views / 1_000_000_000:.1f}B" if views >= 1_000_000_000
                  else f"{views / 1_000_000:.1f}M")
        c3.metric("Videos Analyzed", n_videos)
        c4.metric("With Transcript", n_transcripts)

        col_a2, col_b2, col_c2 = st.columns(3)

        # Top brands for this YouTuber
        with col_a2:
            st.markdown('<p class="section-header">🏷️ Top Brands</p>', unsafe_allow_html=True)
            top_brands_yt = summary.get("top_brands", [])[:10]
            if top_brands_yt:
                df_top_yt = pd.DataFrame(top_brands_yt, columns=["brand", "count"])
                fig_ytb = px.bar(
                    df_top_yt, x="count", y="brand",
                    orientation="h",
                    color="count",
                    color_continuous_scale="RdPu",
                    labels={"count": "Mentions", "brand": ""},
                )
                fig_ytb.update_layout(
                    height=320,
                    yaxis={"autorange": "reversed"},
                    coloraxis_showscale=False,
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                st.plotly_chart(fig_ytb, use_container_width=True)
            else:
                st.info("No brand data.")

        # Category distribution for this YouTuber
        with col_b2:
            st.markdown('<p class="section-header">📂 Categories</p>', unsafe_allow_html=True)
            top_cats_yt = summary.get("top_categories", [])[:8]
            if top_cats_yt:
                df_cat_yt = pd.DataFrame(top_cats_yt, columns=["category", "count"])
                fig_ytc = px.pie(
                    df_cat_yt,
                    names="category", values="count",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                )
                fig_ytc.update_layout(
                    height=320,
                    showlegend=True,
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                st.plotly_chart(fig_ytc, use_container_width=True)
            else:
                st.info("No category data.")

        # Brand sentiment for this YouTuber
        with col_c2:
            st.markdown('<p class="section-header">😊 Brand Sentiment</p>', unsafe_allow_html=True)
            brand_sents_yt = summary.get("brand_sentiments", [])[:8]
            if brand_sents_yt:
                df_sent_yt = pd.DataFrame(brand_sents_yt)
                df_sent_yt["color"] = df_sent_yt["label"].map(SENTIMENT_COLORS)
                fig_yts = go.Figure(go.Bar(
                    x=df_sent_yt["avg_score"],
                    y=df_sent_yt["brand"],
                    orientation="h",
                    marker_color=df_sent_yt["color"],
                    text=df_sent_yt["avg_score"].round(2),
                    textposition="outside",
                ))
                fig_yts.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
                fig_yts.update_layout(
                    height=320,
                    margin=dict(l=10, r=40, t=10, b=10),
                )
                st.plotly_chart(fig_yts, use_container_width=True)
            else:
                st.info("No sentiment data.")

        # Recent videos table
        st.markdown('<p class="section-header">🎬 Recent Videos</p>', unsafe_allow_html=True)
        videos_data = []
        for v in yt_record.get("videos", []):
            analysis = v.get("analysis", {})
            brands_detected = ", ".join(analysis.get("brands", [])[:5])
            overall_sent = analysis.get("overall_sentiment", {})
            videos_data.append({
                "Title": v.get("title", "")[:60],
                "Published": v.get("published_at", "")[:10],
                "Brands Detected": brands_detected or "—",
                "Sentiment": overall_sent.get("label", "—"),
                "Score": round(overall_sent.get("polarity", 0), 2),
                "Has Transcript": "✅" if v.get("transcript") else "❌",
            })
        if videos_data:
            st.dataframe(pd.DataFrame(videos_data), use_container_width=True, hide_index=True)

    # All YouTubers comparison
    st.divider()
    st.markdown('<p class="section-header">📊 All YouTubers Comparison</p>', unsafe_allow_html=True)
    if not df_youtubers.empty:
        fig_compare = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Videos Analyzed", "Videos with Transcript"),
        )
        yt_sorted = df_youtubers.sort_values("videos_analyzed", ascending=True)
        fig_compare.add_trace(
            go.Bar(y=yt_sorted["youtuber"], x=yt_sorted["videos_analyzed"],
                   orientation="h", marker_color="#F48FB1", name="Videos"),
            row=1, col=1,
        )
        fig_compare.add_trace(
            go.Bar(y=yt_sorted["youtuber"], x=yt_sorted["videos_with_transcript"],
                   orientation="h", marker_color="#CE93D8", name="With Transcript"),
            row=1, col=2,
        )
        fig_compare.update_layout(
            height=max(350, len(yt_sorted) * 28),
            showlegend=False,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig_compare, use_container_width=True)


# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.divider()
st.markdown(
    "<p style='text-align:center;color:#aaa;font-size:0.8rem;'>"
    "💄 Beauty Influencer Cosmetics Analytics Dashboard · "
    "Built with Streamlit & Plotly · "
    "Data: YouTube beauty channel analysis"
    "</p>",
    unsafe_allow_html=True,
)
