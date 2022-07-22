# 目录

1. [example 00 引言](#example-00-引言)
2. [example 01 Hello, World!](./ex01_helloworld)
3. [example 02 别把米洒了](./ex02_config_file)
4. [example 03 加点辣酱：指令参数](./ex03_cmd_args)
5. [example 04 好看的菜盘：向用户发消息的各种花活](./ex04_reply)
5. [example 05 开点小灶：事件处理](./ex05_event)
7. [example 06 来电话啦：条件消息](./ex06_add_rule)
8. [example 07 摆盘：卡片消息](./ex07_card_message)
9. [example 08 互动起来：消息回应](./ex08_add_reaction)
10. [example 09 快乐活动：在玩状态](./ex09_bot_status)

appendix. [Dive into khl.py: 设计 khl.py](./appendix_dive_into_khlpy)

# example 00 引言

首先欢迎大家来使用 [khl.py](https://github.com/TWT233/khl.py)！如果有兴趣的话，也非常欢迎大家来一起开发和维护`khl.py`

废话就不多说了，我们先来康康入门的准备工作有哪些：

## 准备点米：整个机器人

巧妇难为无米之炊，所以首先要做的事儿当然是整个机器人来啦，流程也很简单，只要三部

1. 准备一个 [kookapp.cn](https://www.kookapp.cn/) 的账号
2. 来 [服务器：「KOOK」开发者内测](https://kaihei.co/RzFIH8) 申请开发者内测权限
3. 在 [网页后台：开发者中心 - 应用](https://developer.kaiheila.cn/app/index) 创建一个应用，然后点开刚创建好的应用
    - 大家能在左侧的「设置」选项卡列表中看到一项「机器人」，点开它
    - 点开「机器人」选项卡后，就能看到机器人的信息以及「机器人连接模式」、「Token」两项重要选项
        - 「机器人连接模式」请设置为「websocket」，这是一种很好用的连接方式，且本教程前半段都不会讲 webhook
        - 「Token」是机器人的身份凭证，**请不要上传到任何地方 / 告诉其他人 / 直接写进代码 / 上传到代码托管平台**

## 准备口锅：搭个机器人的运行环境

巧妇有了，米有了，接下来就是要口锅来装米才行，而给 [khl.py](https://github.com/TWT233/khl.py) 用的「锅」也很好搭，两步即可：

1. 安装 python，版本号`>=3.6.8`即可
    - 为什么是 `3.6.8`？因为 centos7 能直接通过 epel 安装 `python 3.6.8`，所以 centos 选手也不需要从源码编译了，直接通过 epel 安装即可，很方便
2. 运行以下命令来安装 [khl.py](https://github.com/TWT233/khl.py)：

```shell
pip install khl.py
```

_注意：如果你的机器上同时有多个版本的 python，要注意别装到错误版本的 python 里了_

## 劈劈柴火：稍微了解一下 khl.py

我们下节 `example` 才会正式开始「做饭」，所以我们这里先简单地说说 [khl.py](https://github.com/TWT233/khl.py) 的特点，就当是准备点柴火和引子，方便大家之后「做起饭来」上手更快：

1. [khl.py](https://github.com/TWT233/khl.py) 是全异步的 API 框架
    - 异步是个啥？这个问题就不展开说了，大家可以百度/谷歌一下「异步 同步」，两者对照起来学比较快
2. [khl.py](https://github.com/TWT233/khl.py) 使用 [aiohttp](https://docs.aiohttp.org/en/stable/) 实现网络通信功能
    - 所以你可以直接让机器人用 `aiohttp` 来访问网站、获取资源，不需要再 `import requests` 了
    - `aiohttp` 也是全异步的网络框架，所以和我们的代码相性非常好
3. 有时间的话，还可以搜搜「python asyncio」，因为 [khl.py](https://github.com/TWT233/khl.py) 可以很自然地联动 `asyncio`，来实现一些很炫的东西

## 写在后面

现在巧妇有了米、有了锅、有了柴火，大家可以准备来写几段了

_talk is cheap, show me the code_

最开始的话当然还是 hello world 了，[example 01 Hello, World!](./ex01_helloworld)，我们走
