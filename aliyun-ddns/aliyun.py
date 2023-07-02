import json
import httpx
import logging

from mbot.core.plugins import PluginContext, PluginMeta
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from typing import Dict, Any
from mbot.openapi import mbot_api

from .DescribeDomainRecords import Sample as DescribeDomainRecordsSample
from .UpdateDomainRecord import Sample as UpdateDomainRecordSample

server = mbot_api

_LOGGER = logging.getLogger(__name__)


def main_config(config: Dict[str, Any]):
    global uid, ToChannelName, access_key_id, access_key_secret, domain_name, task_enable
    uid = config.get('uid')
    ToChannelName = config.get('ToChannelName')
    access_key_id = config.get('access_key_id')
    access_key_secret = config.get('access_key_secret')
    domain_name = config.get('domain_name')
    task_enable = config.get('task_enable')


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    main_config(config)


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    main_config(config)


@plugin.task('Aliyun-ddns', 'Aliyun-ddns', cron_expression='* * * * *')
def aiproxy_overview_task():
    if task_enable:
        main()


@plugin.command(name='Aliyun-ddns', title='Aliyun-ddns', desc='点击立即更新Aliyun-ddns', icon='AutoAwesome',
                run_in_background=True)
def aiproxy_overview_command(ctx: PluginCommandContext):
    main()
    return PluginCommandResponse(True, f'Aliyun-ddns更新成功！')


def check_record():
    RecordResult = DescribeDomainRecordsSample().main(access_key_id=access_key_id,
                                                      access_key_secret=access_key_secret,
                                                      domain_name=domain_name,
                                                      rr_keyword='@')
    record = RecordResult.body.domain_records.record
    RecordList = []
    for item in record:
        if item.rr != '@':
            continue
        record = {
            'RecordId': item.record_id,
            'RR': item.rr,
            'Type': item.type,
            'DomainName': item.domain_name,
            'Value': item.value,
        }
        RecordList.append(record)
    return json.dumps(RecordList, indent=4, ensure_ascii=False)


def update_record(record_id: str,
                  rr: str,
                  record_type: str,
                  value: str
                  ):
    UpdateResult = UpdateDomainRecordSample().main(access_key_id=access_key_id,
                                                   access_key_secret=access_key_secret,
                                                   record_id=record_id,
                                                   rr=rr,
                                                   record_type=record_type,
                                                   value=value)
    if UpdateResult.status_code == 200:
        return True


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
        r_v4 = httpx.get(v)
        if r_v4.status_code != 200:
            continue
        r_v4 = r_v4.text.rstrip()
        v4_api = k
        break
    for k, v in ipv6_url.items():
        r_v6 = httpx.get(v)
        if r_v6.status_code != 200:
            continue
        r_v6 = r_v6.text.rstrip()
        v6_api = k
        break
    return {"ipv4": r_v4, "v4_api": v4_api, "ipv6": r_v6, "v6_api": v6_api}


def send_notify(title, content):
    channel_item = ToChannelName
    pic = ''
    if uid:
        for _ in uid:
            server.notify.send_message_by_tmpl('{{title}}', '{{a}}', {
                'title': title,
                'a': content,
                'pic_url': pic
            }, to_uid=_, to_channel_name=channel_item)


def main():
    RecordList = json.loads(check_record())
    now_ip = check_now_ip()
    for item in RecordList:
        if item['Type'] == 'A':
            if item['Value'] != now_ip['ipv4']:
                if update_record(record_id=item['RecordId'],
                                 rr=item['RR'],
                                 record_type=item['Type'],
                                 value=now_ip['ipv4']):
                    _LOGGER.info(f'当前IPv4地址为{now_ip["ipv4"]}(来源：{now_ip["v4_api"]})')
                    _LOGGER.info(f'域名{item["RR"]}.{item["DomainName"]}的{item["Type"]}记录已更新为{now_ip["ipv4"]}')
                    send_notify(title=f'DDNS:IP变动',
                                content=f'域名{item["RR"]}.{item["DomainName"]}的{item["Type"]}记录已更新为{now_ip["ipv4"]}', )
            # else:
            #     _LOGGER.info(f'IPv4地址未变化，无需更新')
        elif item['Type'] == 'AAAA':
            if item['Value'] != now_ip['ipv6']:
                if update_record(record_id=item['RecordId'],
                                 rr=item['RR'],
                                 record_type=item['Type'],
                                 value=now_ip['ipv6']):
                    _LOGGER.info(f'当前IPv6地址为{now_ip["ipv6"]}(来源：{now_ip["v6_api"]})')
                    _LOGGER.info(f'域名{item["RR"]}.{item["DomainName"]}的{item["Type"]}记录已更新为{now_ip["ipv6"]}')
                    send_notify(title=f'DDNS:IP变动',
                                content=f'域名{item["RR"]}.{item["DomainName"]}的{item["Type"]}记录已更新为{now_ip["ipv6"]}', )
            # else:
            #     _LOGGER.info(f'IPv6地址未变化，无需更新')
