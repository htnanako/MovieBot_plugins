import logging
import os
import re
import time
import httpx

from mbot.core.params import ArgSchema, ArgType
from mbot.core.plugins import (
    plugin,
    PluginCommandContext,
    PluginCommandResponse,
)

from . import config
from .files import FilesLink
from .event import register

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


@plugin.command(
    name="pls_manual",
    title="PLS手动刮削存量短剧",
    desc="指定下载目录",
    icon="AutoAwesome",
    run_in_background=True,
)
def pls_manual(ctx: PluginCommandContext,
               source_path: ArgSchema(ArgType.String, "下载目录", "")) -> PluginCommandResponse:
    """
    指定下载目录, 手动刮削存量
    :param ctx:  插件上下文
    :param source_path:  下载目录
    :return:
    """
    # 获取该目录下所有一级文件夹
    dirs = os.listdir(source_path)
    try:
        for dir in dirs:
            # 判断是否为文件夹
            if os.path.isdir(os.path.join(source_path, dir)):
                # 开始刮削
                fl = FilesLink()
                fl.main(os.path.join(source_path, dir))
                time.sleep(10)
        logger.info(f"[PLS事件] 刮削任务完成")
        return PluginCommandResponse(True, "刮削完成")
    except Exception as e:
        logger.error(f"刮削失败: {e}", exc_info=True)
        return PluginCommandResponse(False, "刮削失败")
