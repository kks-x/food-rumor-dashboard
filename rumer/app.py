import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="食品安全谣言可视化分析平台",
    layout="wide",
    initial_sidebar_state="expanded"
)

custom_css = """
<style>
.block-container {
    padding-top: 1rem;
}
.card {
    background-color: #f7f9fc;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #e9edf5;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

@st.cache_data
def load_all_data():
    file_map = {
        "rumor1": "./dataSets/rumor1.json",
        "rumor2": "./dataSets/rumor2.json",
        "rumor3": "./dataSets/rumor3.json"
    }
    out = {}
    for k, path in file_map.items():
        with open(path, "r", encoding="utf-8") as f:
            out[k] = json.load(f)
    return out

data_pool = load_all_data()

# 侧边栏：只选择话题
with st.sidebar:
    st.header("📊 控制面板")
    st.divider()
    topic_option = st.selectbox(
        "选择分析话题",
        ["谣言话题1", "谣言话题2", "谣言话题3", "三话题对比"]
    )
    st.info("上方标签切换不同分析图表")

st.title("🍜 食品安全谣言可视化分析平台")
st.divider()

def get_single_data():
    mapping = {
        "谣言话题1": "rumor1",
        "谣言话题2": "rumor2",
        "谣言话题3": "rumor3"
    }
    if topic_option in mapping:
        return data_pool[mapping[topic_option]]
    return None
d = get_single_data()

# ========== 横向并排四个标签（A/B/C/D并列） ==========
tabA, tabB, tabC, tabD = st.tabs([
    "📈 A：传播时间线",
    "🕸️ B：传播网络",
    "💬 C：情感演化",
    "🗺️ D：内容地域"
])

# Tab A 传播时间线
with tabA:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("传播时间线分析：这类话题传播节奏有什么共性")
    st.divider()
    if topic_option != "三话题对比":
        if d and "time_series" in d:
            df_ts = pd.DataFrame(d["time_series"])
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_ts["date"],
                y=df_ts["count"],
                mode="lines+markers",
                name="发文量",
                line=dict(width=2.5, color="#2b7bba")
            ))
            if "interact" in df_ts.columns:
                fig.add_trace(go.Scatter(
                    x=df_ts["date"],
                    y=df_ts["interact"],
                    mode="lines+markers",
                    name="互动量",
                    line=dict(width=2.5, color="#ff884b")
                ))
            fig.update_layout(height=480)
            st.plotly_chart(fig, use_container_width=True)
            if "time_phase" in d:
                st.subheader("传播阶段划分表")
                st.dataframe(pd.DataFrame(d["time_phase"]), use_container_width=True)
        else:
            st.warning("缺少 time_series 时序数据")
    else:
        fig = go.Figure()
        colors = ["#2b7bba", "#ff884b", "#37ae68"]
        names = ["谣言话题1", "谣言话题2", "谣言话题3"]
        for idx, k in enumerate(["rumor1", "rumor2", "rumor3"]):
            dd = data_pool[k]
            if "time_series" in dd:
                df = pd.DataFrame(dd["time_series"])
                fig.add_trace(go.Scatter(
                    x=df["date"], y=df["count"],
                    name=names[idx],
                    line=dict(width=2., color=colors[idx])
                ))
        fig.update_layout(height=480)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Tab B 传播网络
with tabB:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("传播网络分析：这类话题由谁驱动、传播结构是什么样")
    st.divider()
    if d and "network_edges" in d and "network_nodes" in d:
        edges = pd.DataFrame(d["network_edges"])
        nodes = pd.DataFrame(d["network_nodes"])
        fig = px.scatter(nodes, x="x", y="y", size="weight", hover_data=["uid", "username"])
        for _, e in edges.iterrows():
            fig.add_trace(go.Scatter(
                x=[e["x1"], e["x2"]],
                y=[e["y1"], e["y2"]],
                mode="lines",
                line=dict(color="#999", width=0.7),
                showlegend=False
            ))
        fig.update_layout(height=480)
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("🏆 关键用户节点排行")
        st.dataframe(nodes.sort_values("weight", ascending=False), use_container_width=True)
    else:
        st.warning("等待组员B填充网络数据 network_nodes / network_edges")
    st.markdown("</div>", unsafe_allow_html=True)

# Tab C 情感演化
with tabC:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("情感演化分析：这类话题的情绪怎么随传播变化")
    st.divider()
    if d and "sentiment_time" in d:
        df_sent = pd.DataFrame(d["sentiment_time"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_sent["date"], y=df_sent["neg"], name="负面", line=dict(color="#e74c3c")))
        fig.add_trace(go.Scatter(x=df_sent["date"], y=df_sent["neu"], name="中性", line=dict(color="#f39c12")))
        fig.add_trace(go.Scatter(x=df_sent["date"], y=df_sent["pos"], name="正面", line=dict(color="#27ae60")))
        fig.update_layout(height=480)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("缺少 sentiment_time 情感时序数据")
    if d and "sentiment_word_list" in d:
        st.subheader("情绪关键词词云")
        words = " ".join(d["sentiment_word_list"])
        wc = WordCloud(background_color="white", width=900, height=320).generate(words)
        fig_w, ax = plt.subplots(figsize=(10,4))
        ax.imshow(wc)
        ax.axis("off")
        st.pyplot(fig_w)
    st.markdown("</div>", unsafe_allow_html=True)

# Tab D 内容地域
with tabD:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("内容与地域分析：这类话题的话术与扩散范围")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if d and "hot_word_list" in d:
            st.subheader("全局热词词云")
            words = " ".join(d["hot_word_list"])
            wc = WordCloud(background_color="white", width=600, height=320).generate(words)
            fig_w, ax = plt.subplots(figsize=(8,4))
            ax.imshow(wc)
            ax.axis("off")
            st.pyplot(fig_w)
        else:
            st.warning("缺少 hot_word_list 热词")
    with col2:
        if d and "word_time_series" in d:
            st.subheader("关键词热度演化")
            df_w = pd.DataFrame(d["word_time_series"])
            fig = px.line(df_w, x="date", y="cnt", color="word")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("缺少 word_time_series 词频演化数据")
    st.subheader("🗺️ 地域分布热力图")
    if d and "region_data" in d:
        df_r = pd.DataFrame(d["region_data"])
        fig_map = px.choropleth(
            df_r,
            locations="province",
            locationmode="china",
            color="count",
            hover_data=["province", "count"]
        )
        fig_map.update_layout(height=420)
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("缺少 region_data 地域数据")
    st.markdown("</div>", unsafe_allow_html=True)
