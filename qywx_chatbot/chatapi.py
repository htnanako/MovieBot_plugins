import httpx
import re
import logging
import time
import json

from tenacity import retry, wait_random_exponential, stop_after_attempt

from . import config
from .utils import save_img, UserRecords

logger = logging.getLogger(__name__)

ERROR_CODE = {
    400: '[ERROR: 400] 后端服务出错，请查看日志。 | Backend service error, please check the log',
    401: '[ERROR: 401] 提供错误的API密钥 | Incorrect API key provided',
    403: '[ERROR: 403] 服务器拒绝访问，请稍后再试 | Server refused to access, please try again later',
    429: '[ERROR: 429] 额度不足 | Quota exhausted',
    502: '[ERROR: 502] 错误的网关 |  Bad Gateway',
    503: '[ERROR: 503] 服务器繁忙，请稍后再试 | Server is busy, please try again later',
    504: '[ERROR: 504] 网关超时 | Gateway Time-out',
    500: '[ERROR: 500] 服务器内部错误，请稍后再试 | Internal Server Error',
}


def unknown_error_code(error_code):
    return f'[ERROR: {error_code}] 未知错误，请检查日志 | Unknown error, please check the log'


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
async def chat(query, username):
    query = query.strip()
    payload = {
        "model": config.model,
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ],
        "max_tokens": 2000,
    }
    start = 0
    if config.custom_prompt:
        payload["messages"].insert(0, {
            "role": "system",
            "content": config.custom_prompt.format(date=time.strftime("%Y-%m-%d", time.localtime()))
        })
        start = 1
    if config.context_num:
        for index, record in enumerate(UserRecords().get_records(username=username)):
            payload["messages"].insert(index + start, record)
    try:
        r = httpx.post(url=f"{config.base_url}/v1/chat/completions",
                       headers={
                           "Content-Type": "application/json",
                           "Authorization": f"Bearer {config.api_key}"
                       },
                       json=payload,
                       proxies=config.proxies,
                       timeout=180)
        j = r.json()
        if r.status_code == 200:
            answer = j.get('choices')[0].get('message').get('content')
            logger.info(f'「ChatBot」:Chat answer: {answer}')
            pattern = r'\[([^\]]+)\]\(([^)]+)\)'

            def replace_link(match):
                title = match.group(1)
                url = match.group(2)
                return f'<a href="{url}">{title}</a>'

            answer = re.sub(pattern, replace_link, answer)
            if config.context_num:
                assistant_content = {
                    "role": "assistant",
                    "content": answer
                }
                user_content = {
                    "role": "user",
                    "content": query
                }
                UserRecords().add_record(username=username, record=user_content)
                UserRecords().add_record(username=username, record=assistant_content)
            return answer
        else:
            logger.error(f"「ChatBot」Chat Error: {j}", exc_info=True)
            return f'{ERROR_CODE[r.status_code] if r.status_code in ERROR_CODE else unknown_error_code(r.status_code)}'
    except Exception as e:
        logger.error(f"「ChatBot」Chat Error: {e}", exc_info=True)
        return f'思考失败，{e}'


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
async def draw(prompt, draw_info):
    prompt = prompt.strip()
    size = draw_info.split('_')[0]
    quality = draw_info.split('_')[1]
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality
    }
    try:
        r = httpx.post(url=f"{config.base_url}/v1/images/generations",
                       headers={
                           "Content-Type": "application/json",
                           "Authorization": f"Bearer {config.api_key}"
                       },
                       json=payload,
                       proxies=config.proxies,
                       timeout=300)
        j = r.json()
        if r.status_code == 200:
            img_url = j.get('data')[0].get('url')
            img_prompt = j.get('data')[0].get('revised_prompt')
            img_name = await save_img(img_url, img_prompt)
            logger.info(f'「ChatBot」Draw Image Complete: {img_prompt}')
            result = {
                "success": True,
                "img_url": img_url,
                "img_prompt": img_prompt,
                "img_name": img_name
            }
            return result
        else:
            logger.error(f"「ChatBot」Draw Error: {j}", exc_info=True)
            result = {
                "success": False,
                "error": j.get("error") if j.get("error") else {ERROR_CODE[r.status_code] if r.status_code in ERROR_CODE else unknown_error_code(r.status_code)}
            }
            return result
    except Exception as e:
        logger.error(f"「ChatBot」Draw Error: {e}", exc_info=True)
        result = {
            "success": False,
            "error": f'绘图失败，{e}'
        }
        return result
