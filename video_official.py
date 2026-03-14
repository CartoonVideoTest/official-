import streamlit as st
import requests
import re
from bs4 import BeautifulSoup

# ==================== 配置区域 ====================
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0"
}

# 视频解析接口
ANALYSE_HEADERS = {
    "解析1（优先电影）": "https://jx.xmflv.com/?url=",
    "解析2（建议电视剧）": "https://yparse.ik9.cc/index.php?url=",
    "解析3（最好用的吧）": "https://jx.playerjy.com/?url="
}

# 支持的搜索源
SEARCH_SOURCES = ["bilibili", "腾讯视频", "爱奇艺"]


# ==================== B站相关函数 ====================

@st.cache_data(ttl=3600)  # 缓存1小时
def bilibili_search(search_words):
    """
    在B站搜索视频
    """
    if not search_words:
        return {}

    search_urls = [
        "https://search.bilibili.com/pgc?keyword",
        "https://search.bilibili.com/bangumi?keyword"
    ]
    search_results = {}

    try:
        for search_url in search_urls:
            response = requests.get(f"{search_url}={search_words}", headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            results = soup.select("div.media-card")
            if len(results) == 0:
                continue

            for result in results:
                try:
                    video_url = result.select_one("a.media-card-image")["href"]
                    img_elem = result.select_one("a.media-card-image>picture.v-img>source:nth-child(2)")
                    img_url = "https:" + img_elem["srcset"] if img_elem else ""
                    title_elem = result.select_one("div.media-card-content>div>div.media-card-content-head-title>a")
                    video_title = title_elem["title"] if title_elem else "未知标题"

                    search_results[video_title] = [img_url, video_url]
                except Exception as e:
                    st.warning(f"解析视频条目时出错: {e}")
                    continue

    except requests.exceptions.Timeout:
        st.error("B站搜索请求超时，请稍后重试")
    except requests.exceptions.RequestException as e:
        st.error(f"B站搜索请求失败: {e}")
    except Exception as e:
        st.error(f"搜索过程中发生未知错误: {e}")

    return search_results


@st.cache_data(ttl=3600)
def bilibili_detail(video_url):
    """
    获取B站视频详情（剧集信息）
    """
    video_counts = {}

    try:
        video_id_match = re.search("(\d+)", video_url.split("/")[-1])
        if not video_id_match:
            return {1: video_url}

        video_id = video_id_match.group()
        response = requests.get(
            f"https://api.bilibili.com/pgc/view/web/ep/list?season_id={video_id}",
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        if data.get("code") != 0:
            return {1: video_url}

        # 处理剧集
        if "result" in data and "episodes" in data["result"]:
            counts = data["result"]["episodes"]
            for count in counts:
                count_title = count.get("show_title", f"第{len(video_counts) + 1}集")
                url = count.get("share_url", video_url)
                video_counts[count_title] = url
        else:
            # 单集（可能是电影）
            video_counts = {1: video_url}

    except Exception as e:
        st.warning(f"获取视频详情失败: {e}")
        video_counts = {1: video_url}

    return video_counts


# ==================== UI组件函数 ====================

def embed_video_iframe(video_url):
    """
    使用iframe嵌入视频
    """
    iframe_html = f"""
    <iframe 
        width=100% 
        height=500
        src="{video_url}"
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen>
    </iframe>
    """
    st.markdown(iframe_html, unsafe_allow_html=True)


def show_disclaimer():
    """
    显示免责声明
    """
    st.success("此网站只用于测试，无商业用途")
    st.warning("视频内的广告请勿轻信")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("了解", key="ensure"):
            st.session_state["ensure_play"] = True
            st.rerun()

    with c2:
        if st.link_button("跳转", "https://www.mps.gov.cn/"):
            st.session_state["ensure_play"] = False


def render_sidebar():
    """
    渲染侧边栏搜索界面
    """
    with st.sidebar:
        st.title("🔍 视频检索")
        st.write("---")

        input_words = st.text_input("输入关键词：", key="search_input")
        ori_search = st.selectbox("搜索源：", SEARCH_SOURCES, key="search_source")

        if st.button("搜索", type="primary", use_container_width=True):
            if not input_words:
                st.warning("请输入搜索关键词")
            else:
                st.session_state["search_data"] = {}
                st.session_state["search"] = True
                st.session_state["last_search"] = input_words
                st.rerun()

        return input_words, ori_search


def render_search_results(input_words, ori_search):
    """
    渲染搜索结果
    """
    st.write(f"📌 搜索源：**{ori_search}**")
    st.write(f"📝 搜索词：**{input_words}**")
    st.write("---")

    if ori_search == "bilibili":
        with st.spinner("正在搜索B站视频..."):
            if st.session_state["search_data"]:
                results = st.session_state["search_data"]
            else:
                results = bilibili_search(input_words)
                st.session_state["search_data"] = results

        if not results:
            st.warning("⚠️ 未检索到相关视频")
            return

        for idx, (title, video_detail) in enumerate(results.items()):
            img_url, count_url = video_detail

            col1, col2 = st.columns([1, 2])
            with col1:
                # 使用默认图片（B站图片URL可能无法直接显示）
                st.image("https://www.bilibili.com/favicon.ico", width=100)

            with col2:
                st.subheader(title)

                # 获取剧集信息
                counts = bilibili_detail(count_url)
                if counts:
                    select_count = st.selectbox(
                        "选择剧集：",
                        list(counts.keys()),
                        key=f"count_{idx}"
                    )

                    if st.button("▶️ 播放", key=f"play_{title}_{idx}"):
                        st.session_state["search"] = False
                        st.session_state["play"] = True
                        st.session_state["select_v"] = [
                            title,
                            select_count,
                            counts[select_count]
                        ]
                        st.rerun()

            st.write("---")

    elif ori_search in ["腾讯视频", "爱奇艺"]:
        st.info(f"🔜 {ori_search} 搜索功能正在开发中...")
        # 这里可以添加其他平台的搜索逻辑


def render_player():
    """
    渲染播放器界面
    """
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("◀️ 返回", key="back_last_page", use_container_width=True):
            st.session_state["play"] = False
            st.session_state["search"] = True
            st.session_state["select_v"] = ''
            st.rerun()

    with col2:
        title = st.session_state["select_v"][0]
        title_step = st.session_state["select_v"][1]
        play_url = st.session_state["select_v"][2]
        st.write(f"🎬 **{title}**")
        st.write(f"📺 {title_step}")
        st.caption(f"🔗 {play_url[:50]}..." if len(play_url) > 50 else f"🔗 {play_url}")

    with col3:
        select_ana = st.selectbox("选择解析接口：", ANALYSE_HEADERS.keys())

    st.write("---")

    # 播放视频
    with st.spinner("正在加载视频..."):
        embed_video_iframe(ANALYSE_HEADERS[select_ana] + play_url)


# ==================== 主程序 ====================

def main():
    """
    主程序入口
    """
    # 页面配置
    st.set_page_config(
        page_title="视频检索播放器",
        page_icon="🎬",
        layout="wide"
    )

    # 初始化session state
    if "search" not in st.session_state:
        st.session_state["search"] = False
    if "search_data" not in st.session_state:
        st.session_state["search_data"] = {}
    if "play" not in st.session_state:
        st.session_state["play"] = False
    if "select_v" not in st.session_state:
        st.session_state["select_v"] = []
    if "ensure_play" not in st.session_state:
        st.session_state["ensure_play"] = False

    # 显示标题
    st.title("🎥 视频检索播放器")

    # 免责声明
    if not st.session_state["ensure_play"]:
        show_disclaimer()
    else:
        # 侧边栏
        input_words, ori_search = render_sidebar()

        # 主内容区
        if st.session_state["play"]:
            render_player()
        elif st.session_state["search"]:
            if input_words:
                render_search_results(input_words, ori_search)
            else:
                st.info("👈 请在侧边栏输入关键词开始搜索")
        else:
            st.info("👈 在侧边栏搜索视频开始使用")

            # 显示使用说明
            with st.expander("📖 使用说明"):
                st.markdown("""
                ### 如何使用
                1. 在左侧侧边栏输入搜索关键词
                2. 选择搜索源（目前支持B站）
                3. 点击搜索按钮
                4. 从结果中选择要播放的视频和剧集
                5. 选择合适的解析接口播放视频

                ### 注意事项
                - 如果视频无法播放，可以尝试切换不同的解析接口
                - 部分视频可能需要代理才能正常访问
                - 本工具仅用于技术学习，请勿用于商业用途
                """)


if __name__ == "__main__":
    main()