import json

from urllib.parse import unquote

from .config import *


class Config:
    def __init__(self):
        self.config_path = notify_api_file_path
        # if not os.path.exists(self.config_path):
        #     with open(self.config_path, "w") as nf:
        #         nf.write("[]")

    def get_config(self):
        with open(self.config_path, "r") as nf:
            return json.loads(nf.read())

    def _save_config(self, config: dict):
        with open(self.config_path, "w") as nf:
            nf.write(json.dumps(config, indent=4, ensure_ascii=False))

    def update_config(self, data: dict):
        conf = self.get_config()
        default_img = data.get("default_img")
        if default_img:
            data["default_img"] = unquote(default_img)
        if not data.get("id"):
            ids = [item["id"] for item in conf]
            if ids:
                data["id"] = max(ids) + 1
            else:
                data["id"] = 1
            conf.append(data)
        else:
            for index, item in enumerate(conf):
                if item["id"] == data["id"]:
                    conf[index] = data
                    break
        self._save_config(conf)

    def del_config(self, id: int):
        conf = self.get_config()
        for index, item in enumerate(conf):
            if item["id"] == id:
                conf.pop(index)
                break
        self._save_config(conf)
