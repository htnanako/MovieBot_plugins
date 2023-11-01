from flask import Blueprint, request
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from mbot.register.controller_register import login_required

from .event import CommandList

APP_USER_AGENT = "moviebot/command_api"

bp = Blueprint('toolbox', __name__)
"""
把flask blueprint注册到容器
这个URL访问完整的前缀是 /api/plugins/你设置的前缀
"""
plugin.register_blueprint('toolbox', bp)
command_list = CommandList()


@bp.route('/search', methods=["GET"])
@login_required()
def search():
    search_result = command_list.get_command_list()
    return search_result, 200


@bp.route("/push", methods=["GET"])
@login_required()
def push():
    title = request.args.get("title")
    run_result = command_list.select_command(title)
    return run_result, 200
