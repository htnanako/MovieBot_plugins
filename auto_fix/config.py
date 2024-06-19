import httpx
import os

from mbot.openapi import mbot_api
from moviebotapi.core.models import MediaType

server = mbot_api
server_ak = server.auth.get_default_ak()
port = server.config.web.port


def get_link_setting():
    url = f"http://127.0.0.1:{port}/api/setting/get_link_setting?access_key={server_ak}"
    res = httpx.get(url=url, timeout=30)
    return res.json().get("data")


def get_media_path_setting():
    url = f"http://127.0.0.1:{port}/api/config/get_media_path?access_key={server_ak}"
    res = httpx.get(url=url, timeout=30)
    return res.json().get("data")


def get_all_tv_path():
    media_paths = get_media_path_setting()
    tv_path = []
    for media_path in media_paths.get("paths"):
        if media_path.get("type") == "tv":
            tv_path.append(media_path.get("target_dir"))
    return tv_path


def get_tmdb_info(tmdb_id):
    return server.tmdb.get(media_type=MediaType.TV, tmdb_id=tmdb_id)


def get_all_files(target_folder):
    file_list = []
    for root, dirs, files in os.walk(target_folder):
        for file in files:
            file_list.append(file)
    return file_list
