import logging

from mbot.core.params import ArgSchema, ArgType
from mbot.core.plugins import (
    plugin,
    PluginCommandContext,
    PluginCommandResponse,
)

from .event import register, manual

logger = logging.getLogger(__name__)


@plugin.command(
    name="pls_register",
    title="注册短剧数据库认证key",
    desc="输入邮箱地址",
    icon="AutoAwesome",
    run_in_background=False,
)
def pls_register(ctx: PluginCommandContext,
                 email_addr: ArgSchema(ArgType.String, "邮箱地址", "")) -> PluginCommandResponse:
    """
    注册短剧数据库认证key
    :param ctx:  插件上下文
    :param email_addr:  邮箱地址
    :return:
    """
    try:
        r = register(email_addr)
        if r.get("status"):
            logger.info(f"[PLS事件] 注册成功")
            return PluginCommandResponse(True, f"注册成功, 你的access_key为:{r.get('access_key')}")
        return PluginCommandResponse(False, f"注册失败, {r.get('msg')}")
    except Exception as e:
        logger.error(f"注册失败")
        return PluginCommandResponse(False, "注册失败")


task_mode_enum = [
    {
        "name": "刮削存量短剧",
        "value": "scrape_all"
    },
    {
        "name": "刮削单部短剧",
        "value": "scrape_single"
    }
]


@plugin.command(
    name="pls_manual",
    title="PLS手动刮削存量短剧",
    desc="指定下载目录",
    icon="AutoAwesome",
    run_in_background=True,
)
def pls_manual(ctx: PluginCommandContext,
               source_path: ArgSchema(ArgType.String, "文件目录", "手动输入待刮削的目录"),
               task_mode: ArgSchema(ArgType.Enum, '任务类型', '选择任务类型', enum_values=lambda: task_mode_enum, multi_value=False)) -> PluginCommandResponse:
    """
    指定下载目录, 手动刮削存量
    :param ctx:  插件上下文
    :param source_path:  下载目录
    :param task_mode:  任务类型
    :return:
    """
    try:
        manual(source_path, task_mode)
        return PluginCommandResponse(True, "刮削完成")
    except Exception as e:
        logger.error(f"刮削失败: {e}", exc_info=True)
        return PluginCommandResponse(False, "刮削失败")
