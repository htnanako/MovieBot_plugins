import logging
from typing import Dict

from moviebotapi.core.models import MediaType

from mbot.core.plugins import plugin, PluginContext
from mbot.openapi import mbot_api
from . import Config
from .datawrapper import PlaybackData

_LOGGER = logging.getLogger(__name__)


def _get_progress(progress):
    if not progress:
        return
    progress_all_num = 21
    progress_do_text = "■"
    progress_undo_text = "□"
    progress_do_num = round(0.5 + ((progress_all_num * int(progress)) / 100))
    # 处理96%-100%进度时进度条展示，正常计算时，进度大于等于96%就已是满条，需单独处理
    if 95 < int(progress) < 100:
        progress_do_num = progress_all_num - 1

    progress_undo_num = progress_all_num - progress_do_num
    progress_do = progress_do_text * progress_do_num
    progress_undo = progress_undo_text * progress_undo_num
    return progress_do + progress_undo + f' {progress}%'


def _get_backdrop_url(play: PlaybackData):
    if play.backdrop_url:
        return play.backdrop_url
    if not play.provider_ids:
        return
    tmdb_id = play.provider_ids.get('Tmdb')
    meta = mbot_api.tmdb.get(MediaType.TV if play.is_tv else MediaType.Movie, tmdb_id)
    if not meta or not meta.backdrop_path:
        return
    return 'https://www.themoviedb.org/t/p/w533_and_h300_bestv2%s' % meta.backdrop_path


def _get_message_context(play: PlaybackData):
    return {
        'server_name': play.server_name,
        'title': play.title,
        'year': play.release_year,
        'season_number': play.season_number,
        'episode_number': play.episode_number,
        'episode_title': play.episode_title,
        'user': play.user_name,
        'container': play.container,
        'video_stream_title': play.video_stream_title,
        'transcoding_info': play.transcoding_info,
        'current_cpu': play.current_cpu,
        'bitrate': play.bitrate,
        'size': play.size,
        'client': play.client,
        'device_name': play.device_name,
        'pic_url': _get_backdrop_url(play),
        'link_url': '',
        'progress_text': _get_progress(play.progress),
        'genres': play.genres,
        'series_genres': play.series_genres,
        'intro': play.overview,
        'created_at': play.created_at
    }


def _get_uid():
    uid = []
    if Config.uid:
        uid = Config.uid
    return uid


@plugin.on_event(
    bind_event='EmbyPlaybackStart', order=1)
def playback_start(ctx: PluginContext, event_type: str, data: Dict):
    play = PlaybackData(data)
    uid = _get_uid()
    _LOGGER.info(f'{play.user_name} 开始播放 {play.title}')
    if uid:
        for i in uid:
            mbot_api.notify.send_message_by_tmpl(
                Config.default_start_title,
                Config.default_start_body,
                _get_message_context(play),
                to_uid=i,
                to_channel_name=play.to_channel_name
            )
    else:
        mbot_api.notify.send_message_by_tmpl(
            Config.default_start_title,
            Config.default_start_body,
            _get_message_context(play),
            to_channel_name=play.to_channel_name
        )


@plugin.on_event(
    bind_event='EmbyPlaybackStop', order=1)
def playback_stop(ctx: PluginContext, event_type: str, data: Dict):
    play = PlaybackData(data)
    uid = _get_uid()
    _LOGGER.info(f'{play.user_name} 停止播放 {play.title}')
    if uid:
        for i in uid:
            mbot_api.notify.send_message_by_tmpl(
                Config.default_stop_title,
                Config.default_stop_body,
                _get_message_context(play),
                to_uid=i,
                to_channel_name=play.to_channel_name
            )
    else:
        mbot_api.notify.send_message_by_tmpl(
            Config.default_stop_title,
            Config.default_stop_body,
            _get_message_context(play),
            to_channel_name=play.to_channel_name
        )


@plugin.on_event(
    bind_event='EmbyLibraryNew', order=1)
def library_new(ctx: PluginContext, event_type: str, data: Dict):
    play = PlaybackData(data)
    uid = _get_uid()
    if play.type == "Movie":
        _LOGGER.info(f'{play.server_name} 新增电影 {play.title}')
        if uid:
            for i in uid:
                mbot_api.notify.send_message_by_tmpl(
                    Config.default_new_movie_title,
                    Config.default_new_movie_body,
                    _get_message_context(play),
                    to_uid=i,
                    to_channel_name=play.to_channel_name
                )
        else:
            mbot_api.notify.send_message_by_tmpl(
                Config.default_new_movie_title,
                Config.default_new_movie_body,
                _get_message_context(play),
                to_channel_name=play.to_channel_name
            )
    else:
        _LOGGER.info(f'{play.server_name} 新增剧集 {play.title}')
        if uid:
            for i in uid:
                mbot_api.notify.send_message_by_tmpl(
                    Config.default_new_series_title,
                    Config.default_new_series_body,
                    _get_message_context(play),
                    to_uid=i,
                    to_channel_name=play.to_channel_name
                )
        else:
            mbot_api.notify.send_message_by_tmpl(
                Config.default_new_series_title,
                Config.default_new_series_body,
                _get_message_context(play),
                to_channel_name=play.to_channel_name
            )
