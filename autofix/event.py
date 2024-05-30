import logging

from typing import Dict

from mbot.core.event.models import EventType
from mbot.core.plugins import plugin
from mbot.core.plugins import PluginContext

from .config import *
from .files import fix_filename

logger = logging.getLogger(__name__)


@plugin.on_event(bind_event=[EventType.DownloadCompleted], order=1)
def on_event(ctx: PluginContext, event_type: str, data: Dict):
    logger.info(f"[AutoFix事件] 获取到下载完成信息: {data}")
    media_paths = get_media_path_setting()
    source_path = data.get("source_path")
    torrent_hash = data.get("torrent_hash")
    logger.info(f"[AutoFix事件] {source_path} 下载完成，开始运行完成后的处理任务，Hash: {torrent_hash}")
    library_path = data.get("library_path")
    tv_path = []
    for media_path in media_paths.get("paths"):
        if media_path.get("type") == "tv":
            tv_path.append(media_path.get("target_dir"))
    if library_path not in tv_path:
        logger.info(f"[AutoFix事件] {library_path} 不是剧集目录, 跳过")
        return
    title = data.get("x_meta").get("title")
    tmdbId = data.get("x_meta").get("tmdbId")
    tmdb_name = get_tmdb_info(tmdbId).name
    if tmdb_name == title:
        logger.info(f"[AutoFix事件] 文件命名正确, 跳过")
        return
    data.get("x_meta")["tmdb_name"] = tmdb_name
    logger.info(f"[AutoFix事件] 文件命名错误：{tmdb_name} ✔  {title} ✖")
    logger.info(f"[AutoFix事件] 开始修正命名")
    fix_filename(data)

