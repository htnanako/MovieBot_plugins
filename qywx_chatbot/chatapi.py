import httpx
import re
from tenacity import wait_fixed, stop_after_attempt, retry
import logging

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


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
async def chat(base_url, proxy, api_key, model, query, session_id=None, session_limit=None):
    query = query.strip()
    params = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ],
        "max_tokens": 2048,
    }
    if 'aiproxy' in base_url:
        if session_limit != '' and session_limit != '0':
            params["session_id"] = session_id
            params["session_limit"] = session_limit
    try:
        r = httpx.post(url=f"{base_url}/v1/chat/completions",
                       headers={
                           "Content-Type": "application/json",
                           "Authorization": f"Bearer {api_key}"
                       },
                       json=params,
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
            return f'{ERROR_CODE[r.status_code] if r.status_code in ERROR_CODE else f"[ERROR: {r.status_code}] 未知错误，请检查日志 | Unknown error, please check the log"}'
    except Exception as e:
        logger.error(f"chat error: {e}")
        return f'思考失败，{e}'
