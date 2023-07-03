import httpx
import logging

from mbot.core.plugins import PluginMeta
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from mbot.openapi import mbot_api
from typing import Dict, Any


from .Aliyun.aliyun_main import main as aliyun_main
from .DNSPod.dnspod_main import main as dnspod_main

server = mbot_api

_LOGGER = logging.getLogger(__name__)


def main_config(config: Dict[str, Any]):
    global uid, ToChannelName, CloudVendor, key_id, key_secret, domain_name, record_type, task_enable
    uid = config.get('uid')
    ToChannelName = config.get('ToChannelName')
    CloudVendor = config.get('CloudVendor')
    key_id = config.get('key_id')
    key_secret = config.get('key_secret')
    domain_name = config.get('domain_name')
    record_type = config.get('record_type')
    task_enable = config.get('task_enable')


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    main_config(config)


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    main_config(config)


@plugin.task('DDNS', 'DDNS', cron_expression='* * * * *')
def DDNS_task():
    if task_enable:
        main()


@plugin.command(name='DDNS', title='DDNS', desc='点击立即更新DDNS记录', icon='AutoAwesome',
                run_in_background=True)
def DDNS_command(ctx: PluginCommandContext):
    main()
    return PluginCommandResponse(True, f'DDNS记录更新成功！')


def check_now_ip():
    global r_v4, r_v6, v4_api, v6_api
    ipv4_url = {
        "ipsb": "https://api-ipv4.ip.sb/ip"
    }
    ipv6_url = {
        "ipsb": "https://api-ipv6.ip.sb/ip",
        "ident.me": "https://ident.me",
        "ifconfig.io": "https://ifconfig.io/ip"
    }
    for k, v in ipv4_url.items():
        try:
            r_v4 = httpx.get(v)
            if r_v4.status_code != 200:
                continue
            r_v4 = r_v4.text.rstrip()
            v4_api = k
            break
        except:
            continue
    for k, v in ipv6_url.items():
        try:
            r_v6 = httpx.get(v)
            if r_v6.status_code != 200:
                continue
            r_v6 = r_v6.text.rstrip()
            v6_api = k
            break
        except:
            continue
    return {"ipv4": r_v4, "v4_api": v4_api, "ipv6": r_v6, "v6_api": v6_api}


def send_notify(title, content):
    channel_item = ToChannelName
    pic = 'https://s2.loli.net/2023/07/03/JOrRCw8hmEUb35s.jpg'
    if uid:
        for _ in uid:
            server.notify.send_message_by_tmpl('{{title}}', '{{a}}', {
                'title': title,
                'a': content,
                'pic_url': pic
            }, to_uid=_, to_channel_name=channel_item)


def main():
    now_ip = check_now_ip()
    if CloudVendor == 'Aliyun':
        update_result = aliyun_main(access_key_id=key_id,
                                    access_key_secret=key_secret,
                                    domain_name=domain_name,
                                    now_ip=now_ip,
                                    record_type=record_type)
    elif CloudVendor == 'DNSPod':
        update_result = dnspod_main(SecretId=key_id,
                                    SecretKey=key_secret,
                                    domain_name=domain_name,
                                    now_ip=now_ip,
                                    record_type=record_type)
    else:
        update_result = None
    if len(update_result) > 0:
        send_notify(title=f'🌐DDNS: IP变动',
                    content='\n'.join(update_result), )
