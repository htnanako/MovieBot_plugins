from importlib import import_module
import os

from .config import *


class InstallModule:
    def __init__(self):
        pass

    @staticmethod
    def main(modules: list):
        need_install_modules = []
        for module in modules:
            try:
                import_module(module)
                logger.info(f"「奈奈子的工具箱」: 「{module}」模块已安装。")
            except ImportError:
                need_install_modules.append(module)
        if need_install_modules:
            for module in need_install_modules:
                GetPackage(module)
                logger.info(f"「奈奈子的工具箱」: 安装「{module}」模块完成！")
            server.common.restart_app()


def GetPackage(module_name):
    command = f"python3 -m pip install -U {module_name} -i https://pypi.tuna.tsinghua.edu.cn/simple"
    try:
        install_log = os.popen(command).read()
        logger.warning(f"「奈奈子的工具箱」: 正在安装「{module_name}」模块。")
    except Exception as e:
        logger.error(f"「奈奈子的工具箱」: 安装「{module_name}」模块失败, 原因为：{e}", exc_info=True)
