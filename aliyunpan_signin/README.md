## 阿里云盘每日签到

> 基于MovieBot插件系统实现的阿里云盘签到。

### 使用

#### 一、获取 refresh_token

- 自动获取: 登录[阿里云盘](https://www.aliyundrive.com/drive/)后，控制台粘贴 `JSON.parse(localStorage.token).refresh_token`
  ![](./assets/refresh_token_1.png)

- 手动获取: 登录[阿里云盘](https://www.aliyundrive.com/drive/)后，可以在开发者工具 ->
  Application -> Local Storage 中的 `token` 字段中找到。  
  注意：不是复制整段 JSON 值，而是 JSON 里 `refresh_token` 字段的值，如下图所示红色部分：
  ![refresh token](https://raw.githubusercontent.com/mrabit/aliyundriveDailyCheck/master/assets/refresh_token_2.png)

#### 二、下载本插件，解压后拷贝到MovieBot插件目录

#### 三、重启MovieBot，进入插件管理，配置refreshToken
