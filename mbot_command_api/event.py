import httpx

from mbot.openapi import mbot_api

command_list_api = "/api/plugins/get_plugin_command_list"
run_command_api = "/api/plugins/run_command"
server = mbot_api

access_key = server.auth.get_default_ak()
web = server.config.web
port = web.port
base_url = f"http://localhost:{port}"


class CommandList:
    def __init__(self):
        self.command_list = []

    def get_command_list(self):
        r = httpx.get(url=f"{base_url}{command_list_api}?access_key={access_key}")
        r_json = r.json()
        self.command_list = []
        for command_item in r_json["data"]:
            if command_item["has_args"] == 0:
                name = command_item["name"]
                title = command_item["title"]
                plugin_title = command_item["plugin_title"]
                plugin_name = command_item["plugin_name"]
                result_item = {
                    "name": name,
                    "title": title,
                    "plugin_title": plugin_title,
                    "plugin_name": plugin_name
                }
                self.command_list.append(result_item)
        return self.command_list

    def select_command(self, title):
        data = {}
        for command_item in self.command_list:
            if command_item["title"] == title:
                command_name = command_item["name"]
                plugin_name = command_item["plugin_name"]
                data = {
                    "command_name": command_name,
                    "plugin_name": plugin_name
                }
                break
            else:
                continue
        if not data:
            return None
        r = httpx.post(url=f"{base_url}{run_command_api}?access_key={access_key}", json=data)
        if r.status_code == 200:
            return r.json()
