import requests




def iqiyi_search(words):

    response = requests.get(f"https://mesh.if.iqiyi.com/portal/lw/search/homePageV3?key={words}")
    result = response.json()["data"]["templates"]

    search_result = {}
    for video in result:
        v_type = video["s3"]
        if v_type == "短视频":
            continue

        try:
            video_one = video["intentAlbumInfos"][0]        # dict
        except:
            video_one = video["albumInfo"]

        video_title = video_one["title"]

        ######################## 暂不可用 ########################
        if video_title == "相关作品":
            new_video_one = video_one["videos"]
            for n_video in new_video_one:
                try:
                    video_url = n_video["pageUrl"]
                except:
                    continue
                video_title = n_video["title"]
                img_url = n_video["img"]
                search_result[video_title] = [img_url, video_url]
        #########################################################

        else:
            try:
                video_url = video_one["pageUrl"]
            except:
                continue
            img_url = video_one["img"]
            search_result[video_title] = [img_url, video_url]


    return search_result


def iqiyi_detail(video_url : str) -> dict[str, str]:
    return {"进入播放视频选集" : video_url}



