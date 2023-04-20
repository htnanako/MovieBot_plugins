from mbot.core.plugins import plugin
from mbot.core.plugins import PluginContext, PluginMeta
from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from typing import Dict, Any
from mbot.openapi import mbot_api
import re
import logging

import json
import requests

server = mbot_api


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    global uid, ToChannelName, refreshToken, task_enable
    uid = config.get('uid')
    ToChannelName = config.get('ToChannelName')
    refreshToken = config.get('refreshToken')
    task_enable = config.get('task_enable')
    if task_enable and not refreshToken:
        logging.error(f'[aliyunpan_signin]:请检查refreshToken是否正确填写。')
        return
    refreshToken_str = set_token_secret()
    logging.info(f'[aliyunpan_signin]:阿里云盘签到正常启动，refreshToken:{refreshToken_str}')


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    global uid, ToChannelName, refreshToken, task_enable
    uid = config.get('uid')
    ToChannelName = config.get('ToChannelName')
    refreshToken = config.get('refreshToken')
    task_enable = config.get('task_enable')
    if task_enable and not refreshToken:
        logging.error(f'[aliyunpan_signin]:请检查refreshToken是否正确填写。')
        return
    refreshToken_str = set_token_secret()
    logging.info(f'[aliyunpan_signin]:阿里云盘签到配置修改，refreshToken:{refreshToken_str}')


@plugin.task('aliyunpan_signin_task', '阿里云盘签到', cron_expression='10 0 * * *')
def aliyunpan_signin_task():
    if task_enable:
        main()


@plugin.command(name='aliyunpan_signin_command', title='阿里云盘签到', desc='点击执行阿里云盘签到', icon='AutoAwesome',
                run_in_background=True)
def aliyunpan_signin_command(ctx: PluginCommandContext):
    main()
    return PluginCommandResponse(True, f'阿里云盘签到执行成功')


# 使用refresh_token更新access_token
def updateAccesssToken(queryBody, remarks):
    updateAccesssTokenURL = 'https://auth.aliyundrive.com/v2/account/token'
    headers = {'Content-Type': 'application/json'}
    errorMessage = [remarks, '更新 access_token 失败']
    response = requests.post(url=updateAccesssTokenURL, data=json.dumps(queryBody), headers=headers)
    jsonData = response.json()
    if 'code' in jsonData:
        if jsonData['code'] == 'RefreshTokenExpired' or jsonData['code'] == 'InvalidParameter.RefreshToken':
            errorMessage.append('refresh_token已过期或无效')
        else:
            errorMessage.append(jsonData['message'])
        raise Exception(','.join(errorMessage))
    else:
        return (jsonData['nick_name'], jsonData['refresh_token'], jsonData['access_token'])


# 执行签到
def signin(queryBody, access_token, remarks):
    signinURL = 'https://member.aliyundrive.com/v1/activity/sign_in_list'
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    sendMessage = [remarks]
    response = requests.post(url=signinURL, data=json.dumps(queryBody), headers=headers)
    jsonData = response.json()
    if not jsonData['success']:
        sendMessage.append('签到失败')
        raise Exception(','.join(sendMessage))
    else:
        try:
            sendMessage.append('签到成功')
            currentSignInfo = jsonData['result']['signInLogs'][jsonData['result']['signInCount'] - 1]
            sendMessage.append('本月累计签到 ' + str(jsonData['result']['signInCount']) + ' 天')
            if currentSignInfo['reward'] and (
                    'name' in currentSignInfo['reward'] or 'description' in currentSignInfo['reward']):
                sendMessage.append(
                    '本次签到获得' + (currentSignInfo['reward']['name'] if 'name' in currentSignInfo['reward'] else '') + (
                        currentSignInfo['reward']['description'] if 'description' in currentSignInfo['reward'] else ''))
            sendMessage_str = ','.join(sendMessage)
            logging.info(f'[aliyunpan_signin]:{sendMessage_str}')
            return sendMessage_str
        except Exception as e:
            sendMessage.append('但是解析签到信息失败，请去阿里云盘APP查看。')
            sendMessage_str = ','.join(sendMessage)
            logging.info(f'[aliyunpan_signin]:{sendMessage_str}')
            raise Exception(sendMessage_str)


# 获取refreshToken
def getRefreshToken():
    refreshTokenList = [r.strip() for r in refreshToken.split(',')]
    return refreshTokenList



# 定义Python的Generator（Python中Iterator的一种）
# 返回一个refresh_token，从环境变量refreshToken中解析
# 最终分离出每个refresh_token中的value值进行返回
def refreshTokenGenerator():
    for refreshToken_item in getRefreshToken():
        yield refreshToken_item


# 主程序
def main():
    messageList = []
    refreshTokenGen = refreshTokenGenerator()
    index = 1
    for refreshToken_item in refreshTokenGen:
        queryBody = {
            'grant_type': 'refresh_token',
            'refresh_token': refreshToken_item
        }
        try:
            remarks = '账号' + str(index)
            nick_name, refresh_token, access_token = updateAccesssToken(queryBody, remarks)
            if len(nick_name) > 0 and nick_name != remarks:
                remarks = nick_name + '(' + remarks + ')'
            message = signin(queryBody, access_token, remarks)
            messageList.append(message)
        except Exception as e:
            messageList.append(str(e))
        index += 1

    message_last = '\n'.join(messageList)
    send_notify('阿里云盘签到', message_last)


def set_token_secret():
    refreshToken_list = getRefreshToken()
    refreshToken_new_list = []
    for refreshToken_item in refreshToken_list:
        refreshToken_secret = re.sub(r'(?<=.{3}).(?=.{3})', '*', refreshToken_item)
        refreshToken_new_list.append(refreshToken_secret)
    refreshToken_str = ','.join(refreshToken_new_list)
    return refreshToken_str


def send_notify(title, content):
    channel_item = ToChannelName
    pic = 'https://s2.loli.net/2023/04/20/ySNZLnI3pQ6RvYb.jpg'
    if uid:
        for _ in uid:
            server.notify.send_message_by_tmpl('{{title}}', '{{a}}', {
                'title': title,
                'a': content,
                'pic_url': pic
            }, to_uid=_, to_channel_name=channel_item)
