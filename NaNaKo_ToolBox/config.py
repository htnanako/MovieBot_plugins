import logging

from mbot.openapi import mbot_api

command_list_api = "/api/plugins/get_plugin_command_list"
run_command_api = "/api/plugins/run_command"
get_all_sys_notify_api = "/api/user/get_all_sys_notify"
log_page_url = "/setting/app-log"
server = mbot_api

access_key = server.auth.get_default_ak()
web = server.config.web
port = web.port
base_url = f"http://localhost:{port}"

logger = logging.getLogger(__name__)


class ConsoleLog:
    def __init__(self):
        self.name = "ConsoleLog"

    def log_info(self, content: str, exc_info=False):
        logger.info(f"「奈奈子的工具箱」: {content}", exc_info=exc_info)

    def log_warning(self, content: str, exc_info=False):
        logger.warning(f"「奈奈子的工具箱」: {content}", exc_info=exc_info)

    def log_error(self, content: str, exc_info=False):
        logger.error(f"「奈奈子的工具箱」: {content}", exc_info=exc_info)
