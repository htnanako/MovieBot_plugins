## 企业微信ChatBot插件

> 基于MovieBot插件系统实现的企业微信ChatBot。

> 目前支持OpenAI官方接口及AiProxy接口。仅AiProxy接口支持上下文，请在设置中配置上下文数量。

### 使用

#### 一、获取相关参数

- 代理：如果选择OpenAI，请保证容器所在网络可以访问，不然需要配置代理。如果选择AiProxy，则无需代理。
- 模型：目前通用聊天模型只有gpt-3.5-turbo及gpt-4,以及gpt-3.5-turbo-16k，可支持更大的回复tokens。
- api_key：根据你选择的服务提供商，获取对应的api_key填入。不同服务提供商的api_key不可混用。
- 如果使用AiProxy，可支持Bing和Google搜索，具体查看[官方文档](https://docs.aiproxy.io/product/search)。

- 企业微信信息，和消息推送通道同样的获取方式，需要单独一个应用，不可与推送通道混用应用
- 接收消息服务器地址：`http://域名:外网端口/api/plugins/qywx_chatbot/chat`

- 相关信息填写或者修改保存后即刻生效，无需重启容器。

#### 二、下载本插件，解压后拷贝到MovieBot插件目录

#### 三、重启MovieBot，进入插件管理，配置相关信息。