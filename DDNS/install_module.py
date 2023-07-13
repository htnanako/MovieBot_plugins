#!/usr/bin/env python3
import logging
from importlib import import_module
import threading
import os


_LOGGER = logging.getLogger(__name__)


class ImportModule(threading.Thread):
    def __init__(self, import_list):
        threading.Thread.__init__(self)
        self.name = "ImportModule"
        self.import_list = import_list

    def run(self):
        for v in self.import_list:
            try:
                import_module(v)
            except ImportError:
                _LOGGER.error("「DDNS」没有找到需要的依赖库:  " + v + " 现在开始安装！")
                GetPackage(v)
            except Exception as e:
                _LOGGER.error(f"「DDNS」导入依赖库失败！原因：{e}", exc_info=True)
        _LOGGER.info("「DDNS」依赖库导入完成！")


def GetPackage(PackageName):
    command = f"pip install --upgrade {PackageName}"
    try:
        install_log = os.popen(command).read()
        _LOGGER.warning(f'「DDNS - 安装依赖脚本」如果下方报错：依赖库 alibabacloud_alidns20150109,tencentcloud-sdk-python'
                        f'安装失败导致插件载入失败，请手动进入 mbot 命令行安装')
    except Exception as e:
        _LOGGER.error(f"「DDNS - 安装依赖脚本」安装依赖库失败！原因：{e}")
