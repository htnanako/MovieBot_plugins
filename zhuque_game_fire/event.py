from mbot.core.plugins import plugin, PluginContext, PluginMeta, PluginCommandContext, PluginCommandResponse
from mbot.openapi import mbot_api
from typing import Dict, Any
import logging
import httpx
import json
import time
import datetime
import random
from dateutil.parser import parse
from threading import Thread

server = mbot_api
_LOGGER = logging.getLogger(__name__)

url = 'https://zhuque.in/api/gaming/listGenshinCharacter'
fire_url = 'https://zhuque.in/api/gaming/fireGenshinCharacterMagic'
img_url = "https://s2.loli.net/2023/02/08/7IOmzLKbPZGDNC2.jpg"


def async_call(fn):
    def wrapper(*args, **kwargs):
        Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


@async_call
def start_main():
    times, has_character = zhuque_character()
    try:
        now_time = parse(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        if now_time >= times:
            if fire():
                return
            else:
                time.sleep(random.randint(10, 15) * 60)
                start_main()
        else:
            delta = times - now_time
            delta_second = delta.total_seconds()
            remain_time = parse_seconds(delta_second)
            logging.info(f'[zhuque_game_file]:开始睡觉，{remain_time}后起来干活。')
            time.sleep(int(delta_second) + random.randint(300, 600))
            start_main()
    except Exception as e:
        logging.error(f'[zhuque_game_file]:释放技能出错了,错误信息：{e}', exc_info=True)
        return


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    global message_to_uid, channel, task_switch, cookie, x_csrf_token
    message_to_uid = config.get('uid')
    channel = config.get('ToChannelName')
    task_switch = config.get('task_switch')
    cookie = config.get('cookie')
    x_csrf_token = config.get('x_csrf_token')
    _LOGGER.info(f'[zhuque_game_file]:ZHUQUE释放技能插件初始化完成。')
    if task_switch:
        start_main()


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    _LOGGER.info('[zhuque_game_file]:ZHUQUE释放技能插件配置更新。')
    global message_to_uid, channel, task_switch, cookie, x_csrf_token
    message_to_uid = config.get('uid')
    channel = config.get('ToChannelName')
    task_switch = config.get('task_switch')
    cookie = config.get('cookie')
    x_csrf_token = config.get('x_csrf_token')
    

@plugin.task('zhuque_fire_task', '执行朱雀批量释放技能', cron_expression='0 0 * * *')
def task():
    if task_switch:
        start_main()


@plugin.command(name='zhuque_fire', title='释放技能', desc='朱雀站批量释放技能', icon='LocalFireDepartment', run_in_background=True)
def zhuque_fire_echo(ctx: PluginCommandContext):
    _LOGGER.info(f'开始获取角色信息')
    times, has_character = zhuque_character()
    try:
        now_time = parse(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        if now_time >= times:
            fire()
            return PluginCommandResponse(True, f'释放技能成功')
        else:
            delta = times - now_time
            delta_second = delta.total_seconds()
            remain_time = parse_seconds(delta_second)
            _LOGGER.info(f'[zhuque_game_file]:时间未到。还需要{remain_time}')
            return PluginCommandContext(True, f'时间未到。')
    except Exception as e:
        logging.error(f'[zhuque_game_file]:释放技能出错了,错误信息：{e}', exc_info=True)
        return PluginCommandResponse(False, f'释放技能出错了,{e}')


def zhuque_character():
    has_character, times_list = [], []
    headers = {
        'cookie': cookie,
        'x-csrf-token': x_csrf_token,
    }
    try:
        response = httpx.get(url, headers=headers, timeout=30).text
        response = json.loads(response)
        for i in response['data']['characters']:
            name = i['key']
            if i['info']:
                level = i['info']['level']
                next_time = int(i['info']['next_time'])
                next_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(next_time))
                h = f'角色：{name}(Lv.{level})\n时间：{next_time}'
                if '行秋' in name or '班尼特' in name:
                    continue
                times = parse(next_time)
                times_list.append(times)
                has_character.append(h)
        max_time = latest_time(times_list)
        return max_time, has_character
    except Exception as e:
        logging.error(f'[zhuque_game_file]:获取角色信息出错了,错误信息{e}', exc_info=True)
        return


def latest_time(times_list):
    today = datetime.date.today()
    past_list = []
    for i in times_list:
        if i.date() <= today:
            past_list.append(i)
    if past_list:
        return max(past_list)
    else:
        tomorrow = today + datetime.timedelta(days=1)
        return datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)


def parse_seconds(delta_second):
    if delta_second >= 3600:
        hours = delta_second // 3600
        remaining_seconds = delta_second % 3600
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        remain_time = f'{int(hours):02d}小时{int(minutes):02d}分钟{int(seconds):02d}秒'
    elif delta_second >= 60:
        minutes = delta_second // 60
        seconds = delta_second % 60
        remain_time = f'{int(minutes):02d}分钟{int(seconds):02d}秒'
    else:
        remain_time = f'{int(delta_second):02d}秒'
    return remain_time


def fire():
    content = f''
    headers = {
        'accept': 'application/json, text/plain, */*',
        'referer': "https://zhuque.in/gaming/genshin/character/list",
        'x-requested-with': 'XMLHttpRequest',
        'content-type': 'application/json',
        'origin': 'https://zhuque.in',
        'cookie': cookie,
        'x-csrf-token': x_csrf_token,
    }
    data = {
        'all': 1
    }
    try:
        response = httpx.post(fire_url, headers=headers, json=data, timeout=30)
        res = response.json()
        if res.get('status') == 200:
            _LOGGER.info(f'[zhuque_game_file]:已拥有角色：')
            times, has_character = zhuque_character()
            for h in has_character:
                content += h + '\n'
                _LOGGER.info(h)
            bonus = res.get('data').get('bonus')
            _LOGGER.info(f'[zhuque_game_file]:释放技能成功,获得了{bonus}灵石')
            title = f'释放技能成功,获得了{bonus}灵石'
            sent_notify(title, content)
            return True
        else:
            _LOGGER.error(f'[zhuque_game_file]:释放技能失败，时间还未到')
            return False
    except Exception as e:
        logging.error(f'[zhuque_game_file]:释放技能出错了,错误信息：{e}', exc_info=True)
        return False


def sent_notify(title, content):
    if message_to_uid:
        for _ in message_to_uid:
            server.notify.send_message_by_tmpl('{{title}}', '{{a}}', {
                'title': title,
                'a': content,
                'pic_url': img_url
            }, to_uid=_, to_channel_name=channel)


def main():
    times, has_character = zhuque_character()
    try:
        now_time = parse(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        if now_time >= times:
            fire()
            return True
        else:
            return False
    except Exception as e:
        logging.error(f'[zhuque_game_file]:释放技能出错了,错误信息：{e}', exc_info=True)
        return False
