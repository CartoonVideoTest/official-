import requests
from sources.base_source import VideoSource


class TencentSource(VideoSource):
    def __init__(self):
        self.source_name = "tencent"

    def search(self, query: str) -> list:
        # 请求参数
        request_data = {
            "version": "25061301",
            "clientType": 1,
            "filterValue": "",
            "uuid": "2943A369-EBE8-4708-8A01-9CD01341A8BD",
            "retry": 0,
            "query": query,
            "pagenum": 0,
            "isPrefetch": True,
            "pagesize": 30,
            "queryFrom": 0,
            "searchDatakey": "",
            "transInfo": "",
            "isneedQc": True,
            "preQid": "",
            "adClientInfo": "",
            "extraInfo": {
                "isNewMarkLabel": "1",
                "multi_terminal_pc": "1",
                "themeType": "1",
                "sugRelatedIds": "{}",
                "appVersion": ""
            }
        }

        headers = {
            "origin": "https://v.qq.com",
            "referer": "https://v.qq.com/",
        }

        # 获取腾讯视频数据
        response = requests.post(
            url="https://pbaccess.video.qq.com/trpc.videosearch.mobile_search.MultiTerminalSearch/MbSearch?vplatform=2",
            json=request_data,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        # 处理响应数据
        json_data = response.json()
        area_box_list = json_data.get("data", {}).get("areaBoxList", [])
        if not area_box_list:
            return []

        items = area_box_list[0].get("itemList", [])
        if not items:
            return []

        # 格式化结果
        results = []
        for item in items:
            video_info = item.get("videoInfo", {})
            play_sites = video_info.get("playSites", [])
            episode_info = play_sites[0].get("episodeInfoList", [{}])[0] if play_sites else {}

            results.append({
                "title": video_info.get("title", "无标题"),
                "description": "来源: 腾讯视频",
                "pageUrl": episode_info.get("url", "")
            })
        return results