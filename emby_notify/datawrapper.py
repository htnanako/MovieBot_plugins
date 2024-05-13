import time

from typing import Dict

from mbot.common.numberutils import NumberUtils


class PlaybackData:
    def __init__(self, data: Dict):
        self.data = data
        if self.internet_url:
            self.server_url = self.internet_url.rstrip('/')
        else:
            self.server_url = None

    def _get_if_none_than_obj(self, key):
        val = self.data.get(key)
        if not val:
            return {}
        return val

    def _get_poster_url(self, item_id):
        if not item_id or not self.server_url:
            return
        return f'{self.server_url}/emby/Items/{item_id}/Images/Primary?maxHeight=600&maxWidth=400'

    def _get_backdrop_url(self, item_id):
        if not item_id or not self.server_url:
            return
        return f'{self.server_url}/emby/Items/{item_id}/Images/Backdrop/0?maxWidth=800'

    @property
    def _session(self):
        return self._get_if_none_than_obj('Session')

    @property
    def _user(self):
        return self._get_if_none_than_obj('User')

    @property
    def _meta(self):
        return self._get_if_none_than_obj('Meta')

    @property
    def _server(self):
        return self._get_if_none_than_obj('Server')

    @property
    def _series(self):
        return self._get_if_none_than_obj('Series')

    @property
    def server_name(self):
        return self._server.get('Name')

    @property
    def _item(self):
        return self._get_if_none_than_obj('Item')

    @property
    def user_id(self):
        return self._user.get('Id')

    @property
    def user_name(self):
        return self._user.get('Name')

    @property
    def client(self):
        return self._session.get('Client')

    @property
    def device_name(self):
        return self._session.get('DeviceName')

    @property
    def type(self):
        return self._item.get('Type')

    @property
    def title(self):
        if self._item.get('Type') == 'Movie':
            return self._item.get('Name')
        else:
            return f"{self._item.get('SeriesName')} S{self.season_number}E{self.episode_number}"

    @property
    def episode_title(self):
        if self._item.get('Type') == 'Episode':
            return self._item.get('Name')
        else:
            return

    @property
    def release_year(self):
        return self._item.get('ProductionYear')

    @property
    def episode_number(self):
        if self._item.get('IndexNumber'):
            return str(self._item.get('IndexNumber')).zfill(2)
        else:
            return

    @property
    def season_number(self):
        if self._item.get('ParentIndexNumber'):
            return str(self._item.get('ParentIndexNumber')).zfill(2)
        else:
            return

    @property
    def is_tv(self):
        return 'Series' in self.data

    @property
    def provider_ids(self):
        if 'Series' in self.data:
            return self.data.get('Series').get('ProviderIds')
        else:
            if self._item.get('ProviderIds'):
                return self._item.get('ProviderIds')
            if self._meta.get('ProviderIds'):
                return self._meta.get('ProviderIds')

    @property
    def progress(self):
        item = self.data.get('Item')
        if not item:
            return 0
        inf = self.data.get('PlaybackInfo')
        if not inf:
            return 0
        cur = inf.get('PositionTicks')
        if not cur:
            cur = 1
        total = item.get('RunTimeTicks')
        if not total:
            total = 1
        return round(cur / total * 100, 2)

    @property
    def poster_url(self):
        if self._item.get('Type') == 'Movie':
            return self._get_poster_url(self._item.get('Id'))
        else:
            return self._get_poster_url(self._item.get('ParentLogoItemId'))

    @property
    def backdrop_url(self):
        if self._item.get('Type') == 'Movie':
            return self._get_backdrop_url(self._item.get('Id'))
        else:
            return self._get_backdrop_url(self._item.get('ParentBackdropItemId'))

    @property
    def bitrate(self):
        bitrate = self._item.get('Bitrate')
        if not bitrate:
            return 0
        return round(bitrate / 1000 / 1000)

    @property
    def transcoding_info(self):
        if 'TranscodingInfo' in self.data:
            info = self.data.get('TranscodingInfo')
            return f'{str(info.get("SubProtocol")).upper()}({round(info.get("Bitrate") / 1000 / 1000)}Mbps {info.get("Framerate")}fps)'
        else:
            return '直接播放'

    @property
    def current_cpu(self):
        if 'TranscodingInfo' in self.data:
            info = self.data.get('TranscodingInfo')
            if info.get('CurrentCpuUsage'):
                return round(info.get('CurrentCpuUsage') * 100, 2)
            else:
                return
        else:
            return

    @property
    def container(self):
        return str(self._item.get('Container')).upper()

    @property
    def video_stream_title(self):
        ms = self._meta.get('MediaStreams')
        if not ms:
            return
        return ms[0].get('DisplayTitle')

    @property
    def size(self):
        size = self._item.get('Size')
        if not size:
            return 0
        return NumberUtils.size_format_from_byte(size)

    @property
    def genres(self):
        genres = self._item.get('Genres')
        if not genres:
            return
        return ' / '.join(genres)

    @property
    def series_genres(self):
        genres = self._item.get('Genres')
        if not genres:
            return
        return ' / '.join(genres)

    @property
    def overview(self):
        if self._item.get('Overview'):
            return self._item.get('Overview')
        if self._meta.get('Overview'):
            return self._meta.get('Overview')
        return

    @property
    def created_at(self):
        return (time.strftime("%Y-%m-%d %a %H:%M:%S", time.localtime())
                .replace("Mon", "周一")
                .replace("Tue", "周二")
                .replace("Wed", "周三")
                .replace("Thu", "周四")
                .replace("Fri", "周五")
                .replace("Sat", "周六")
                .replace("Sun", "周日")
                )

    @property
    def internet_url(self):
        return self.data.get('InternetUrl')

    @property
    def to_channel_name(self):
        return self.data.get('ToChannelName')
