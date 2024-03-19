import json
import datetime

from flask import Response
from typing import Union


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(obj)


def data_to_json_200(message: Union[str, None] = None, data: Union[bool, list, dict, str, None] = None) -> Response:
    """
    返回http_status=200的结果
    :param message: 消息
    :param data: 返回结果
    :return:
    """
    if not message:
        message = "success"
    return Response(
        mimetype="application/json",
        status=200,
        response=json.dumps({
            'success': True,
            'errorCode': 0,
            'message': message,
            'data': data
        }, cls=CustomJSONEncoder),
    )


def json_200(message: Union[str, None] = None) -> Response:
    """
    返回http_status=200的结果
    :param message: 消息
    :return:
    """
    if not message:
        message = "success"
    return Response(
        mimetype="application/json",
        status=200,
        response=json.dumps({
            'success': True,
            'errorCode': 0,
            'message': message,
        }, cls=CustomJSONEncoder),
    )


def json_500(message: Union[str, None] = None) -> Response:
    """
    返回http_status=500的结果
    :param message: 消息
    :return:
    """
    if not message:
        message = "error"
    return Response(
        mimetype="application/json",
        status=500,
        response=json.dumps({
            'success': False,
            'errorCode': 500,
            'message': message,
        }, cls=CustomJSONEncoder),

    )


def json_with_status(status_code: int, message: Union[str, None] = None, data: Union[bool, list, dict, str, None] = None) -> Response:
    """
    返回自定义statuscode的结果
    :param status_code: 状态码
    :param data: 返回结果
    :param message: 消息
    :return:
    """
    if not message:
        message = "success" if status_code == 200 else "error"
    return Response(
        mimetype="application/json",
        status=status_code,
        response=json.dumps({
            'success': True if status_code == 200 else False,
            'errorCode': status_code,
            'message': message,
            'data': data
        }, cls=CustomJSONEncoder),
    )
