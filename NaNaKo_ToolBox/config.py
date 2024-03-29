import logging

from mbot.openapi import mbot_api

command_list_api = "/api/plugins/get_plugin_command_list"
run_command_api = "/api/plugins/run_command"
get_all_sys_notify_api = "/api/user/get_all_sys_notify"
log_page_url = "/setting/app-log"
search_site_uri = "/api/movie/search_keyword"
server = mbot_api

access_key = server.auth.get_default_ak()
web = server.config.web
port = web.port
base_url = f"http://localhost:{port}"

logger = logging.getLogger(__name__)

