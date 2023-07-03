#!/usr/bin/env python3
import logging
from importlib import import_module
import time
import os

_LOGGER = logging.getLogger(__name__)
#########################依赖库初始化###########################
# 依赖库列表
import_list = [
    'alibabacloud_alidns20150109',
    'tencentcloud-sdk-python'
]
# 判断依赖库是否安装,未安装则安装对应依赖库
# sourcestr = "https://pypi.tuna.tsinghua.edu.cn/simple/"  # 镜像源
# sourceurl = "pypi.tuna.tsinghua.edu.cn"
sourcestr = "http://pypi.douban.com/simple/"  # 镜像源
sourceurl = "pypi.douban.com"


def GetPackage(PackageName):
    command = f"pip install --upgrade {PackageName}" # -i {sourcestr} --trusted-host {sourceurl}"
    # 正在安装
    # _LOGGER.info(f"「DDNS」正在安装依赖{str(PackageName)}")
    # _LOGGER.info(command)
    try:
        install_log = os.popen(command)
        # _LOGGER.info(f'「DDNS - 安装依赖脚本」安装依赖日志如下:\n{install_log.read()}')
        _LOGGER.warning(f'「DDNS - 安装依赖脚本」如果下方报错：依赖库 alibabacloud_alidns20150109,tencentcloud-sdk-python-dnspod '
                        f'安装失败导致插件载入失败，请手动进入 mbot 命令行安装')
    except Exception as e:
        _LOGGER.error(f"「DDNS - 安装依赖脚本」安装依赖库失败！原因：{e}")


for v in import_list:
    try:
        import_module(v)
    except ImportError:
        # _LOGGER.error("「DDNS」没有找到需要的依赖库:  " + v + " 现在开始安装！")
        GetPackage(v)
##############################################################
