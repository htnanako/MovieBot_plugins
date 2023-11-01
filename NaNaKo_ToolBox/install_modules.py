from importlib import import_module
import threading
import os

from .config import ConsoleLog


class InstallModule(threading.Thread):
    def __init__(self, module_name):
        threading.Thread.__init__(self)
        self.name = "InstallModule"
        self.module_name = module_name

    def run(self):
        try:
            import_module(self.module_name)
        except ImportError:
            GetPackage(self.module_name)
        except Exception as e:
            ConsoleLog().log_error(f"安装「{self.module_name}」模块失败, 原因为：{e}", exc_info=True)
        ConsoleLog().log_info(f"安装「{self.module_name}」模块完成！")


def GetPackage(module_name):
    command = f"python3 -m pip install -U {module_name} -i https://pypi.tuna.tsinghua.edu.cn/simple"
    try:
        install_log = os.popen(command).read()
        ConsoleLog().log_warning(f"正在安装「{module_name}」模块，如日志无报错，稍后自行重启容器生效。")
    except Exception as e:
        ConsoleLog().log_error(f"安装「{module_name}」模块失败, 原因为：{e}", exc_info=True)
