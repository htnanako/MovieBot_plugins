import logging

from mbot.core.plugins import PluginMeta, plugin, PluginCommandContext, PluginCommandResponse
from mbot.core.params import ArgSchema, ArgType

from .config import *
from .files import fix_filename

logger = logging.getLogger(__name__)


@plugin.command(name='manualfix', title='手动修正识别名', desc='点击手动修正识别名', icon='AutoAwesome',
                run_in_background=True)
def manualfix_command(ctx: PluginCommandContext,
                      path: ArgSchema(ArgType.String, '剧集季度路径', '输入识别错误的剧集季度路径，即Season目录',
                                      required=True),
                      error_name: ArgSchema(ArgType.String, '错误名称', '输入识别错误的剧集名称',
                                            required=True),
                      target_name: ArgSchema(ArgType.String, '指定目标名称', '输入指定整理的目标剧集名称，不指定时默认使用TMDB名称。此参数不会影响自动修正',
                                             required=False),
                      tmdbId: ArgSchema(ArgType.String, 'TMDB ID', '输入正确的TMDB ID',
                                        required=True),
                      season_year: ArgSchema(ArgType.String, '季度发行年份', '输入正确的季度发行年份',
                                             required=True),
                      ):
    if not os.path.exists(path):
        logger.error(f"[AutoFix事件] 路径不存在: 「{path}」")
        return PluginCommandResponse(False, "路径不存在，请检查")
    manual_fix(path, error_name, target_name, season_year, tmdbId)
    return PluginCommandResponse(True, "修正完成")


def manual_fix(path, error_name, target_name, season_year, tmdbId):
    path = path.rstrip("/")
    library_path = None
    for tv_path_item in get_all_tv_path():
        if tv_path_item in path:
            library_path = tv_path_item
            break
    target_path = os.path.dirname(path)
    # 路径的最后一层是Season
    season_number = path.split("/")[-1].replace("Season ", "")
    tmdb_info = get_tmdb_info(tmdbId)
    if target_name:
        tmdb_name = target_name
    else:
        tmdb_name = tmdb_info.name
    media_data = {
        "meta": {
            "title": error_name,
            "originalTitle": tmdb_info.original_name,
            "releaseYear": tmdb_info.first_air_date.split("-")[0],
            "tmdbName": tmdb_name,
            "tmdbId": tmdbId
        },
        "target_path": target_path,
        "library_path": library_path,
        "season_number": season_number,
        "season_year": season_year
    }
    logger.info(f"[AutoFix事件] 开始对 「{error_name}」 进行手动修正")
    logger.info(f"""[AutoFix事件] { {
        "title": media_data.get("meta").get("title"),
        "tmdbName": media_data.get("meta").get("tmdbName"),
        "tmdbId": media_data.get("meta").get("tmdbId"),
        "target_path": media_data.get("target_path"),
        "library_path": media_data.get("library_path"),
        "season_number": media_data.get("season_number"),
        "season_year": media_data.get("season_year")
    } }""")
    fix_filename(media_data)
