import re
import requests

headers = {
    'origin': 'https://v.qq.com',
    'referer': 'https://v.qq.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
}

def tencent_search(video_name : str) -> dict[str, list]:
    data = {"version":"26022601",
            "clientType":1,
            "filterValue":"",
            "uuid":"D553A7BE-6EE3-4E01-8A64-399FF00D7D55",
            "retry":0,
            "query":video_name,
            "pagenum":0,
            "isPrefetch":True,
            "pagesize":30,
            "queryFrom":0,
            "searchDatakey":"",
            "transInfo":"",
            "isneedQc":True,
            "preQid":"",
            "adClientInfo":"",
            "extraInfo":{"isNewMarkLabel":"1","multi_terminal_pc":"1","themeType":"1","sugRelatedIds":"{}","appVersion":"","frontVersion":"26031209"},"featureList":["DEFAULT_FEFEATURE","PC_SHORT_VIDEOS_WATERFALL"]}
    search_results = {}

    response = requests.post("https://pbaccess.video.qq.com/trpc.videosearch.mobile_search.MultiTerminalSearch/MbSearch?vversion_platform=2",
                             headers=headers,
                             json=data)

    """
    搜名字只有单集电影，典型代表《肖申克的救赎》
    """
    results1 = response.json()["data"]["normalList"]["itemList"]
    results2 = response.json()["data"]["areaBoxList"][0]["itemList"]
    for data in [results1, results2]:
        for result_one in data:
            try:
                result = result_one["videoInfo"]

                subTitle = result["subTitle"]
                if subTitle in ["来源·外站", "全网搜"]:
                    continue
                video_url = result["playSites"][0]["episodeInfoList"][0]["url"]
                if not video_url:
                    continue
                video_type = result["typeName"]
                video_title = result["title"] + f"({video_type})"

                img_url = result["imgUrl"]
                search_results[video_title] = [img_url, video_url]
            except:
                continue

    """
    搜名字存在集合型，典型代表《谍影重重》系列、《海绵宝宝》系列
    """
    # videos = response.json()["data"]["areaBoxList"][0]["itemList"]
    # for video_one in videos:
    #     try:
    #         video = video_one["videoInfo"]
    #
    #         subTitle = video["subTitle"]
    #         if subTitle in ["来源·外站", "全网搜"]:
    #             continue
    #         video_url = video["playSites"][0]["episodeInfoList"][0]["url"]
    #         if not video_url:
    #             continue
    #         video_type = video["typeName"]
    #         video_title = video["title"] + f"({video_type})"
    #         img_url = video["imgUrl"]
    #         search_results[video_title] = [img_url, video_url]
    #     except:
    #         continue

    return search_results


def tencent_detail(video_url : str) -> dict[str, str]:
    video_id_change = video_url.split("/")[-1].split(".")[0]
    video_counts = {}

    response = requests.get(video_url, headers=headers)
    video_id = re.search('video_ids:(.+?)]', response.text).group(1).replace("[", "").replace('"','').split(",")
    n=1
    for video_one_id in video_id:
        video_counts[n] = video_url.replace(video_id_change, video_one_id)
        n+=1
    return video_counts

