import httpx
import re
from tenacity import wait_fixed, stop_after_attempt, retry
import logging

logger = logging.getLogger(__name__)


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
                           ]
                       },
                       proxies=proxy,
                       timeout=180)
        r.raise_for_status()
        j = r.json()
        answer = j.get('choices')[0].get('message').get('content')
        logger.info(f'Chat answer: {answer}')
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        def replace_link(match):
            title = match.group(1)
            url = match.group(2)
            return f'<a href="{url}">{title}</a>'

        answer = re.sub(pattern, replace_link, answer)
        return answer
    except Exception as e:
        logger.error(f"chat error: {e}")
        return '思考失败，请查看日志。'
