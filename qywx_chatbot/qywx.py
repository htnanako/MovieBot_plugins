import os
import datetime
import threading
import httpx
import json
import asyncio
import logging
from cacheout import Cache
from flask import Blueprint, request, send_file
from xml.etree.ElementTree import fromstring
from tenacity import wait_fixed, stop_after_attempt, retry
from typing import Dict, Any

from . import config
from .chatapi import chat, draw
from .qywx_Crypt.WXBizMsgCrypt import WXBizMsgCrypt
from .utils import UserRecords

from mbot.core.plugins import PluginMeta
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from mbot.openapi import mbot_api

APP_USER_AGENT = "moviebot/qywx_chatbot"

bp = Blueprint('qywx_chatbot', __name__)
"""
把flask blueprint注册到容器
这个URL访问完整的前缀是 /api/plugins/你设置的前缀
"""
plugin.register_blueprint('qywx_chatbot', bp)

logger = logging.getLogger(__name__)

token_cache = Cache(maxsize=1000)
server = mbot_api
web = server.config.web
server_url = web.server_url



class QywxSendMessage:
    def __init__(self):
        self.BASE_URL = config.qywx_base_url.strip('/')
        self.sCorpID = config.sCorpID
        self.sCorpsecret = config.sCorpsecret
        self.sAgentid = config.sAgentid
        self.sToken = config.sToken
        self.sEncodingAESKey = config.sEncodingAESKey
        self.token_cache = token_cache.get('access_token')
        self.token_expires_time = token_cache.get('expires_time')

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def get_access_token(self):
        if self.token_expires_time is not None and self.token_expires_time >= datetime.datetime.now():
            return self.token_cache
        res = httpx.get(
            f'{self.BASE_URL}/cgi-bin/gettoken?corpid={self.sCorpID}&corpsecret={self.sCorpsecret}', headers={
                'user-agent': APP_USER_AGENT
            })
        j = res.json()
        if j['errcode'] == 0:
            self.token_expires_time = datetime.datetime.now() + datetime.timedelta(seconds=j['expires_in'] - 500)
            self.token_cache = j['access_token']
            token_cache.set('access_token', self.token_cache, ttl=j['expires_in'] - 500)
            token_cache.set('expires_time', self.token_expires_time, ttl=j['expires_in'] - 500)
            return self.token_cache
        else:
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def __do_send_message__(self, access_token, data):
        url = f'{self.BASE_URL}/cgi-bin/message/send?access_token={access_token}'
        res = httpx.post(url, data=data, headers={
            'user-agent': APP_USER_AGENT
        })
        return res.json()

    def send_text_message(self, text_message, to_user):
        access_token = self.get_access_token()
        if access_token is None:
            logger.error('「ChatBot」获取企业微信access_token失败，请检查你的corpid和corpsecret配置')
            return
        data = json.dumps({
            'touser': to_user,
            'agentid': self.sAgentid,
            'msgtype': 'text',
            'text': {
                "content": text_message
            }
        }, ensure_ascii=False).encode('utf8')
        json_data = self.__do_send_message__(access_token, data)
        if json_data.get('errcode') != 0:
            logger.error(f'「ChatBot」企业微信推送失败：{json_data}')

    def send_img_text_message(self, title, content, img_url, to_user):
        access_token = self.get_access_token()
        if access_token is None:
            logger.error('「ChatBot」获取企业微信access_token失败，请检查你的corpid和corpsecret配置')
            return
        data = json.dumps({
            "touser": to_user,
            "msgtype": "news",
            "agentid": self.sAgentid,
            "news": {
                "articles": [
                    {
                        "title": title,
                        "description": content,
                        "url": img_url,
                        "picurl": img_url,
                    }
                ]
            },
        }, ensure_ascii=False).encode('utf8')
        json_data = self.__do_send_message__(access_token, data)
        if json_data.get('errcode') != 0:
            logger.error(f'「ChatBot」企业微信推送失败：{json_data}')


class QywxTextMsgThread(threading.Thread):
    def __init__(self, query: str, touser: str, agentid: str, session_id: str):
        threading.Thread.__init__(self)
        self.name = "QywxTextMsgThread"
        self.query = query
        self.touser = touser
        self.agentid = agentid
        self.session_id = session_id

    def run(self):
        try:
            result = asyncio.run(chat(query=self.query, username=self.touser))
            QywxSendMessage().send_text_message(result, self.touser)
        except Exception as e:
            logger.error(f'「ChatBot」企业微信推送失败：{e}', exc_info=True)


class QywxImgMsgThread(threading.Thread):
    def __init__(self, prompt: str, touser: str, agentid: str):
        threading.Thread.__init__(self)
        self.name = "QywxImgMsgThread"
        self.prompt = prompt
        self.touser = touser
        self.agentid = agentid
        self.server_url = server_url

    def run(self):
        try:
            result = asyncio.run(draw(prompt=self.prompt,
                                      draw_info=config.draw_info))
            if result.get("success"):
                img_prompt = result.get("img_prompt")
                img_name = result.get("img_name")
                if self.server_url:
                    img_url = f"{self.server_url.rstrip('/')}/api/plugins/qywx_chatbot/img?img_name={img_name}"
                else:
                    img_url = result.get("img_url")
                if not img_name:
                    img_url = result.get("img_url")
                title = "Draw Image Complete"
                QywxSendMessage().send_img_text_message(title, img_prompt, img_url, self.touser)
            else:
                error = result.get("error")
                title = "Draw Image Fail"
                QywxSendMessage().send_text_message(f'{title}\n{error}', self.touser)
        except Exception as e:
            logger.error(f'「ChatBot」企业微信推送失败：{e}', exc_info=True)


@bp.route("/chat", methods=['GET'])
def verify():
    try:
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        wxcpt = WXBizMsgCrypt(config.sToken, config.sEncodingAESKey, config.sCorpID)
        ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        if ret == 0:
            logger.info("「ChatBot」verifyurl echostr: " + sEchoStr.decode('utf-8'))
            return sEchoStr.decode('utf-8'), 200
        else:
            logger.error(f"「ChatBot」ERR: VerifyURL ret: {str(sEchoStr)}")
            return '', 401
    except Exception as e:
        logger.error(f'「ChatBot」回调接口出错了，{e}', exc_info=True)
        return '', 500


@bp.route("/chat", methods=['POST'])
def recv():
    try:
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        wxcpt = WXBizMsgCrypt(config.sToken, config.sEncodingAESKey, config.sCorpID)
        if wxcpt is None:
            logger.error('「ChatBot」没有配置企业微信的接收消息设置，不能使用此功能。')
            return '', 500
        body = request.data
        ret, sMsg = wxcpt.DecryptMsg(body.decode('utf-8'), msg_signature, timestamp, nonce)
        decrypt_data = {}
        for node in list(fromstring(sMsg.decode('utf-8'))):
            decrypt_data[node.tag] = node.text
        content = decrypt_data.get('Content')
        fromuser = decrypt_data.get('FromUserName')
        touser = decrypt_data.get('ToUserName')
        create_time = decrypt_data.get('CreateTime')
        msg_type = decrypt_data.get('MsgType')
        msg_id = decrypt_data.get('MsgId')
        if any(content.startswith(prefix) for prefix in config.clear_context_command):
            UserRecords().clear_records(fromuser)
            reply = f"<xml><ToUserName>{touser}</ToUserName><FromUserName>{fromuser}</FromUserName><CreateTime>{create_time}</CreateTime><MsgType>{msg_type}</MsgType><Content>清理上下文完成</Content><MsgId>{msg_id}</MsgId><AgentID>{config.sAgentid}</AgentID></xml>"
            ret, send_Msg = wxcpt.EncryptMsg(reply, nonce, timestamp)
            return send_Msg, 200
        if content.startswith("画"):
            logger.info(f"「ChatBot」Draw: {content.strip()}[dall-e-3]")
            draw_thread = QywxImgMsgThread(content.replace('画', '').strip(), fromuser, config.sAgentid)
            draw_thread.start()
            reply = f"<xml><ToUserName>{touser}</ToUserName><FromUserName>{fromuser}</FromUserName><CreateTime>{create_time}</CreateTime><MsgType>{msg_type}</MsgType><Content>正在画图，请稍后....</Content><MsgId>{msg_id}</MsgId><AgentID>{config.sAgentid}</AgentID></xml>"
            ret, send_Msg = wxcpt.EncryptMsg(reply, nonce, timestamp)
            return send_Msg, 200
        else:
            logger.info(f"「ChatBot」Chat: {content}[{config.model}]")
            chat_thread = QywxTextMsgThread(content, fromuser, config.sAgentid, session_id=fromuser)
            chat_thread.start()
            reply = f"<xml><ToUserName>{touser}</ToUserName><FromUserName>{fromuser}</FromUserName><CreateTime>{create_time}</CreateTime><MsgType>{msg_type}</MsgType><Content>思考中....</Content><MsgId>{msg_id}</MsgId><AgentID>{config.sAgentid}</AgentID></xml>"
        ret, send_Msg = wxcpt.EncryptMsg(reply, nonce, timestamp)
        return send_Msg, 200
    except Exception as e:
        logger.error(f'「ChatBot」处理微信消息出错。{e}', exc_info=True)
        return '', 500


@bp.route("/img", methods=['GET'])
def show_img():
    img_name = request.args.get('img_name')
    img_path = f'/data/img_output/{img_name}'
    if not os.path.exists(img_path):
        return '', 404
    return send_file(img_path, mimetype='image/png')
