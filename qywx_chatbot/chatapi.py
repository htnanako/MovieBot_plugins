import httpx
import re
from tenacity import wait_fixed, stop_after_attempt, retry
import logging

logger = logging.getLogger(__name__)

ERROR_CODE = {
    401: '[ERROR: 401] 提供错误的API密钥 | Incorrect API key provided',
    403: '[ERROR: 403] 服务器拒绝访问，请稍后再试 | Server refused to access, please try again later',
    429: '[ERROR: 429] 额度不足 | Quota exhausted',
    502: '[ERROR: 502] 错误的网关 |  Bad Gateway',
    503: '[ERROR: 503] 服务器繁忙，请稍后再试 | Server is busy, please try again later',
    504: '[ERROR: 504] 网关超时 | Gateway Time-out',
    500: '[ERROR: 500] 服务器繁忙，请稍后再试 | Internal Server Error',
}


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
async def chat(base_url, proxy, api_key, model, query):
    try:
        r = httpx.post(f'{base_url}/v1/chat/completions',
                       headers={
                           "Content-Type": "application/json",
                           "Authorization": f"Bearer {api_key}"
                       },
                       json={
                           "model": model,
                           "messages": [
                               {
                                   "role": "user",
                                   "content": query
                               }
                           ],
                           "max_tokens": 2048,
                       },
                       proxies=proxy,
                       timeout=180)
        j = r.json()
        if r.status_code == 200:
            answer = j.get('choices')[0].get('message').get('content')
            logger.info(f'Chat answer: {answer}')
            pattern = r'\[([^\]]+)\]\(([^)]+)\)'

            def replace_link(match):
                title = match.group(1)
                url = match.group(2)
                return f'<a href="{url}">{title}</a>'

            answer = re.sub(pattern, replace_link, answer)
            return answer
        else:
            logger.error(f"chat error: {j}")
            return f'{ERROR_CODE[r.status_code]}'
    except Exception as e:
        logger.error(f"chat error: {e}")
        return f'思考失败，请查看日志。'
