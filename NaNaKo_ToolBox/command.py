import httpx
import datetime

from cacheout import Cache

from mbot.core.plugins import PluginMeta, plugin, PluginCommandContext, PluginCommandResponse
from mbot.core.params import ArgSchema, ArgType

from .config import *

time_cache = Cache(maxsize=100)


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


@plugin.command(name='install_module', title='安装模块', desc='点击手动安装模块', icon='AutoAwesome',
                run_in_background=True)
def install_module_command(
        ctx: PluginCommandContext,
        module_name: ArgSchema(ArgType.String, '模块名称', '准确输入要安装的模块名称。安装完成后请重启程序。',
                               required=True)):
    from .install_modules import InstallModule
    InstallModule(module_name=module_name).start()
    return PluginCommandResponse(True, f'正在安装「{module_name}」模块，如日志无报错，稍后自行重启容器生效。')


@plugin.command(name='calc_start_time', title='MovieBot启动时间', desc='查看MovieBot启动时间', icon='AutoAwesome',
                run_in_background=False)
def calc_start_time_command(
        ctx: PluginCommandContext):
    extra = calc_start_time()
    return PluginCommandResponse(True, f"MovieBot已运行了「{extra}」")


def restart_app():
    server.common.restart_app()


def clear_notify():
    r = httpx.get(url=f"{base_url}{get_all_sys_notify_api}?access_key={access_key}")
    r_json = r.json()
    if r_json["code"] == 0:
        return True


def calc_start_time():
    def calc_time():
        start_time = time_cache.get('start_time')
        now = datetime.datetime.now()
        return (now - start_time).total_seconds()

    def parse_seconds(seconds):
        seconds = int(seconds)
        months = seconds // (30 * 24 * 3600)
        days = seconds // (24 * 3600)
        days = days % 30
        seconds = seconds % (24 * 3600)
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        all_times = ""
        if months:
            all_times += f"{months}月"
        if days:
            all_times += f"{days}天"
        if hours:
            all_times += f"{hours}小时"
        if minutes:
            all_times += f"{minutes}分"
        if seconds:
            all_times += f"{seconds}秒"
        return all_times

    start_total_seconds = calc_time()
    return parse_seconds(start_total_seconds)
