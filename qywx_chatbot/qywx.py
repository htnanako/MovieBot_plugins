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

from .chatapi import chat, draw
from .qywx_Crypt.WXBizMsgCrypt import WXBizMsgCrypt

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


def main_config(config):
    global SERVICE, base_url, proxies, self_url, api_key, session_limit, model, draw_info
    global qywx_base_url, sCorpID, sCorpsecret, sAgentid, sToken, sEncodingAESKey
    # base_url = config.get('SERVICE')
    SERVICE = config.get('SERVICE')
    self_url = config.get('self_url')
    if self_url:
        base_url = self_url.strip('/')
    elif SERVICE == 'openai':
        base_url = 'https://api.openai.com'
    elif SERVICE == 'aiproxy':
        base_url = 'https://api.aiproxy.io'
    proxy = config.get('proxy')
    proxies = None
    if proxy:
        proxies = {
            "http://": proxy,
            "https://": proxy,
            "sock5://": proxy
        }
    api_key = config.get('api_key')
    session_limit = config.get('session_limit')
    model = config.get('model')
    draw_info = config.get('draw_info')
    qywx_base_url = config.get('qywx_base_url')
    sCorpID = config.get('sCorpID')
    sCorpsecret = config.get('sCorpsecret')
    sAgentid = config.get('sAgentid')
    sToken = config.get('sToken')
    sEncodingAESKey = config.get('sEncodingAESKey')
    config_list = [base_url, api_key, model, qywx_base_url, sCorpID, sCorpsecret, sAgentid, sToken, sEncodingAESKey]
    for config_item in config_list:
        if not config_item:
            logger.error(f"「ChatBot」ChatBot配置不完整，配置完成后重启。")
            return
    if 'openai' in SERVICE and 'claude' in model:
        logger.error(f"「ChatBot」OPENAI官方接口不支持Claude模型，请重新选择。")
        return
    logger.info(f"「ChatBot」ChatBot配置完成。Base_url:{base_url}, API_KEY:{api_key[:7]}*****{api_key[-6:]}, Model:{model}")


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    main_config(config)


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    main_config(config)


class QywxSendMessage:
    def __init__(self):
        self.BASE_URL = qywx_base_url.strip('/')
        self.sCorpID = sCorpID
        self.sCorpsecret = sCorpsecret
        self.sAgentid = sAgentid
        self.sToken = sToken
        self.sEncodingAESKey = sEncodingAESKey
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
            result = asyncio.run(chat(SERVICE=SERVICE,
                                      base_url=base_url,
                                      proxy=proxies,
                                      api_key=api_key,
                                      model=model,
                                      query=self.query,
                                      session_id=self.session_id,
                                      session_limit=session_limit))
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
            result = asyncio.run(draw(base_url=base_url,
                                      proxy=proxies,
                                      api_key=api_key,
                                      prompt=self.prompt,
                                      draw_info=draw_info))
            if result.get("success"):
                img_prompt = result.get("img_prompt")
                img_name = result.get("img_name")
                if self.server_url:
                    img_url = f"{self.server_url.rstrip('/')}/api/plugins/qywx_chatbot/img?img_name={img_name}"
                else:
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
        wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
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
        wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
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
        if content.startswith("画"):
            logger.info(f"「ChatBot」Draw: {content.strip()}[dall-e-3]")
            draw_thread = QywxImgMsgThread(content.replace('画', '').strip(), fromuser, sAgentid)
            draw_thread.start()
            reply = f"<xml><ToUserName>{touser}</ToUserName><FromUserName>{fromuser}</FromUserName><CreateTime>{create_time}</CreateTime><MsgType>{msg_type}</MsgType><Content>正在画图，请稍后....</Content><MsgId>{msg_id}</MsgId><AgentID>{sAgentid}</AgentID></xml>"
            ret, send_Msg = wxcpt.EncryptMsg(reply, nonce, timestamp)
            return send_Msg, 200
        if 'openai' in SERVICE and 'claude' in model:
            logger.info(f"「ChatBot」Chat: {content}[{model}]")
            logger.error(f"「ChatBot」OPENAI官方接口不支持Claude模型，请重新选择。")
            reply_msg = f"OPENAI官方接口不支持Claude模型"
            reply = f"<xml><ToUserName>{touser}</ToUserName><FromUserName>{fromuser}</FromUserName><CreateTime>{create_time}</CreateTime><MsgType>{msg_type}</MsgType><Content>{reply_msg}</Content><MsgId>{msg_id}</MsgId><AgentID>{sAgentid}</AgentID></xml>"
            ret, send_Msg = wxcpt.EncryptMsg(reply, nonce, timestamp)
            return send_Msg, 200
        if content.startswith("/b") or content.startswith("/g"):
            if 'aiproxy' in SERVICE:
                logger.info(f"「ChatBot」Chat: {content.replace('/b', '').replace('/g', '').strip()}[{model}]")
                replymsg = "联网搜索中...."
            else:
                logger.info(f"「ChatBot」Chat: {content.replace('/b', '').replace('/g', '').strip()}[{model}]")
                content = content.replace('/b', '').replace('/g', '').strip()
                replymsg = f"思考中....\nOPENAI官方接口不支持Bing或Google搜索"
            chat_thread = QywxTextMsgThread(content, fromuser, sAgentid, session_id=fromuser)
            chat_thread.start()
            reply = f"<xml><ToUserName>{touser}</ToUserName><FromUserName>{fromuser}</FromUserName><CreateTime>{create_time}</CreateTime><MsgType>{msg_type}</MsgType><Content>{replymsg}</Content><MsgId>{msg_id}</MsgId><AgentID>{sAgentid}</AgentID></xml>"
        else:
            logger.info(f"「ChatBot」Chat: {content}[{model}]")
            chat_thread = QywxTextMsgThread(content, fromuser, sAgentid, session_id=fromuser)
            chat_thread.start()
            reply = f"<xml><ToUserName>{touser}</ToUserName><FromUserName>{fromuser}</FromUserName><CreateTime>{create_time}</CreateTime><MsgType>{msg_type}</MsgType><Content>思考中....</Content><MsgId>{msg_id}</MsgId><AgentID>{sAgentid}</AgentID></xml>"
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
