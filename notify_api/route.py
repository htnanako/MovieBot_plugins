import httpx
import logging

from flask import Blueprint, request
from mbot.register.controller_register import login_required

from .common.response import *
from .utils import *
from .main import NotifyApiMain

bp = Blueprint('notifyapi', __name__,
               static_folder='./frontend/dist', static_url_path='/frontend')

logger = logging.getLogger(__name__)


@bp.route('/get_user', methods=["GET"])
@login_required()
def get_user():
    """
    获取用户列表
    :return:  用户列表
    """
    user_list = server.user.list()
    return data_to_json_200(message="success", data=[{"name": user.nickname, "value": user.uid} for user in user_list])


@bp.route('/get_notify_channel', methods=["GET"])
@login_required()
def get_notify_channel():
    """
    获取通知渠道列表
    :return:  通知渠道列表
    """
    get_notify_list_url = f"http://127.0.0.1:{port}/api/setting/get_notify?access_key={server_ak}"
    res = httpx.get(get_notify_list_url)
    channel_data = res.json()["data"]
    channal_enum = []
    for item in channel_data:
        name = item["name"]
        value = item["name"]
        channal_enum.append({"name": name, "value": value})
    return data_to_json_200(message="success", data=channal_enum)


@bp.route('/save_config', methods=["POST"])
@login_required()
def save_config():
    """
    保存配置
    :return:  保存结果
    """
    data = request.json
    if not data:
        return data_to_json_200(message="error", data="数据为空")
    Config().update_config(data)
    return data_to_json_200(message="配置已保存", data=data)


@bp.route('/get_config', methods=["GET"])
@login_required()
def get_config():
    """
    获取配置
    :return:  配置
    """
    config = Config().get_config()
    return data_to_json_200(message="success", data=config)


@bp.route('/del_config', methods=["GET"])
@login_required()
def del_config():
    """
    删除配置
    :return:  删除结果
    """
    id = request.args.get("id")
    if not id:
        return json_500(message="Miss ID")
    Config().del_config(int(id))
    return json_200(message="删除成功")


@bp.route('/send_notify', methods=["POST", "GET"])
@login_required()
def send_notify():
    """
    发送通知
    :return:  发送结果
    """
    try:
        if request.method == "GET":
            title = request.args.get("title")
            content = request.args.get("content")
            id = request.args.get("id")
            pic_url = request.args.get("pic_url", None)
            link_url = request.args.get("link_url", None)
        else:
            data = request.json
            title = data.get("title")
            content = data.get("content")
            id = data.get("id")
            pic_url = data.get("pic_url", None)
            link_url = data.get("link_url", None)
        if not title:
            return json_500(message="Miss Title")
        if not content:
            return json_500(message="Miss Content")
        if not id:
            return json_500(message="Miss Id")
        mes = {
            "title": title,
            "content": content,
            "id": int(id),
            "pic_url": pic_url,
            "link_url": link_url
        }
        logger.info(f"「Notify API」发送通知: {mes}")
        if NotifyApiMain().send_notify(mes):
            return json_200(message="发送成功")
        else:
            return json_500(message="发送失败, 请查看日志")
    except Exception as e:
        logger.error(f"「Notify API」 发送通知失败: {e}", exc_info=True)
        return json_500(message=str(e))
