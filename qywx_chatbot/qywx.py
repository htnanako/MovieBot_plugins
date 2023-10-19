import datetime
import threading
import httpx
import json
import asyncio
import logging
from flask import Blueprint, request
from xml.etree.ElementTree import fromstring
from tenacity import wait_fixed, stop_after_attempt, retry
from typing import Dict, Any

from .chatapi import chat
from .qywx_Crypt.WXBizMsgCrypt import WXBizMsgCrypt

from mbot.core.plugins import PluginMeta
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse

APP_USER_AGENT = "moviebot/qywx_chatbot"

bp = Blueprint('qywx_chatbot', __name__)
"""
把flask blueprint注册到容器
这个URL访问完整的前缀是 /api/plugins/你设置的前缀
"""
plugin.register_blueprint('qywx_chatbot', bp)

logger = logging.getLogger(__name__)


def main_config(config):
    global SERVICE, base_url, proxies, self_url, api_key, session_limit, model
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
    qywx_base_url = config.get('qywx_base_url')
    sCorpID = config.get('sCorpID')
    sCorpsecret = config.get('sCorpsecret')
    sAgentid = config.get('sAgentid')
    sToken = config.get('sToken')
    sEncodingAESKey = config.get('sEncodingAESKey')
    config_list = [base_url, api_key, model, qywx_base_url, sCorpID, sCorpsecret, sAgentid, sToken, sEncodingAESKey]
    for config_item in config_list:
        if not config_item:
            logger.error(f"chatbot配置不完整，配置完成后重启。")
            return
    if 'openai' in SERVICE and 'claude' in model:
        logger.error(f"OPENAI官方接口不支持Claude模型，请重新选择。")
        return
    logger.info(f"chatbot配置完成。Base_url:{base_url}, API_KEY:{api_key[:7]}*****{api_key[-6:]}, Model:{model}")


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
        self.token_cache = None
        self.token_expires_time = None

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
            return self.token_cache
        else:
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
    def __do_send_message__(self, access_token, params):
        url = f'{self.BASE_URL}/cgi-bin/message/send?access_token={access_token}'
        res = httpx.post(url, data=params, headers={
            'user-agent': APP_USER_AGENT
        })
        return res.json()

    def send_text_message(self, text_message, to_user):
        access_token = self.get_access_token()
        if access_token is None:
            logger.error('获取企业微信access_token失败，请检查你的corpid和corpsecret配置')
            return
        params = json.dumps({
            'touser': to_user,
            'agentid': self.sAgentid,
            'msgtype': 'text',
            'text': {
                "content": text_message
            }
        }, ensure_ascii=False).encode('utf8')
        json_data = self.__do_send_message__(access_token, params)
        if json_data.get('errcode') != 0:
            logger.error(f'企业微信推送失败：{json_data}')


class QywxTaskThread(threading.Thread):
    def __init__(self, query: str, touser: str, agentid: str, session_id: str):
        threading.Thread.__init__(self)
        self.name = "QywxTaskThread"
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
            logger.error(f'企业微信推送失败：{e}', exc_info=True)


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
            logger.info("verifyurl echostr: " + sEchoStr.decode('utf-8'))
            return sEchoStr.decode('utf-8'), 200
        else:
            logger.error(f"ERR: VerifyURL ret: {str(sEchoStr)}")
            return '', 401
    except Exception as e:
        logger.error(f'回调接口出错了，{e}', exc_info=True)
        return '', 500


@bp.route("/chat", methods=['POST'])
def recv():
    try:
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
        if wxcpt is None:
            logger.error('没有配置企业微信的接收消息设置，不能使用此功能。')
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
        if 'openai' in SERVICE and 'claude' in model:
            logger.info(f"Chat: {content}[{model}]")
            logger.error(f"OPENAI官方接口不支持Claude模型，请重新选择。")
            reply_msg = f"OPENAI官方接口不支持Claude模型"
            reply = f"<xml><ToUserName>{touser}</ToUserName><FromUserName>{fromuser}</FromUserName><CreateTime>{create_time}</CreateTime><MsgType>{msg_type}</MsgType><Content>{reply_msg}</Content><MsgId>{msg_id}</MsgId><AgentID>{sAgentid}</AgentID></xml>"
            ret, send_Msg = wxcpt.EncryptMsg(reply, nonce, timestamp)
            return send_Msg, 200
        if content.startswith("/b") or content.startswith("/g"):
            if 'aiproxy' in SERVICE:
                logger.info(f"Chat: {content.replace('/b', '').replace('/g', '').strip()}[{model}]")
                replymsg = "联网搜索中...."
            else:
                logger.info(f"Chat: {content.replace('/b', '').replace('/g', '').strip()}[{model}]")
                content = content.replace('/b', '').replace('/g', '').strip()
                replymsg = f"思考中....\nOPENAI官方接口不支持Bing或Google搜索"
            chat_thread = QywxTaskThread(content, fromuser, sAgentid, session_id=fromuser)
            chat_thread.start()
            reply = f"<xml><ToUserName>{touser}</ToUserName><FromUserName>{fromuser}</FromUserName><CreateTime>{create_time}</CreateTime><MsgType>{msg_type}</MsgType><Content>{replymsg}</Content><MsgId>{msg_id}</MsgId><AgentID>{sAgentid}</AgentID></xml>"
        else:
            logger.info(f"Chat: {content}[{model}]")
            chat_thread = QywxTaskThread(content, fromuser, sAgentid, session_id=fromuser)
            chat_thread.start()
            reply = f"<xml><ToUserName>{touser}</ToUserName><FromUserName>{fromuser}</FromUserName><CreateTime>{create_time}</CreateTime><MsgType>{msg_type}</MsgType><Content>思考中....</Content><MsgId>{msg_id}</MsgId><AgentID>{sAgentid}</AgentID></xml>"
        ret, send_Msg = wxcpt.EncryptMsg(reply, nonce, timestamp)
        return send_Msg, 200
    except Exception as e:
        logger.error(f'处理微信消息出错。{e}', exc_info=True)
        return '', 500
