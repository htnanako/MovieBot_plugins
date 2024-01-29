import logging
from typing import Dict, Any
import threading
from mbot.core.plugins import plugin
from mbot.core.plugins import PluginContext, PluginMeta
from .tgbot import TGBOT

_LOGGER = logging.getLogger(__name__)
tgbot = TGBOT()


@plugin.after_setup
def setup_config(plugin: PluginMeta, config: Dict):
    bot_token = config.get('TGbotTOKEN')
    allow_id = config.get('chat_id')
    proxy = config.get('proxy')
    base_url = config.get('base_url', 'https://api.telegram.org/bot')
    if not bot_token:
        _LOGGER.info(f'TG Bot缺少配置，停止启动，请完成插件配置')
        return
    if allow_id:
        allow_id = allow_id.split(',')
        for i in range(len(allow_id)):
            allow_id[i] = allow_id[i].strip()
    tgbot.set_config(bot_token, proxy, base_url, allow_id)
    _LOGGER.info(
        f"Telegram机器人加载成功，Base_url：{base_url},TGbotTOKEN:{bot_token},chat_id:{allow_id},Proxy：{proxy}")
    thread = threading.Thread(target=tgbot.start_bot)
    thread.start()


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    bot_token = config.get('TGbotTOKEN')
    allow_id = config.get('chat_id')
    proxy = config.get('proxy')
    base_url = config.get('base_url', 'https://api.telegram.org/bot')
    if not bot_token:
        _LOGGER.info(f'TG Bot缺少配置，停止启动，请完成插件配置')
        return
    if allow_id:
        allow_id = allow_id.split(',')
        for i in range(len(allow_id)):
            allow_id[i] = allow_id[i].strip()
    tgbot.set_config(bot_token, proxy, base_url, allow_id)
    _LOGGER.info(
        f"Telegram机器人加载成功，Base_url：{base_url},TGbotTOKEN:{bot_token},chat_id:{allow_id},Proxy：{proxy}")

