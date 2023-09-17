from mbot.core.plugins import PluginContext, PluginMeta
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from typing import Dict, Any
from mbot.openapi import mbot_api
import logging
import time

from .utils import set_token_secret
from .restart import restart_docker
from .xiaoya_diy import xiaoya_diy

server = mbot_api

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(message)s")
logging = logging.getLogger("__adrive__")


def set_conf(config: Dict[str, Any]):
    global uid, channel_item, refreshToken, sign_task, reward_enable, xiaoya_task, xiaoya_refresh_token, xiaoya_folder_id
    global xy_diy,db_path,new_head_value,new_body_value,new_readme,portainer_url,portainer_access_token,env,xy_name
    xy_diy = config.get("xy_diy",False)
    db_path = config.get("db_path",'')
    new_head_value = config.get("new_head_value",'')
    new_body_value = config.get("new_body_value",'')
    new_readme = config.get("new_readme",'')
    portainer_url = config.get("portainer_url",'')
    portainer_access_token = config.get("portainer_access_token",'')
    env = config.get("env",'2')
    xy_name = config.get("xy_name",'xiaoya')

    uid = config.get("uid")
    channel_item = config.get("channel_item")
    refreshToken = config.get("refreshToken")
    sign_task = config.get("sign_task")
    reward_enable = config.get("reward_enable")
    if sign_task and not refreshToken:
        logging.error(f"[aliyunpan_signin]:请检查refreshToken是否正确填写。")
        return
    refreshToken_str = set_token_secret(refreshToken)
    logging.info(f"[aliyunpan_signin]:阿里云盘签到正常启动，refreshToken:{refreshToken_str}")
    xiaoya_task = config.get("xiaoya_task")
    if xiaoya_task:
        xiaoya_conf = config.get("xiaoya_conf")
        xiaoya_refresh_token = xiaoya_conf.split(":")[0]
        xiaoya_folder_id = xiaoya_conf.split(":")[1]
        logging.info(f"[aliyunpan_signin]:小雅清理任务正常启动，{xiaoya_refresh_token[:6]}***{xiaoya_refresh_token[-6:]}:{xiaoya_folder_id}")


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    set_conf(config)


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    set_conf(config)


@plugin.task('aliyunpan_signin_task', '阿里云盘签到', cron_expression='10 0 * * *')
def aliyunpan_signin_task():
    if sign_task:
        sign_main()

@plugin.task('xiaoya_diy_task', '小雅自动重启与美化', cron_expression='30 6,11,19 * * *')
def xiaoya_diy_task():
    logging.info(f"「小雅自动重启与美化」开始运行")
    if portainer_url and portainer_access_token:
        rusult = restart_docker(portainer_url, portainer_access_token, env,xy_name)
        logging.info(f"「小雅自动重启」第 1/2 次重启：{rusult}")
        if xy_diy:
            logging.info(f"「小雅自动美化」等待 3 分钟后开始写入美化数据")
            time.sleep(180)
    else:
        logging.warning(f"「小雅自动重启与美化」未设置 Portainer 参数，重启失败。")
    if xy_diy:
        rusult2 = xiaoya_diy(db_path,new_head_value,new_body_value,new_readme)
        logging.info(f"「小雅自动美化」{rusult2}")
        rusult = restart_docker(portainer_url, portainer_access_token, env,xy_name)
        logging.info(f"「小雅自动重启」第 2/2 次重启：{rusult}")
    else:
        logging.warning(f"「小雅自动重启与美化」未开启小雅美化，跳过")
    logging.info(f"「小雅自动重启与美化」运行完成")
        

@plugin.command(name='xiaoya_diy_command', title='小雅重启与美化', desc='点击执行重启和美化', icon='AutoAwesome',
                run_in_background=True)
def xiaoya_diy_command(ctx: PluginCommandContext):
    logging.info(f"「小雅重启与美化」开始手动运行")
    if portainer_url and portainer_access_token:
        rusult = restart_docker(portainer_url, portainer_access_token, env)
        logging.info(f"「小雅重启」第 1/2 次重启：{rusult}")
        if xy_diy:
            logging.info(f"「小雅美化」等待 3 分钟后开始写入美化数据")
            time.sleep(180)
    else:
        logging.warning(f"「小雅重启与美化」未设置 Portainer 参数，重启失败。")
    if xy_diy:
        rusult2 = xiaoya_diy(db_path,new_head_value,new_body_value,new_readme)
        logging.info(f"「小雅美化」{rusult2}")
        rusult = restart_docker(portainer_url, portainer_access_token, env)
        logging.info(f"「小雅重启」第 2/2 次重启：{rusult}")
    else:
        logging.warning(f"「小雅重启与美化」未开启小雅美化，跳过")
    logging.info(f"「小雅重启与美化」运行完成")
    return PluginCommandResponse(True, f'小雅重启与美化执行完成')


@plugin.command(name='aliyunpan_signin_command', title='阿里云盘签到', desc='点击执行阿里云盘签到', icon='AutoAwesome',
                run_in_background=True)
def aliyunpan_signin_command(ctx: PluginCommandContext):
    sign_main()
    return PluginCommandResponse(True, f'阿里云盘签到执行成功')


@plugin.task('xiaoya_clear_task', '清理小雅转存文件夹', cron_expression='0 4 * * *')
def xiaoya_clear_task():
    if xiaoya_task:
        clear_main()


@plugin.command(name='xiaoya_clear_command', title='清理小雅转存文件夹', desc='点击执行清理小雅转存文件夹', icon='AutoAwesome',
                run_in_background=True)
def xiaoya_clear_command(ctx: PluginCommandContext):
    clear_main()
    return PluginCommandResponse(True, f'阿里云盘签到执行成功')


def sign_main():
    from .sign import SignTask
    signTask = SignTask()
    signTask.config(reward_enable=reward_enable,
                    refreshToken=refreshToken,
                    uid=uid,
                    channel_item=channel_item)
    signTask.main()


def clear_main():
    from .clear import ClearFile
    clearFile = ClearFile()
    clearFile.config(xiaoya_refresh_token=xiaoya_refresh_token,
                     xiaoya_folder_id=xiaoya_folder_id,
                     uid=uid,
                     channel_item=channel_item)
    clearFile.main()
