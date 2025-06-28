import requests
from urllib.parse import quote
from sources.base_source import VideoSource


class IqiyiSource(VideoSource):
    def __init__(self):
        self.source_name = "iqiyi"

    def search(self, query: str) -> list:
        # 获取爱奇艺数据
        response = requests.get(
            f"https://mesh.if.iqiyi.com/portal/lw/search/homePageV3?key={quote(query)}",
            timeout=10
        )
        response.raise_for_status()
        data = response.json().get("data", {}).get("templates", [{}])[0].get("intentAlbumInfos", [])

        # 格式化结果
        results = []
        for item in data:
            results.append({
                "title": item.get("title", "无标题"),
                "description": item.get("description", ""),
                "pageUrl": item.get("pageUrl", "")
            })
        return results