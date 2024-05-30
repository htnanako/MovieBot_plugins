<center><img src="https://raw.githubusercontent.com/htnanako/MovieBot_plugins/main/emby_notify/logo.jpg"  alt=""/></center>


## Emby事件通知

> 基于MovieBot插件系统实现的Emby事件通知插件。

> 本插件在 `多吃点` dalao的插件基础上修改

### 使用

#### 一、下载本插件

- 下载本插件，将emby_notify文件夹拷贝到插件目录。
- 重启MovieBot

#### 二、配置信息

- 重启后进行插件配置，只需要配置推送用户和能让Emby访问到的MovieBot地址
- 如需指定推送通道，配置完成后重启，插件会自动在Emby的通知配置中新增一个Webhook地址，将地址添加一个`to_channel_name`参数，参数值为MovieBot中配置的推送通知通道名称。

#### 三、通知格式

以下为插件配置的默认通知格式，如需自定义可自行修改，格式遵循[Jinja2](https://docs.jinkan.org/docs/jinja2/)语法

- 播放开始标题
```jinja2
{{user}}开始播放 {{title}}{%if year%}({{year}}){%endif%}
```

- 播放开始内容
```jinja2
{%if progress_text%}{{progress_text}}
{%endif%}{{container}} · {{video_stream_title}}
⤷{{transcoding_info}} {{bitrate}}Mbps{%if current_cpu%}
⤷CPU消耗：{{current_cpu}}%{%endif%}
来自：{{server_name}}
大小：{{size}}
设备：{{client}} · {{device_name}}{%if genres%}
风格：{{genres}}{%endif%}{%if intro%}
简介：{{intro}}{%endif%}
```

- 播放停止标题
```jinja2
{{user}}停止播放 {{title}}{%if year%}({{year}}){%endif%}
```

- 播放停止内容
```jinja2
{%if progress_text%}{{progress_text}}
{%endif%}{{container}} · {{video_stream_title}}
⤷{{transcoding_info}} {{bitrate}}Mbps{%if current_cpu%}
⤷CPU消耗：{{current_cpu}}%{%endif%}
来自：{{server_name}}
大小：{{size}}
设备：{{client}} · {{device_name}}{%if genres%}
风格：{{genres}}{%endif%}{%if intro%}
简介：{{intro}}{%endif%}
```

- 电影入库标题
```jinja2
🍟 新片入库： {{title}} {%if release_year%}({{release_year}}){%endif%}
```

- 电影入库内容
```jinja2
🍟 {{server_name}}
入库时间: {{created_at}}{%if genres%}

风格：{{genres}}{%endif%}
大小：{{size}}{%if intro%}
简介：{{intro}}{%endif%}
```

- 剧集入库标题
```jinja2
📺 新片入库： {{title}}
```

- 剧集入库内容
```jinja2
📺 {{server_name}}
入库时间: {{created_at}}
{%if episode_title%}
单集标题：{{episode_title}}{%endif%}{%if series_genres%}
风格：{{series_genres}}{%endif%}
大小：{{size}}{%if intro%}
简介：{{intro}}{%endif%}
```

#### 四、可用变量

> 注意：部分参数仅剧集可用，部分参数仅播放通知可用，自行鉴别。

|         变量         |   描述   |       备注        |
|:------------------:|:------:|:---------------:|
|    server_name     |  服务器名  |
|       title        |   标题   | 如果是剧集，自动增加季度和集数 |
|        year        |   年份   |
|   season_number    |   季度   |
|   episode_number   |   集数   |
|   episode_title    |  集标题   |
|        user        |  用户名   |
|     container      |   容器   |
| video_stream_title | 视频流标题  |
|  transcoding_info  |  转码信息  |
|    current_cpu     | 当前CPU  |
|      bitrate       |   码率   |
|        size        |   大小   |
|       client       |  客户端   |
|    device_name     |  设备名   |
|      pic_url       |  图片链接  |
|      link_url      | 推送跳转链接 |
|   progress_text    |  进度文本  |
|       genres       |   风格   |
|   series_genres    |  剧集风格  |
|       intro        |   简介   |
|     created_at     |  创建时间  |

