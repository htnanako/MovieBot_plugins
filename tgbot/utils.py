import httpx
import os
from tenacity import retry, wait_random_exponential, stop_after_attempt


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def save_photo(poster_url: str):
    r = httpx.get(poster_url)
    r.raise_for_status()
    with open('poster.jpg', 'wb') as f:
        f.write(r.content)


def get_photo():
    if not os.path.exists('poster.jpg'):
        return 'https://p.xmoviebot.com/plugins/tg_bot_logo.jpg'
    with open('poster.jpg', 'rb') as f:
        poster = f.read()
    return poster


def del_photo():
    try:
        os.remove('poster.jpg')
    except FileNotFoundError:
        pass
