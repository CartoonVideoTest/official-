import streamlit as st
from ori_scripts.bilibili_script import bilibili_search as search_b
from ori_scripts.bilibili_script import bilibili_detail as detail_b
from ori_scripts.tencent_script import tencent_search as search_t
from ori_scripts.tencent_script import tencent_detail as detail_t
from ori_scripts.iqiyi_script import iqiyi_search as search_i
from ori_scripts.iqiyi_script import iqiyi_detail as detail_i




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

def video_show_page(search_def, detail_def):

    if st.session_state["search_data"] != {}:
        results = st.session_state["search_data"]
    else:
        results = search_def(input_words)
        st.session_state["search_data"] = results

    if not results:
        st.warning("未检索到相关视频")

    for title, video_detail in results.items():
        img_url = video_detail[0]
        count_url = video_detail[1]

        col1, col2 = st.columns(2)
        with col1:
            st.image(img_url)

        with col2:
            st.title(title)
            counts = detail_def(count_url)
            select_count = st.selectbox("选择：", counts.keys(), key=title)
            if st.button("播放", key=f"{title}_{select_count}"):
                st.session_state["search"] = False
                st.session_state["play"] = True
                st.session_state["select_v"] = [title, select_count, counts[select_count]]
                st.rerun()

        st.write("---")


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



if not st.session_state["ensure_play"]:
    st.success("此网站只用于测试，无商业用途")
    st.error("视频内的广告请勿轻信")
    st.warning("上当受骗鄙人概不负责")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("了解", key="ensure"):
            st.session_state["ensure_play"] = True
            st.rerun()

    with c2:
        if st.link_button("跳转", "https://www.mps.gov.cn/"):
            st.session_state["ensure_play"] = False


else:

    # 正式框架
    with st.sidebar:
        st.title("视频检索")
        st.write("---")

        ori_list = ["腾讯视频", "bilibili", "爱奇艺"]
        input_words = st.text_input("输入关键词：")
        ori_search = st.selectbox("搜索源：", ori_list)
        if st.button("搜索"):
            st.session_state["search_data"] = {}
            st.session_state["search"] = True


    if st.session_state["search"]:
        st.write(f"搜索源：{ori_search}")
        st.write(f"搜索词：{input_words}")

        st.write("---")

        if ori_search == "bilibili":
            video_show_page(search_b, detail_b)

        if ori_search == "腾讯视频":
            video_show_page(search_t, detail_t)

        if ori_search == "爱奇艺":
            video_show_page(search_i, detail_i)


    if st.session_state["play"]:
        analyse_headers = {
            "解析1（优先电影）" : "https://jx.xmflv.com/?url=",
            "解析2（建议电视剧）" : "https://yparse.ik9.cc/index.php?url=",
            "解析3（最好用的吧）" : "https://jx.playerjy.com/?url="
        }

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("<返回", key = "back_last_page"):
                st.session_state["play"] = False
                st.session_state["search"] = True
                st.session_state["select_v"] = ''
                st.rerun()

        with col2:
            title = st.session_state["select_v"][0]
            title_step = st.session_state["select_v"][1]
            play_url = st.session_state["select_v"][2]
            st.write(f"正在播放：{title}")
            st.write(f"播放集数：{title_step}")
            st.write(f"播放链接：{play_url}")

        with col3:
            select_ana = st.selectbox("选择解析：", analyse_headers.keys())

        st.write("---")

        embed_video_iframe(analyse_headers[select_ana] + play_url)



