import time

from typing import Dict, Any
from mbot.core.plugins import PluginContext, plugin, PluginMeta
from moviebotapi.common import MenuItem

from .route import bp
from .config import *


plugin.register_blueprint('notifyapi', bp)


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    basePath = '/api/plugins/notifyapi'

    # 定义前端的URL和相关的权限
    href = '/common/view?hidePadding=true#' + basePath + \
           '/frontend/index.html?t=' + str(int(round(time.time() * 1000)))
    urls = ['/get_user', '/get_notify_channel', '/save_config', '/get_config', '/del_config', '/send_notify']

    # 为以上的URLs添加权限
    server.auth.add_permission([1], href)
    for url in urls:
        server.auth.add_permission([1], basePath + url)

    # 获取当前的菜单项，如果找到"我的"菜单分组，则添加文件管理项
    menus = server.common.list_menus()
    for item in menus:
        if item.title == '我的':
            page = MenuItem()
            page.title = '通知API'
            page.href = href
            page.icon = 'Notifications'
            item.pages.append(page)
            break
    server.common.save_menus(menus)
