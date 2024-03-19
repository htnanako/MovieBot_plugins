import random
import logging

from .utils import *

logger = logging.getLogger(__name__)


class NotifyApiMain:
    def __init__(self):
        self.channels = Config().get_config()

    def send_notify(self, message: dict):
        title = message.get("title")
        content = message.get("content")
        id = message.get("id")
        img = message.get("pic_url")
        link_url = message.get("link_url", None)
        channel, users, pic_url = None, None, None
        for item in self.channels:
            if item["id"] == id:
                channel = item["channels"]
                users = item["users"]
                if img:
                    pic_url = img
                else:
                    pic_url = item.get("default_img", None)
                break
        if not channel:
            logger.error("「Notify API」 Channel not found")
            return None
        if pic_url:
            pic_url += f"#{str(random.randint(1, 10000))}"
        for _ in users:
            server.notify.send_message_by_tmpl('{{title}}', '{{a}}', {
                'title': title,
                'a': content,
                'pic_url': pic_url,
                'link_url': link_url
            }, to_channel_name=channel, to_uid=_)
        return True
