import requests
import re
from bs4 import BeautifulSoup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0"}

def bilibili_search(search_words):
    search_urls = ["https://search.bilibili.com/pgc?keyword", "https://search.bilibili.com/bangumi?keyword"]
    search_results = {}

    for search_url in search_urls:
        response = requests.get(f"{search_url}={search_words}", headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        results = soup.select("div.media-card")
        if len(results) == 0:
            continue
        for result in results:
            video_url = result.select_one("a.media-card-image")["href"]
            img_url = "https:" + result.select_one("a.media-card-image>picture.v-img>source:nth-child(2)")["srcset"]
            video_title = result.select_one("div.media-card-content>div>div.media-card-content-head-title>a")["title"]

            search_results[video_title] = [img_url, video_url]
    return search_results


def bilibili_detail(video_url):
    video_counts = {}
    video_id = re.search("(\d+)", video_url.split("/")[-1]).group()
    response = requests.get(f"https://api.bilibili.com/pgc/view/web/ep/list?season_id={video_id}", headers=headers)

    try:
        """ 存在剧集 """
        counts = response.json()["result"]["episodes"]
        for count in counts:
            count_title = count["show_title"]
            url = count["share_url"]
            video_counts[count_title] = url
    except:
        """ 仅单集，大概率为电影 """
        video_counts = { 1 : video_url}

    return video_counts




