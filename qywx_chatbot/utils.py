import os
import httpx
import datetime
import logging
import json

from collections import deque
from tenacity import retry, wait_random_exponential, stop_after_attempt

from . import config

logger = logging.getLogger(__name__)

# 取当前绝对路径
save_path = os.path.join('/data', 'img_output')
if not os.path.exists(save_path):
    os.mkdir(save_path)
img_info_file = os.path.join(save_path, 'img_with_prompt_info.txt')


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
async def save_img(img_url, img_prompt):
    try:
        url = img_url.split('?')[0]
        params_source = img_url.split('?')[1]
        params = {}
        for item in params_source.split('&'):
            params[item.split('=')[0]] = item.split('=')[1]
        headers = {
            "Host": url.split('/')[2],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "DNT": "1",
            "Pragma": "no-cache",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }

        def get_image_content():
            r = httpx.get(url=url,
                          headers=headers,
                          params=params,
                          follow_redirects=True,
                          timeout=180)
            return r

        img_content = ''
        for i in range(3):
            r = get_image_content()
            if "AuthenticationFailed" in r.text:
                print(f"「ChatBot」Get Image Error: {r.text}")
                continue
            img_content = r.content
            break
        if not img_content:
            logger.error(f"「ChatBot」图片下载失败, 将使用源链接，会到期失效。")
            return None

        img_basename = img_url.split('img-')[1].split('.png')[0]
        img_name = f'{img_basename}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.png'
        img_path = os.path.join(save_path, img_name)
        with open(img_path, 'wb') as f:
            f.write(img_content)
        with open(img_info_file, 'a+') as f:
            img_info = f"{img_name}: {img_prompt}"
            f.write(img_info + '\n')
        return img_name
    except Exception as e:
        logger.error(f"「ChatBot」Save Image Error: {e}", exc_info=True)
        return False


class UserRecords:
    def __init__(self, filename='/data/conf/context.json'):
        self.records = {}
        self.max_records = int(config.context_num)
        self.filename = filename
        if not os.path.exists(self.filename):
            open(self.filename, 'w').close()
        self.load_records()

    def add_record(self, username, record):
        if username not in self.records:
            self.records[username] = deque(maxlen=self.max_records)
        self.records[username].append(record)
        self.save_records()

    def get_records(self, username):
        return list(self.records.get(username, []))

    def clear_records(self, username):
        if username in self.records:
            del self.records[username]
            self.save_records()

    def save_records(self):
        records_to_save = {user: list(records) for user, records in self.records.items()}
        with open(self.filename, 'w') as file:
            file.write(json.dumps(records_to_save, ensure_ascii=False, indent=4))

    def load_records(self):
        try:
            with open(self.filename, 'r') as file:
                file_content = file.read().strip()
                if file_content:
                    records_from_file = json.loads(file_content)
                    self.records = {user: deque(records, maxlen=self.max_records) for user, records in records_from_file.items()}
        except FileNotFoundError:
            pass
