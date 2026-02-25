"""
뷰티 인플루언서 화장품 분석 대시보드
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ──────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="뷰티 인플루언서 분석",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# 스타일
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

    /* 사이드바 배경 */
    div[data-testid="stSidebarContent"] {
        background-color: #fff8fa;
    }
    /* 사이드바 텍스트 */
    div[data-testid="stSidebarContent"] label,
    div[data-testid="stSidebarContent"] p,
    div[data-testid="stSidebarContent"] span,
    div[data-testid="stSidebarContent"] div {
        color: #333 !important;
    }
    div[data-testid="stSidebarContent"] h2,
    div[data-testid="stSidebarContent"] h3 {
        color: #AD1457 !important;
    }
    /* 멀티셀렉트 태그 */
    div[data-testid="stSidebarContent"] span[data-baseweb="tag"] {
        background-color: #F8BBD9 !important;
        color: #880E4F !important;
    }
    div[data-testid="stSidebarContent"] span[data-baseweb="tag"] span {
        color: #880E4F !important;
    }
    /* 익스팬더 */
    div[data-testid="stSidebarContent"] details summary p {
        color: #555 !important;
        font-weight: 500;
    }
    /* 전체 선택/해제 버튼 */
    div[data-testid="stSidebarContent"] button[kind="secondary"] {
        background-color: #fce4ec !important;
        border: 1px solid #F48FB1 !important;
        color: #880E4F !important;
        font-size: 0.78rem !important;
        padding: 2px 6px !important;
    }
    div[data-testid="stSidebarContent"] button[kind="secondary"]:hover {
        background-color: #F8BBD9 !important;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 데이터 로딩
# ──────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"

SENTIMENT_COLORS = {
    "positive": "#4CAF50",
    "neutral":  "#FFC107",
    "negative": "#F44336",
}

SENTIMENT_KO = {
    "positive": "긍정",
    "neutral":  "중립",
    "negative": "부정",
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

# 세션 상태 초기화
if "youtuber_multiselect" not in st.session_state:
    st.session_state["youtuber_multiselect"] = all_youtubers
if "sentiment_multiselect" not in st.session_state:
    st.session_state["sentiment_multiselect"] = ["positive", "neutral", "negative"]

# ──────────────────────────────────────────────
# 사이드바 필터
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💄 필터")
    st.markdown("---")

    with st.expander("👤 유튜버", expanded=False):
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("전체 선택", use_container_width=True, key="btn_select_all"):
                st.session_state["youtuber_multiselect"] = all_youtubers
        with btn_col2:
            if st.button("전체 해제", use_container_width=True, key="btn_deselect_all"):
                st.session_state["youtuber_multiselect"] = []

        selected_youtubers = st.multiselect(
            "포함할 유튜버 선택",
            options=all_youtubers,
            key="youtuber_multiselect",
            help="비워두면 전체 포함",
            label_visibility="collapsed",
        )

    st.markdown("---")
    with st.expander("😊 감성", expanded=False):
        snt_col1, snt_col2 = st.columns(2)
        with snt_col1:
            if st.button("전체 선택", use_container_width=True, key="btn_sent_all"):
                st.session_state["sentiment_multiselect"] = ["positive", "neutral", "negative"]
        with snt_col2:
            if st.button("전체 해제", use_container_width=True, key="btn_sent_none"):
                st.session_state["sentiment_multiselect"] = []

        selected_sentiments = st.multiselect(
            "감성 필터",
            options=["positive", "neutral", "negative"],
            key="sentiment_multiselect",
            format_func=lambda x: SENTIMENT_KO[x],
            label_visibility="collapsed",
        )

    st.markdown("---")
    top_n_brands = st.slider("🏷️ 상위 브랜드 수", 5, 25, 15)

    st.markdown("---")
    st.markdown("### 📂 소개")
    st.markdown("""
주요 뷰티 유튜버들의 영상에서 화장품 브랜드 언급과
감성 반응을 분석한 대시보드입니다.

**데이터**: 유튜버 20명 · 영상 200개 · 브랜드 언급 375건

**감성 분석**: TextBlob NLP + 뷰티 키워드 매칭
""")

# ──────────────────────────────────────────────
# 필터 적용
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
# 헤더
# ──────────────────────────────────────────────
st.markdown('<p class="main-title">💄 뷰티 인플루언서 화장품 분석</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">유튜브 뷰티 채널의 브랜드 언급 · 감성 분석 · 성분 트렌드를 한눈에</p>', unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 주요 지표
# ──────────────────────────────────────────────
total_yt   = len(df_youtubers)
total_vid  = int(df_youtubers["videos_analyzed"].sum()) if not df_youtubers.empty else 0
total_brd  = df_brands["brand"].nunique() if not df_brands.empty else 0
total_sent = len(df_sentiments)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("👤 유튜버", total_yt)
with col2:
    st.metric("🎬 분석 영상", total_vid)
with col3:
    st.metric("🏷️ 브랜드 수", total_brd)
with col4:
    st.metric("💬 감성 분석 건수", total_sent)

st.divider()

# ──────────────────────────────────────────────
# 탭
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 전체 현황",
    "🏷️ 브랜드 분석",
    "🧪 성분 분석",
    "👤 유튜버 프로필",
])


# ══════════════════════════════════════════════
# TAB 1 — 전체 현황
# ══════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<p class="section-header">🏆 언급 상위 브랜드</p>', unsafe_allow_html=True)
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
                labels={"count": "총 언급 수", "brand": "브랜드"},
                title=f"언급 수 기준 상위 {top_n_brands}개 브랜드",
            )
            fig_brands.update_layout(
                height=480,
                yaxis={"autorange": "reversed"},
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(fig_brands, use_container_width=True)
        else:
            st.info("선택한 필터에 해당하는 브랜드 데이터가 없습니다.")

    with col_right:
        st.markdown('<p class="section-header">📂 제품 카테고리</p>', unsafe_allow_html=True)
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
                title="카테고리 분포",
            )
            fig_cat.update_traces(textposition="outside", textinfo="percent+label")
            fig_cat.update_layout(
                height=480,
                showlegend=False,
                margin=dict(l=90, r=90, t=50, b=50),
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("선택한 필터에 해당하는 카테고리 데이터가 없습니다.")

    st.markdown('<p class="section-header">📈 유튜버 채널 현황</p>', unsafe_allow_html=True)
    if not df_youtubers.empty:
        yt_sorted = df_youtubers.sort_values("subscribers", ascending=False)
        fig_yt = px.bar(
            yt_sorted,
            x="youtuber", y="subscribers",
            color="subscribers",
            color_continuous_scale="Pinkyl",
            labels={"subscribers": "구독자 수", "youtuber": ""},
            title="유튜버별 구독자 수",
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
# TAB 2 — 브랜드 분석
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-header">😊 브랜드 감성 분석</p>', unsafe_allow_html=True)

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
        brand_sent_avg["sentiment_ko"] = brand_sent_avg["sentiment_label"].map(SENTIMENT_KO)
        brand_sent_avg["color"] = brand_sent_avg["sentiment_label"].map(SENTIMENT_COLORS)

        fig_sent = go.Figure(go.Bar(
            x=brand_sent_avg["avg_score"],
            y=brand_sent_avg["brand"],
            orientation="h",
            marker_color=brand_sent_avg["color"],
            text=brand_sent_avg["avg_score"].round(2),
            textposition="outside",
            customdata=brand_sent_avg[["mentions", "sentiment_ko"]],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "평균 감성 점수: %{x:.3f}<br>"
                "총 언급 수: %{customdata[0]}<br>"
                "감성: %{customdata[1]}<extra></extra>"
            ),
        ))
        fig_sent.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig_sent.update_layout(
            height=max(400, len(brand_sent_avg) * 28),
            title="브랜드별 평균 감성 점수",
            xaxis_title="감성 점수 (← 부정 | 긍정 →)",
            margin=dict(l=10, r=60, t=40, b=10),
        )
        st.plotly_chart(fig_sent, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<p class="section-header">📊 감성 분포</p>', unsafe_allow_html=True)
            sent_counts = df_sentiments["label"].value_counts().reset_index()
            sent_counts.columns = ["label", "count"]
            sent_counts["label_ko"] = sent_counts["label"].map(SENTIMENT_KO)
            fig_sd = px.pie(
                sent_counts,
                names="label_ko", values="count",
                color="label",
                color_discrete_map=SENTIMENT_COLORS,
                hole=0.4,
                title="감성 비율",
            )
            fig_sd.update_layout(height=320, margin=dict(t=40, b=10))
            st.plotly_chart(fig_sd, use_container_width=True)

        with col_b:
            st.markdown('<p class="section-header">🏅 긍정 반응 상위 브랜드</p>', unsafe_allow_html=True)
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
                    labels={"avg_score": "평균 감성 점수", "brand": ""},
                    title="긍정 평가 상위 브랜드",
                )
                fig_pos.update_layout(
                    height=320,
                    coloraxis_showscale=False,
                    yaxis={"autorange": "reversed"},
                    margin=dict(l=10, r=10, t=40, b=10),
                )
                st.plotly_chart(fig_pos, use_container_width=True)
            else:
                st.info("긍정 감성 데이터가 없습니다.")
    else:
        st.info("선택한 필터에 해당하는 감성 데이터가 없습니다.")

    st.markdown('<p class="section-header">🔥 유튜버 × 브랜드 히트맵</p>', unsafe_allow_html=True)
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
                title="브랜드 언급 히트맵 (상위 15 유튜버 × 상위 15 브랜드)",
                labels=dict(x="브랜드", y="유튜버", color="언급 수"),
            )
            fig_heat.update_xaxes(tickangle=-40)
            fig_heat.update_layout(
                height=max(400, len(pivot) * 35),
                margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown('<p class="section-header">🤝 인플루언서 간 공통 브랜드</p>', unsafe_allow_html=True)
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
            hovertemplate="<b>%{x}</b><br>%{y}명의 유튜버가 언급<extra></extra>",
        ))
        fig_overlap.update_layout(
            height=380,
            title="가장 많은 유튜버가 언급한 브랜드",
            yaxis_title="유튜버 수",
            xaxis_tickangle=-35,
            margin=dict(l=10, r=10, t=40, b=80),
        )
        st.plotly_chart(fig_overlap, use_container_width=True)

    st.markdown('<p class="section-header">📋 브랜드 데이터</p>', unsafe_allow_html=True)
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
        merged["dominant_label"] = merged["dominant_label"].map(SENTIMENT_KO).fillna("중립")
        merged = merged.sort_values("total_mentions", ascending=False)
        merged.columns = ["브랜드", "총 언급 수", "평균 감성 점수", "감성", "유튜버 수"]
        st.dataframe(merged, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# TAB 3 — 성분 분석
# ══════════════════════════════════════════════
with tab3:
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<p class="section-header">🔬 성분 언급 빈도</p>', unsafe_allow_html=True)
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
                labels={"count": "총 언급 수", "ingredient": "성분"},
                title="가장 많이 언급된 스킨케어 성분",
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
            st.info("선택한 필터에 해당하는 성분 데이터가 없습니다.")

    with col_r:
        st.markdown('<p class="section-header">☁️ 성분 워드 클라우드</p>', unsafe_allow_html=True)
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
                st.info("`wordcloud` 패키지를 설치하면 워드 클라우드를 볼 수 있습니다.")
        else:
            st.info("성분 데이터가 없습니다.")

    st.markdown('<p class="section-header">👤 유튜버별 성분 언급</p>', unsafe_allow_html=True)
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
                title="유튜버별 성분 언급 현황",
                labels=dict(x="성분", y="유튜버", color="언급 수"),
            )
            fig_ing_heat.update_xaxes(tickangle=-35)
            fig_ing_heat.update_layout(
                height=max(360, len(ing_pivot) * 32),
                margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(fig_ing_heat, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 4 — 유튜버 프로필
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-header">👤 유튜버 선택</p>', unsafe_allow_html=True)

    chosen_yt = st.selectbox(
        "상세 분석할 유튜버를 선택하세요",
        options=selected_youtubers,
        index=0,
    )

    yt_record = next(
        (y for y in analyzed_data["youtubers"] if y["name"] == chosen_yt),
        None,
    )

    if yt_record:
        summary = yt_record.get("summary", {})
        subs  = yt_record.get("subscriber_count", 0)
        views = yt_record.get("view_count", 0)
        n_videos      = summary.get("total_videos_analyzed", 0)
        n_transcripts = summary.get("videos_with_transcript", 0)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("구독자",
                  f"{subs / 1_000_000:.1f}M" if subs >= 1_000_000 else f"{subs / 1_000:.0f}K")
        c2.metric("총 조회수",
                  f"{views / 1_000_000_000:.1f}B" if views >= 1_000_000_000
                  else f"{views / 1_000_000:.1f}M")
        c3.metric("분석 영상", n_videos)
        c4.metric("자막 있는 영상", n_transcripts)

        col_a2, col_b2, col_c2 = st.columns(3)

        with col_a2:
            st.markdown('<p class="section-header">🏷️ 주요 브랜드</p>', unsafe_allow_html=True)
            top_brands_yt = summary.get("top_brands", [])[:10]
            if top_brands_yt:
                df_top_yt = pd.DataFrame(top_brands_yt, columns=["brand", "count"])
                fig_ytb = px.bar(
                    df_top_yt, x="count", y="brand",
                    orientation="h",
                    color="count",
                    color_continuous_scale="RdPu",
                    labels={"count": "언급 수", "brand": ""},
                )
                fig_ytb.update_layout(
                    height=320,
                    yaxis={"autorange": "reversed"},
                    coloraxis_showscale=False,
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                st.plotly_chart(fig_ytb, use_container_width=True)
            else:
                st.info("브랜드 데이터가 없습니다.")

        with col_b2:
            st.markdown('<p class="section-header">📂 카테고리</p>', unsafe_allow_html=True)
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
                st.info("카테고리 데이터가 없습니다.")

        with col_c2:
            st.markdown('<p class="section-header">😊 브랜드 감성</p>', unsafe_allow_html=True)
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
                st.info("감성 데이터가 없습니다.")

        st.markdown('<p class="section-header">🎬 최근 영상</p>', unsafe_allow_html=True)
        videos_data = []
        for v in yt_record.get("videos", []):
            analysis = v.get("analysis", {})
            brands_detected = ", ".join(analysis.get("brands", [])[:5])
            overall_sent = analysis.get("overall_sentiment", {})
            label_ko = SENTIMENT_KO.get(overall_sent.get("label", ""), "—")
            videos_data.append({
                "제목": v.get("title", "")[:60],
                "게시일": v.get("published_at", "")[:10],
                "감지된 브랜드": brands_detected or "—",
                "감성": label_ko,
                "점수": round(overall_sent.get("polarity", 0), 2),
                "자막": "✅" if v.get("transcript") else "❌",
            })
        if videos_data:
            st.dataframe(pd.DataFrame(videos_data), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown('<p class="section-header">📊 유튜버 전체 비교</p>', unsafe_allow_html=True)
    if not df_youtubers.empty:
        fig_compare = make_subplots(
            rows=1, cols=2,
            subplot_titles=("분석 영상 수", "자막 있는 영상 수"),
        )
        yt_sorted = df_youtubers.sort_values("videos_analyzed", ascending=True)
        fig_compare.add_trace(
            go.Bar(y=yt_sorted["youtuber"], x=yt_sorted["videos_analyzed"],
                   orientation="h", marker_color="#F48FB1", name="영상"),
            row=1, col=1,
        )
        fig_compare.add_trace(
            go.Bar(y=yt_sorted["youtuber"], x=yt_sorted["videos_with_transcript"],
                   orientation="h", marker_color="#CE93D8", name="자막"),
            row=1, col=2,
        )
        fig_compare.update_layout(
            height=max(350, len(yt_sorted) * 28),
            showlegend=False,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig_compare, use_container_width=True)


# ──────────────────────────────────────────────
# 푸터
# ──────────────────────────────────────────────
st.divider()
st.markdown(
    "<p style='text-align:center;color:#aaa;font-size:0.8rem;'>"
    "💄 뷰티 인플루언서 화장품 분석 대시보드 · "
    "Streamlit &amp; Plotly 기반 · "
    "데이터: 유튜브 뷰티 채널 분석 결과"
    "</p>",
    unsafe_allow_html=True,
)
