import logging
import urllib
from typing import Any, Dict, List

from mbot.core import PluginMeta
from mbot.core.plugins import plugin
from mbot.openapi import media_server_manager

_LOGGER = logging.getLogger(__name__)


class _Config:
    uid: List[int] = None
    mbot_server_url: str = None
    default_start_title: str = '{{user}}开始播放 {{title}}{%if year%}({{year}}){%endif%}'
    default_start_body = '{%if progress_text%}{{progress_text}}\n{%endif%}{{container}} · {{video_stream_title}}\n⤷{{transcoding_info}} {{bitrate}}Mbps{%if current_cpu%}\n⤷CPU消耗：{{current_cpu}}%{%endif%}\n来自：{{server_name}}\n大小：{{size}}\n设备：{{client}} · {{device_name}}{%if genres%}\n风格：{{genres}}{%endif%}{%if intro%}\n简介：{{intro}}{%endif%}'
    default_stop_title = '{{user}}停止播放 {{title}}{%if year%}({{year}}){%endif%}'
    default_stop_body = '{%if progress_text%}{{progress_text}}\n{%endif%}{{container}} · {{video_stream_title}}\n⤷{{transcoding_info}} {{bitrate}}Mbps{%if current_cpu%}\n⤷CPU消耗：{{current_cpu}}%{%endif%}\n来自：{{server_name}}\n大小：{{size}}\n设备：{{client}} · {{device_name}}{%if genres%}\n风格：{{genres}}{%endif%}{%if intro%}\n简介：{{intro}}{%endif%}'
    default_new_movie_title = '🍟 新片入库： {{title}} {%if year%}({{year}}){%endif%}'
    default_new_movie_body = '🍟 {{server_name}}\n入库时间: {{created_at}}\n{%if genres%}\n风格：{{genres}}{%endif%}\n大小：{{size}}{%if intro%}\n简介：{{intro}}{%endif%}'
    default_new_series_title = '📺 新片入库： {{title}}'
    default_new_series_body = '📺 {{server_name}}\n入库时间: {{created_at}}\n{%if episode_title%}\n单集标题：{{episode_title}}{%endif%}{%if series_genres%}\n风格：{{series_genres}}{%endif%}\n大小：{{size}}{%if intro%}\n简介：{{intro}}{%endif%}'


    def set_config(self, data: Dict):
        self.uid = data.get('uid')
        self.mbot_server_url = data.get('mbot_server_url')
        if self.mbot_server_url:
            self.mbot_server_url.rstrip('/')
        if data.get('default_start_title'):
            self.default_start_title = data.get('default_start_title')
        if data.get('default_start_body'):
            self.default_start_body = data.get('default_start_body')
        if data.get('default_stop_title'):
            self.default_stop_title = data.get('default_stop_title')
        if data.get('default_stop_body'):
            self.default_stop_body = data.get('default_stop_body')
        if data.get('default_new_movie_title'):
            self.default_new_movie_title = data.get('default_new_movie_title')
        if data.get('default_new_movie_body'):
            self.default_new_movie_body = data.get('default_new_movie_body')
        if data.get('default_new_series_title'):
            self.default_new_episode_title = data.get('default_new_series_title')
        if data.get('default_new_series_body'):
            self.default_new_episode_body = data.get('default_new_series_body')


Config = _Config()


def _check_sys_webhook(sys_webhooks: List, url: str):
    exists = False
    if sys_webhooks:
        for item in sys_webhooks:
            if str(item.get('Url')).startswith(url):
                exists = True
                break
    return exists


def auto_add_webhook():
    if Config.mbot_server_url:
        ak = mbot_api.auth.get_default_ak()
        for server in media_server_manager.all:
            if server.server_type != 'emby':
                continue
            mbot_webhook = f'{Config.mbot_server_url}/api/event/emby_hook?access_key={ak}&server_name={urllib.parse.quote_plus(server.server_config.get("name"))}'
            if not _check_sys_webhook(server.get_system_webhooks(), f'{Config.mbot_server_url}/api/event/emby_hook'):
                _LOGGER.info(f'自动向{server.server_config.get("name")}注册Webhook')
                server.add_system_webhooks(mbot_webhook, ["Playback", "User", "library.new"])
        _LOGGER.info(f'Emby播放通知插件加载成功')
    else:
        _LOGGER.error(f'需要在Emby播放插件中配置MBot内网访问地址后才可以使用')


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    Config.set_config(config)
    auto_add_webhook()


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    Config.set_config(config)
    auto_add_webhook()


from .event import *
