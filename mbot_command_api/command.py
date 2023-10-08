import httpx
from mbot.core.plugins import PluginMeta
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse

from .config import *


@plugin.command(name='restart', title='重启程序', desc='点击重启主程序', icon='AutoAwesome',
                run_in_background=True)
def restart_command(ctx: PluginCommandContext):
    restart_app()
    return PluginCommandResponse(True, f'主程序重启成功！')


@plugin.command(name='clear_notify', title='清除所有系统通知', desc='点击清除所有系统通知', icon='AutoAwesome',
                run_in_background=True)
def clear_notify_command(ctx: PluginCommandContext):
    if clear_notify():
        return PluginCommandResponse(True, f'所有系统通知已清除！')


def restart_app():
    server.common.restart_app()


def clear_notify():
    r = httpx.get(url=f"{base_url}{get_all_sys_notify_api}?access_key={access_key}")
    r_json = r.json()
    if r_json["code"] == 0:
        return True
