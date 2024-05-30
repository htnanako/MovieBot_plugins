<center><img src="https://raw.githubusercontent.com/htnanako/MovieBot_plugins/main/notify_api/logo.png"  alt=""/></center>


## 通知调度中心

> 基于MovieBot插件系统实现的通知调度中心。

### 使用

#### 一、下载本插件

- 下载本插件，将notify_api文件夹拷贝到插件目录。
- 前端部分仅需要拷贝/notify_api/frontend/dist -> /plugins/notify_api/frontend/dist
- 重启MovieBot

#### 二、配置通道

- 重启后即可在程序左侧菜单看到 `通知API` 菜单项。
- 点击添加，输入相关配置信息
    - 名称: 输入一个你自己可分辨的名称，仅作为展示用。
    - 推送用户: 调用此通道时要推送给的用户。
    - 推送渠道: 调用此通道时要推送的通知渠道。
    - 推送图片: 调用此通道时默认使用的图片，可使用随机图接口地址，此配置项可被外部调用覆盖。

#### 三、调用示例

url: `/api/plugins/notifyapi/send_notify`

Method: `GET` & `POST` 均支持

鉴权: 使用MovieBot自带的 `access_key` 鉴权方式，调用时请携带 `access_key` 参数在params

请求参数： 
`GET` 请求时参数配置在params， `POST` 请求时参数配置在body。

| 参数名 | 值类型 | 描述 |
|:------------:|:--------------:|:-------------:|
| id | String/Int | 推送通知的ID,可从前端页面展示中获取 |
| title | String | 推送通知的标题 |
| content | String | 推送通知的内容 |
| pic_url | String | 推送使用的图片。如果携带此参数，则优先使用此参数值，可不传 |
| link_url | String | 通知跳转链接，仅企业微信支持，可不传 |


调用参考：

`GET`请求：

```shell
curl --request GET \
  --url 'http://127.0.0.1:1329/api/plugins/notifyapi/send_notify?id=1&title={title}&content={content}&pic_url={pic_url}&link_url={link_url}&access_key={access_key}'
```

```Python
import requests

url = "http://127.0.0.1:1329/api/plugins/notifyapi/send_notify"

querystring = {
    "id": "1",
    "title": "title",
    "content": "content",
    "pic_url": "pic_url",
    "link_url": "link_url",
    "access_key":"access_key"
}

response = requests.request("GET", url, params=querystring)

print(response.text)
```

`POST`请求

```shell
curl --request POST \
  --url 'http://127.0.0.1:1329/api/plugins/notifyapi/send_notify?access_key=access_key' \
  --header 'Content-Type: application/json' \
  --data '{
  "title": "title",
  "content": "content",
  "pic_url": "pic_url",
  "link_url": "link_url"
  "id": 1
}'
```

```Python
import requests

url = "http://127.0.0.1:1329/api/plugins/notifyapi/send_notify"

querystring = {
    "access_key":"access_key"
}

payload = {
    "title": "title",
    "content": "content",
    "pic_url": "pic_url",
    "link_url": "link_url"
    "id": 1
}
headers = {"Content-Type": "application/json"}

response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

print(response.text)
```