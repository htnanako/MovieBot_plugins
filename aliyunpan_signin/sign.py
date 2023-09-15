import httpx
import logging

from .utils import refreshTokenGenerator, updateAccesssToken, the_last_day, send_notify

logging = logging.getLogger("__adrive__")


class SignTask:
    def __init__(self):
        self.reward_enable = False
        self.uid = ''
        self.channel_item = ''
        self.refreshToken = ''

    def config(self,
               reward_enable,
               refreshToken,
               uid=None,
               channel_item=None
               ):
        self.reward_enable = reward_enable
        self.uid = uid
        self.channel_item = channel_item
        self.refreshToken = refreshToken

    # 执行签到
    def signin(self, refreshToken_item, access_token, remarks):
        signinURL = 'https://member.aliyundrive.com/v1/activity/sign_in_list'
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        queryBody = {
            "grant_type": "refresh_token",
            "refresh_token": refreshToken_item
        }
        sendMessage = [remarks]
        r = httpx.post(url=signinURL, json=queryBody, headers=headers)
        jsonData = r.json()
        if not jsonData['success']:
            sendMessage.append('签到失败')
            raise Exception(','.join(sendMessage))
        else:
            try:
                sendMessage.append('签到成功')
                sendMessage.append('本月累计签到 ' + str(jsonData['result']['signInCount']) + ' 天')
                if self.reward_enable:
                    rewardInfo = self.getReward(access_token, jsonData['result']['signInCount'])
                    sendMessage.append(f'本次签到获得{rewardInfo.get("name", "")}{rewardInfo.get("description", "")}')
                sendMessage_str = ','.join(sendMessage)
                logging.info(f'[aliyunpan_signin]:{sendMessage_str}')
                return sendMessage_str
            except Exception as e:
                sendMessage.append('但是解析签到信息失败，请去阿里云盘APP查看。')
                sendMessage_str = ','.join(sendMessage)
                logging.info(f'[aliyunpan_signin]:{sendMessage_str}')
                raise Exception(sendMessage_str)

    # 领取奖励
    def getReward(self, access_token, signInDay):
        rewardURL = "https://member.aliyundrive.com/v1/activity/sign_in_reward?_rx-s=mobile"
        headers = {
            "authorization": access_token,
            "Content-Type": "application/json"
        }
        data = {"signInDay": signInDay}
        r = httpx.post(rewardURL, headers=headers, json=data)
        jsonData = r.json()
        if not jsonData["success"]:
            raise Exception(jsonData["message"])
        return jsonData["result"]

    # 主程序
    def main(self):
        messageList = []
        refreshTokenGen = refreshTokenGenerator(self.refreshToken)
        for index, refreshToken_item in enumerate(refreshTokenGen):
            try:
                remarks = '账号' + str(index + 1)
                nick_name, refresh_token, access_token = updateAccesssToken(refreshToken_item, remarks)
                if len(nick_name) > 0 and nick_name != remarks:
                    remarks = nick_name + '(' + remarks + ')'
                message = self.signin(refreshToken_item, access_token, remarks)
                messageList.append(message)
            except Exception as e:
                messageList.append(str(e))

        message_last = '\n'.join(messageList)
        if not self.reward_enable and the_last_day():
            message_last += f'\n今天是月末了，记得去领奖励。'
        send_notify('阿里云盘签到', message_last, self.uid, self.channel_item)
