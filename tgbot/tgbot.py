import asyncio
from urllib.parse import unquote
from cacheout import Cache
import logging

from .utils import *

from telegram import InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler, ContextTypes

from moviebotapi.core.models import MediaType
from mbot.openapi import mbot_api

server = mbot_api
_LOGGER = logging.getLogger(__name__)


status_emoji = ['🛎️', '✅', '🔁', '📥']
search_cache = Cache(maxsize=1000)
close_keyboard = [
    [
        InlineKeyboardButton('🔚关闭', callback_data=f'delete'),
    ]
]
close_keyboard = InlineKeyboardMarkup(close_keyboard)
mbot_icon = 'https://nanako-1253183981.cos.ap-guangzhou.myqcloud.com/icon/docker/mbot.png'


async def search_by_douban(keyword: str):
    search_cache.clear()
    del_photo()
    douban_info = server.douban.search(keyword)
    if not douban_info:
        return None
    if len(douban_info) >= 10:
        douban_info = douban_info[:10]
    reply_caption = []
    douban_id_list = []
    poster_url_list = []
    count = 1
    for item in douban_info:
        item_id = str(item.id)
        item_cn_name = item.cn_name
        item_rating = item.rating
        item_poster_url = item.poster_url
        item_url = item.url
        item_status = item.status
        item_rating = f'⭐️{item_rating}' if str(item_rating) != 'nan' else '⭐️0.0'
        item_status = status_emoji[item_status.value] if item_status is not None else status_emoji[3]
        item_poster_url = unquote(item_poster_url.replace('/api/common/get_image?url=', ''))
        set_count = "%02d" % count
        caption = f'`{set_count}`.`{item_status}`|`{item_rating}`|[{item_cn_name}]({item_url})\n'
        reply_caption.append(caption)
        douban_id_list.append(item_id)
        poster_url_list.append(f'{item_poster_url}')
        count += 1
    call = '\n📥未订阅 | ✅️已完成' + '\n🛎️订阅中 | 🔁洗版中' + '\n\n⬇⬇⬇请点对应的序号⬇⬇⬇'
    reply_caption = ''.join(reply_caption) + call
    temp_keyboard = []
    for i in range(len(douban_id_list)):
        temp_keyboard.append(InlineKeyboardButton(f'{i + 1}', callback_data=str(douban_id_list[i])))
    step = 5
    keyboard = [temp_keyboard[i:i + step] for i in range(0, len(temp_keyboard), step)]
    keyboard.append([InlineKeyboardButton('🔚关闭', callback_data=f'delete')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    poster_url = poster_url_list[0]
    x = await get_meta_detail(int(douban_id_list[0]))
    if x:
        background_url = x.background_url
        if background_url:
            poster_url = background_url
    search_cache.set('reply_caption', reply_caption)
    search_cache.set('reply_markup', reply_markup)
    save_photo(poster_url)
    return reply_caption, reply_markup


async def get_meta_detail(douban_id: int):
    try:
        meta = server.meta.get_media_by_douban(MediaType.Movie, douban_id)
    except:
        meta = server.meta.get_media_by_douban(MediaType.TV, douban_id)
    return meta


async def get_douban_detail(douban_id: int):
    douban_detail = server.douban.get(douban_id)
    if not douban_detail:
        return None
    douban_cn_name = douban_detail.cn_name
    douban_rating = douban_detail.rating
    douban_intro = douban_detail.intro
    douban_premiere_date = douban_detail.premiere_date
    douban_cover_image = douban_detail.cover_image
    douban_actor = douban_detail.actor
    douban_media_type = str(douban_detail.media_type)
    douban_season_index = douban_detail.season_index
    douban_genres = douban_detail.genres
    douban_episode_count = douban_detail.episode_count

    douban_rating = f' | ⭐{douban_rating}'

    x = await get_meta_detail(douban_id)
    if x:
        background_url = x.background_url
        if background_url:
            douban_cover_image = background_url

    save_photo(douban_cover_image)

    if len(douban_actor) > 3:
        douban_actor = douban_actor[:4]
    if not douban_actor:
        douban_actor = ''
    else:
        douban_actor = '演员：#' + ' #'.join(i.name for i in douban_actor) + '\n'

    if not douban_genres:
        douban_genres = ''
    else:
        douban_genres = '类型：#' + ' #'.join(i for i in douban_genres) + '\n'
    if len(douban_intro) >= 200:
        douban_intro = f'简介：{douban_intro[0:200]}....'

    if douban_media_type == 'MediaType.Movie':
        douban_media_meta = (f'🎬*{douban_cn_name}*{douban_rating}\n\n'
                             f'上映时间：{douban_premiere_date}\n'
                             f'{douban_actor}{douban_genres}{douban_intro}')
    else:
        douban_media_meta = (f'📺*{douban_cn_name}*{douban_rating}\n\n'
                             f'第{douban_season_index}季 共{douban_episode_count}集\n'
                             f'上映时间：{douban_premiere_date}\n'
                             f'{douban_actor}{douban_genres}{douban_intro}')
    keyboard_un_sub = [
        [
            InlineKeyboardButton('🔚关闭', callback_data=f'delete-{douban_id}-'),
            InlineKeyboardButton('🔙返回', callback_data=f'back-{douban_id}-'),
        ],
        [
            InlineKeyboardButton('🛎️订阅', callback_data=f'sub-{douban_id}-{douban_cn_name}'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard_un_sub)
    keyboard_sub = [
        [
            InlineKeyboardButton('🔚关闭', callback_data=f'delete-{douban_id}-'),
        ],
        [
            InlineKeyboardButton('🔙返回', callback_data=f'back-{douban_id}-'),
        ]
    ]
    reply_markup_sub = InlineKeyboardMarkup(keyboard_sub)
    search_cache.set('reply_markup_sub', reply_markup_sub)
    return douban_media_meta, reply_markup


class TGBOT:
    def __init__(self):
        self.bot_token = None
        self.proxy = None
        self.base_url = None
        self.allow_id = None

    def set_config(self, bot_token, proxy, base_url, allow_id):
        self.bot_token = bot_token
        self.proxy = proxy
        self.base_url = base_url
        self.allow_id = allow_id

    def check_chat_it(self, chat_id):
        if not self.allow_id:
            return True
        elif chat_id not in self.allow_id:
            return False
        else:
            return True

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            chat_id = str(update.message.chat_id)
            username = update.message.chat.username
        except Exception as e:
            _LOGGER.info(f'不可用于频道，请与TGBot私聊或者在群组内使用')
            return
        if not self.allow_id:
            await update.message.reply_text(f"chat_id：{chat_id}\nMovieBot插件未设置chat_id,所有用户都可以访问！！")
            _LOGGER.info(f"当前用户chat_id：{chat_id} ，Movie—Bot插件未设置chat_id")
        if not self.check_chat_it(chat_id):
            await update.message.reply_text(f"chat_id: {chat_id}\nUsername: {username}\n你未经授权！不可使用此机器人")
            _LOGGER.info(f"chat_id: {chat_id}, username: {username}, 未经授权已拦截。")
            return
        content = update.message.text
        await update.message.reply_text(f'正在搜索: {content}')
        _LOGGER.info(f'用户：{username} , 搜索：{content}')
        _douban = await search_by_douban(content)
        await update.message.reply_photo(
            reply_markup=_douban[1],
            photo=get_photo(),
            caption=_douban[0],
            parse_mode='Markdown',
        )

    @staticmethod
    async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        douban_id = query.data
        _douban = await get_douban_detail(int(douban_id))
        await query.edit_message_media(
            reply_markup=_douban[1],
            media=InputMediaPhoto(
                media=get_photo(),
                caption=_douban[0],
                parse_mode='Markdown',
            )
        )
        await query.answer()

    @staticmethod
    async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        douban_id = query.data.split('-')[1]
        if not search_cache.get('reply_caption') or douban_id not in search_cache.get('reply_caption'):
            await query.edit_message_media(
                reply_markup=close_keyboard,
                media=InputMediaPhoto(
                    media=mbot_icon,
                    caption='请重新搜索',
                    parse_mode='Markdown',
                )
            )
            await query.answer()
            return
        reply_caption = search_cache.get('reply_caption')
        reply_markup = search_cache.get('reply_markup')
        await query.edit_message_media(
            reply_markup=reply_markup,
            media=InputMediaPhoto(
                media=get_photo(),
                caption=reply_caption,
                parse_mode='Markdown',
            )
        )
        await query.answer()

    @staticmethod
    async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        search_cache.clear()
        await query.delete_message()
        await query.answer()

    @staticmethod
    async def sub_by_douban(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        douban_id = query.data.split('-')[1]
        douban_cn_name = query.data.split('-')[2]
        if not search_cache.get('reply_markup_sub'):
            await query.edit_message_caption('请重新搜索')
            await query.answer()
            return
        reply_markup_sub = search_cache.get('reply_markup_sub')
        server.subscribe.sub_by_douban(int(douban_id))
        await query.edit_message_caption(f"{douban_cn_name} 已提交订阅 ✔", reply_markup=reply_markup_sub)
        await query.answer()

    def start_bot(self):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            app = Application.builder().token(self.bot_token).base_url(self.base_url).proxy(self.proxy).get_updates_proxy(self.proxy).build()
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))
            app.add_handler(CallbackQueryHandler(self.button, pattern="^\d"))
            app.add_handler(CallbackQueryHandler(self.back, pattern="^back"))
            app.add_handler(CallbackQueryHandler(self.delete, pattern="^delete"))
            app.add_handler(CallbackQueryHandler(self.sub_by_douban, pattern="^sub"))
            app.run_polling(stop_signals=None, close_loop=False)
        except Exception as e:
            _LOGGER.error(f"Telegram机器人启动失败：{e}", exc_info=True)
            return
        finally:
            loop.close()
            pass
