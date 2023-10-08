# Changelog

## 1.0.0 (2023-10-08)


### Features

* add mbot_command_api ([c3c5bda](https://github.com/htnanako/MovieBot_plugins/commit/c3c5bda49a2d0e673f8a1e908b72714a2bc8add6))
* 使用AiProxy时支持上下文记忆，升级后在设置中配置上下文数量。使用AiProxy时支持上下文记忆，升级后在设置中配置上下文数量。 ([96856ec](https://github.com/htnanako/MovieBot_plugins/commit/96856ec983a95ff3fa8035001bc8e07e0f47808a))
* 去掉16k模型，新增0613模型供选择 ([73cab6c](https://github.com/htnanako/MovieBot_plugins/commit/73cab6cbb99ec7656d562ad691b3b0b0c6cfb540))
* 增加max_tokens限制，避免内容过长被企微截断 ([73cab6c](https://github.com/htnanako/MovieBot_plugins/commit/73cab6cbb99ec7656d562ad691b3b0b0c6cfb540))
* 增加配置检测。 ([9923106](https://github.com/htnanako/MovieBot_plugins/commit/9923106dea465f1d97bf512b3e256a2c6c8939c4))
* 增加重启及清除通知按钮 ([fd716a5](https://github.com/htnanako/MovieBot_plugins/commit/fd716a592aa5021f5afd034b8d0d9287fe97be4a))
* 重构代码。定时清理小雅转存盘。 ([eebc946](https://github.com/htnanako/MovieBot_plugins/commit/eebc946e51972b617b108cf6df29f15ca6a6fb06))


### Bug Fixes

* 上下文数量不填写或填写0，不再将本次对话记录到上下文中。 ([67c1ee2](https://github.com/htnanako/MovieBot_plugins/commit/67c1ee20929e4c754b49afb1ea53ca392e15da14))
* 优化chatbot报错提示 ([5246907](https://github.com/htnanako/MovieBot_plugins/commit/524690773f6523324790aeb204847db1c47757a9))
