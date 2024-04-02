from importlib import import_module, metadata
import os

from .config import *


class InstallModule:
    def __init__(self):
        pass

    @staticmethod
    def check_version(module_name):
        try:
            return metadata.version(module_name)
        except Exception:
            return None

    def main(self, modules: list):
        need_install_modules = []
        for module in modules:
            if '=' in module:
                module_name = module.split('=')[0]
                version = module.split('=')[1]
            else:
                module_name = module
                version = None
            try:
                if version:
                    installed_version = self.check_version(module_name)
                    if not installed_version or installed_version != version:
                        raise ImportError
                else:
                    import_module(module)
                    logger.info(f"「奈奈子的工具箱」: 「{module}」模块已安装。")
            except ImportError:
                need_install_modules.append(module)
        if need_install_modules:
            for module in need_install_modules:
                if '=' in module:
                    module_name = module.split('=')[0]
                    version = module.split('=')[1]
                else:
                    module_name = module
                    version = None
                GetPackage(module_name, version)
                logger.info(f"「奈奈子的工具箱」: 安装「{module}」模块完成！")
            server.common.restart_app()


def GetPackage(module_name, version=None):
    if version:
        command = f"python3 -m pip install -U {module_name}=={version} -i https://pypi.tuna.tsinghua.edu.cn/simple"
    else:
        command = f"python3 -m pip install -U {module_name} -i https://pypi.tuna.tsinghua.edu.cn/simple"
    try:
        install_log = os.popen(command).read()
        logger.warning(f"「奈奈子的工具箱」: 正在安装「{module_name}」模块。")
    except Exception as e:
        logger.error(f"「奈奈子的工具箱」: 安装「{module_name}」模块失败, 原因为：{e}", exc_info=True)
