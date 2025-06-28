import streamlit as st
from sources.iqiyi_source import IqiyiSource
from sources.tencent_source import TencentSource

# 初始化session状态
if 'search' not in st.session_state:
    st.session_state.search = False
if 'playing_video' not in st.session_state:
    st.session_state.playing_video = None

# 注册视频源
SOURCES = {
    "爱奇艺": IqiyiSource(),
    "腾讯视频": TencentSource()
}

# 侧边栏搜索区域
with st.sidebar:
    st.title("超简洁影视搜索")
    st.write("暂只支持电影播放")
    videoname = st.text_input("输入影视名称：", key="name")
    source_name = st.selectbox("选择源：", list(SOURCES.keys()))

    if st.button("搜索", key="search_btn"):
        if videoname.strip():
            st.session_state.search = True
            st.session_state.source = SOURCES[source_name]
            st.session_state.playing_video = None
        else:
            st.warning("请输入影视名称")

# 主内容区域
if st.session_state.search and hasattr(st.session_state, 'source'):
    st.header(f"搜索结果 - {source_name}")
    try:
        results = st.session_state.source.search(videoname)
        if not results:
            st.warning("未找到相关影视资源")
            st.session_state.search = False
            st.stop()

        st.session_state.source.display_results(results)

    except Exception as e:
        st.error(f"请求失败: {str(e)}")
        st.session_state.search = False
