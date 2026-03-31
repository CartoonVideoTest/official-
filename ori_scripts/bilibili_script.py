import requests
import re
from bs4 import BeautifulSoup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0"}

def bilibili_search(search_words: str) -> dict:
    search_results = {}
    
    # 【修复点1】更强的请求头，绕过 B 站反爬
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/",
        "Origin": "https://www.bilibili.com",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="134", "Chromium";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin"
    }

    # 【修复点2】改用 B 站**官方搜索 API**（不会被拦截）
    api_url = f"https://api.bilibili.com/x/web-interface/search/all/v2?keyword={search_words}"

    try:
        import requests
        resp = requests.get(api_url, headers=headers, timeout=15)
        data = resp.json()

        # 从 API 结果里拿番剧 / 影视内容
        for result in data.get("data", {}).get("result", []):
            if result.get("result_type") == "media_bangumi":
                items = result.get("data", [])
                for item in items:
                    title = item.get("title", "").replace("<em class=\"keyword\">", "").replace("</em>", "")
                    cover = item.get("cover", "")
                    url = item.get("url", "")
                    if url and cover:
                        if not url.startswith("http"):
                            url = "https:" + url
                        if not cover.startswith("http"):
                            cover = "https:" + cover
                        search_results[title] = [cover, url]

        # 【修复点3】备用方案：爬网页版（防止API失效）
        if not search_results:
            web_url = f"https://search.bilibili.com/all?keyword={search_words}"
            resp_web = requests.get(web_url, headers=headers, timeout=15)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp_web.text, "html.parser")
            for item in soup.select(".video-item"):
                try:
                    title = item.select_one(".title").get_text(strip=True)
                    cover = item.select_one("img")["src"]
                    url = item.select_one("a")["href"]
                    if url and cover:
                        url = "https:" + url
                        cover = "https:" + cover
                        search_results[title] = [cover, url]
                except:
                    continue

    except Exception as e:
        print(f"B站搜索错误: {e}")

    return search_results


def bilibili_detail(video_url) -> dict[str, str]:
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




