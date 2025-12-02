import streamlit as st
import requests
from bs4 import BeautifulSoup

# 爱奇艺搜索逻辑
def iqy_search(search_name):
    try:
        response = requests.get(f"https://mesh.if.iqiyi.com/portal/lw/search/homePageV3?key={search_name}")
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()["data"]["templates"][0]
        page_type = data["s3"]
        count_page = {}
        video_dict = {}
        
        if page_type == "电影类长视频":
            movie_name = data["albumInfo"]["title"]
            video_dict[movie_name] = ""
            count_page[movie_name] = video_dict
        else:
            try:
                video_name = data["albumInfo"]["title"]
                videos = data["albumInfo"]["videos"]
                for video in videos:
                    video_url = video.get("pageUrl", "")
                    video_dict[video["title"]] = video_url
                count_page[video_name] = video_dict
            except:
                videos = data["intentAlbumInfos"]
                for video in videos:
                    video_name = video["title"]
                    video_url = video.get("pageUrl", "")
                    video_dict[video["title"]] = video_url
                    count_page[video_name] = video_dict
        return count_page
    except Exception as e:
        st.error(f"爱奇艺搜索出错: {str(e)}")
        return {}

# Bilibili集数获取逻辑
def bili_count_videos(url):
    try:
        if "/ss" in url:
            season_id = url.split("/ss")[1].split("?")[0]
        else:
            season_id = url.split("/ep")[1].split("?")[0]

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0"
        }
        
        try:
            url_id = f"https://api.bilibili.com/pgc/view/web/ep/list?season_id={season_id}"
            response = requests.get(url_id, headers=headers)
            response.raise_for_status()
            result = response.json()["result"]["episodes"]
        except:
            url_id = f"https://api.bilibili.com/pgc/view/web/ep/list?ep_id={season_id}"
            response = requests.get(url_id, headers=headers)
            response.raise_for_status()
            result = response.json()["result"]["episodes"]

        video_list = {}
        for n, video in enumerate(result, 1):
            video_list[n] = "https://jx.xmflv.cc/?url=" + video["share_url"]
        return video_list
    except Exception as e:
        st.error(f"获取B站集数出错: {str(e)}")
        return {}

# Bilibili搜索逻辑
def bili_search(search_name):
    try:
        video_type = ["bangumi", "pgc"]
        video_dict = {}
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0"
        }
        
        for ty in video_type:
            response = requests.get(
                url=f"https://search.bilibili.com/{ty}?keyword={search_name}",
                headers=headers
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            results = soup.select("div.media-card-content-head-title>a")
            
            for video in results:
                title = video.text.replace("\n", "").strip()
                url = video.get("href", "")
                if title and url:
                    video_dict[title] = url
        return video_dict
    except Exception as e:
        st.error(f"B站搜索出错: {str(e)}")
        return {}

# 主应用
def main():
    st.set_page_config(page_title="视频搜索", layout="wide")
    st.title("视频搜索平台")

    # 侧边栏设置
    with st.sidebar:
        st.header("搜索设置")
        search_term = st.text_input("输入搜索关键词")
        search_sources = st.selectbox(
            "选择搜索源",
            ["哔哩哔哩","爱奇艺"]
            )
        search_button = st.button("搜索")

    # 存储搜索结果的会话状态
    if 'search_results' not in st.session_state:
        st.session_state.search_results = {}
    
    if 'selected_episode' not in st.session_state:
        st.session_state.selected_episode = {}

    # 执行搜索
    if search_button and search_term and search_sources:
        st.session_state.search_results = {}
        st.session_state.selected_episode = {}
        
        # 爱奇艺搜索
        if "爱奇艺" in search_sources:
            with st.spinner("正在从爱奇艺搜索..."):
                iqy_results = iqy_search(search_term)
                if iqy_results:
                    st.session_state.search_results["爱奇艺"] = iqy_results
        
        # B站搜索
        if "哔哩哔哩" in search_sources:
            with st.spinner("正在从哔哩哔哩搜索..."):
                bili_results = bili_search(search_term)
                if bili_results:
                    st.session_state.search_results["哔哩哔哩"] = bili_results

    # 展示搜索结果
    if st.session_state.search_results:
        for source, results in st.session_state.search_results.items():
            st.subheader(f"来自 {source} 的结果")
            
            if source == "爱奇艺":
                for main_title, episodes in results.items():
                    with st.expander(f"📺 {main_title}"):
                        if episodes:
                            selected_ep = st.selectbox(
                                "选择集数",
                                list(episodes.keys()),
                                key=f"iqy_{main_title}"
                            )
                            if selected_ep:
                                episode_url = episodes[selected_ep]
                                st.text(f"选中集数链接: {episode_url}")
            
            elif source == "哔哩哔哩":
                for title, url in results.items():
                    with st.expander(f"📺 {title}"):
                        with st.spinner("获取集数信息..."):
                            episodes = bili_count_videos(url)
                            if episodes:
                                selected_ep = st.selectbox(
                                    "选择集数",
                                    list(episodes.keys()),
                                    key=f"bili_{title}"
                                )
                                if selected_ep:
                                    episode_url = episodes[selected_ep]
                                    st.text(f"选中集数链接: https://jx.xmflv.cc/?url={episode_url}")

if __name__ == "__main__":

    main()

