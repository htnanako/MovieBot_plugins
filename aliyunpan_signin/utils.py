import datetime
import calendar
import logging

import httpx

from mbot.openapi import mbot_api

server = mbot_api

logging.getLogger("__adrive__")


def updateAccesssToken(refreshToken_item, remarks=None):
    updateAccesssTokenURL = 'https://auth.aliyundrive.com/v2/account/token'
    headers = {
        "Content-Type": "application/json"
    }
    queryBody = {
        "grant_type": "refresh_token",
        "refresh_token": refreshToken_item
    }
    errorMessage = [remarks, "更新 access_token 失败"]
    response = httpx.post(url=updateAccesssTokenURL, json=queryBody, headers=headers)
    jsonData = response.json()
    if 'code' in jsonData:
        if jsonData['code'] == 'RefreshTokenExpired' or jsonData['code'] == 'InvalidParameter.RefreshToken':
            errorMessage.append('refresh_token已过期或无效')
        else:
            errorMessage.append(jsonData['message'])
        raise Exception(','.join(errorMessage))
    else:
        return jsonData['nick_name'], jsonData['refresh_token'], jsonData['access_token']


def getRefreshToken(refreshToken):
    refreshTokenList = [r.strip() for r in refreshToken.split(',')]
    return refreshTokenList


def refreshTokenGenerator(refreshToken):
    for refreshToken_item in getRefreshToken(refreshToken):
        yield refreshToken_item


def send_notify(title, content, uid, channel_item):
    pic = 'https://nanako-1253183981.cos.ap-guangzhou.myqcloud.com/public-IMG/adrive.jpg'
    if uid:
        for _ in uid:
            server.notify.send_message_by_tmpl('{{title}}', '{{a}}', {
                'title': title,
                'a': content,
                'pic_url': pic
            }, to_uid=_, to_channel_name=channel_item)


def the_last_day():
    today = datetime.date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    if today.day == last_day:
        return True
    else:
        return False


def set_token_secret(refreshToken):
    refreshToken_list = getRefreshToken(refreshToken)
    refreshToken_new_list = []
    for refreshToken_item in refreshToken_list:
        refreshToken_secret = refreshToken_item[:6] + "***" + refreshToken_item[-6:]
        refreshToken_new_list.append(refreshToken_secret)
    refreshToken_str = ','.join(refreshToken_new_list)
    return refreshToken_str
