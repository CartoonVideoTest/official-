import streamlit as st
from abc import ABC, abstractmethod
from urllib.parse import quote


class VideoSource(ABC):
    URL_HEADER = "https://jx.xmflv.com/?url="

    @abstractmethod
    def search(self, query: str) -> list:
        """搜索视频并返回结果列表"""
        pass

    def display_results(self, results: list):
        """展示搜索结果并处理播放逻辑"""
        for idx, item in enumerate(results, start=1):
            with st.container():
                st.markdown("---")
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.subheader(item.get("title", "无标题"))
                    st.caption(item.get("description", ""))

                with col2:
                    if st.button("播放", key=f"play_{self.source_name}_{idx}"):
                        st.session_state.playing_video = f"{self.source_name}_{idx}"

                # 显示当前选中视频的播放器
                if st.session_state.playing_video == f"{self.source_name}_{idx}":
                    play_url = f"{self.URL_HEADER}{quote(item.get('pageUrl', ''))}"
                    st.markdown(
                        f'<iframe src="{play_url}" width="100%" height="500" '
                        'frameborder="0" allowfullscreen></iframe>',
                        unsafe_allow_html=True
                    )