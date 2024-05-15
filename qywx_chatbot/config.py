import logging
import httpx

from typing import Dict, Any
from mbot.core.plugins import (
    plugin,
    PluginMeta
)

logger = logging.getLogger(__name__)

base_url = "https://api.openai.com"
proxies = None
api_key = ""
context_num = 0
model = ""
custom_model = ""
custom_prompt = ""
draw_info = ""
qywx_base_url = "https://qyapi.weixin.qq.com"
sCorpID = ""
sCorpsecret = ""
sAgentid = ""
sToken = ""
sEncodingAESKey = ""

def init_config(web_config: dict[str, str]):
    global base_url, proxies, api_key, context_num, model, custom_model, custom_prompt, draw_info, qywx_base_url, sCorpID, sCorpsecret, sAgentid, sToken, sEncodingAESKey

    base_url = web_config.get('base_url', base_url)
    proxy = web_config.get('proxy', None)
    api_key = web_config.get('api_key')
    context_num = web_config.get('context_num', 0)
    model = web_config.get('model')
    custom_model = web_config.get('custom_model')
    custom_prompt = web_config.get('custom_prompt')
    draw_info = web_config.get('draw_info')
    qywx_base_url = web_config.get('qywx_base_url', qywx_base_url)
    sCorpID = web_config.get('sCorpID')
    sCorpsecret = web_config.get('sCorpsecret')
    sAgentid = web_config.get('sAgentid')
    sToken = web_config.get('sToken')
    sEncodingAESKey = web_config.get('sEncodingAESKey')

    if model == "customizable":
        model = custom_model
    if proxy:
        proxies = {
            "http://": proxy,
            "https://": proxy,
            "sock5://": proxy
        }
    

    config_list = [base_url, api_key, model, qywx_base_url, sCorpID, sCorpsecret, sAgentid, sToken, sEncodingAESKey]
    for config_item in config_list:
        if not config_item:
            logger.error(f"「ChatBot」ChatBot配置不完整，配置完成后重启。")
            return
    logger.info(f"「ChatBot」ChatBot配置完成。Base_url:{base_url}, API_KEY:{api_key[:7]}*****{api_key[-6:]}, Model:{model}")


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    init_config(config)


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    init_config(config)