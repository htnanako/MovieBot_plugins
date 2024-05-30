import httpx

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


def get_tmdb_info(tmdb_id):
    return server.tmdb.get(media_type=MediaType.TV, tmdb_id=tmdb_id)
