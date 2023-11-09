import httpx
import re
import logging
from tenacity import retry, wait_random_exponential, stop_after_attempt

from .utils import save_img

logger = logging.getLogger(__name__)

ERROR_CODE = {
    400: '[ERROR: 400] 提示触发 Azure OpenAI 的内容管理策略，响应被过滤 | The response was filtered due to the prompt triggering Azure OpenAI’s content management policy',
    401: '[ERROR: 401] 提供错误的API密钥 | Incorrect API key provided',
    403: '[ERROR: 403] 服务器拒绝访问，请稍后再试 | Server refused to access, please try again later',
    429: '[ERROR: 429] 额度不足 | Quota exhausted',
    502: '[ERROR: 502] 错误的网关 |  Bad Gateway',
    503: '[ERROR: 503] 服务器繁忙，请稍后再试 | Server is busy, please try again later',
    504: '[ERROR: 504] 网关超时 | Gateway Time-out',
    500: '[ERROR: 500] 服务器繁忙，请稍后再试 | Internal Server Error',
}


def unknown_error_code(error_code):
    return f'[ERROR: {error_code}] 未知错误，请检查日志 | Unknown error, please check the log'


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
async def chat(SERVICE, base_url, proxy, api_key, model, query, session_id=None, session_limit=None):
    query = query.strip()
    json = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ],
        "max_tokens": 2048,
    }
    if 'aiproxy' in SERVICE:
        if session_limit != '' and session_limit != '0':
            json["session_id"] = session_id
            json["session_limit"] = session_limit
    try:
        r = httpx.post(url=f"{base_url}/v1/chat/completions",
                       headers={
                           "Content-Type": "application/json",
                           "Authorization": f"Bearer {api_key}"
                       },
                       json=json,
                       proxies=proxy,
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
            return answer
        else:
            logger.error(f"「ChatBot」Chat Error: {j}")
            return f'{ERROR_CODE[r.status_code] if r.status_code in ERROR_CODE else unknown_error_code(r.status_code)}'
    except Exception as e:
        logger.error(f"「ChatBot」Chat Error: {e}")
        return f'思考失败，{e}'


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
async def draw(base_url, proxy, api_key, prompt, draw_info):
    prompt = prompt.strip()
    size = draw_info.split('_')[0]
    quality = draw_info.split('_')[1]
    json = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality
    }
    try:
        r = httpx.post(url=f"{base_url}/v1/images/generations",
                       headers={
                           "Content-Type": "application/json",
                           "Authorization": f"Bearer {api_key}"
                       },
                       json=json,
                       proxies=proxy,
                       timeout=300)
        j = r.json()
        if r.status_code == 200:
            img_url = j.get('data')[0].get('url')
            img_prompt = j.get('data')[0].get('revised_prompt')
            await save_img(img_url, img_prompt)
            logger.info(f'「ChatBot」Draw Image Complete: {img_prompt}')
            result = {
                "success": True,
                "img_url": img_url,
                "img_prompt": img_prompt
            }
            return result
        else:
            logger.error(f"「ChatBot」Draw Error: {j}")
            result = {
                "success": False,
                "error": j.get["error"] if j.get["error"] else {ERROR_CODE[r.status_code] if r.status_code in ERROR_CODE else unknown_error_code(r.status_code)}
            }
            return result
    except Exception as e:
        logger.error(f"「ChatBot」Draw Error: {e}")
        result = {
            "success": False,
            "error": f'绘图失败，{e}'
        }
        return result
