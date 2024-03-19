import os

from mbot.openapi import mbot_api


notify_api_file_path = "/data/conf/notifyapi_config.json"
if not os.path.exists(notify_api_file_path):
    with open(notify_api_file_path, "w") as nf:
        nf.write("[]")

server = mbot_api
server_ak = server.auth.get_default_ak()
port = server.config.web.port
