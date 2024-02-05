import os
import httpx
import datetime
import logging
from tenacity import retry, wait_random_exponential, stop_after_attempt

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
            "Host": "oaidalleapiprodscus.blob.core.windows.net",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        img_content = httpx.get(url=url,
                                headers=headers,
                                params=params,
                                follow_redirects=True,
                                timeout=180).content
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
