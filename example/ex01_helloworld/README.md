# example 01 Hello, World!

这节就开始做饭了，我们也自然是从简单开始，先来练练「白米饭」：

学代码不写 helloworld，就好比游北京不到长城，所以我们上手也是写个 helloworld

## 跑代码

样例代码已经写好了，就是这个文件夹中的 `ex01.py`，我们先下载一下代码：

```shell
git clone https://github.com/TWT233/khl.py.git
cd khl.py/example
```

运行代码也很简单，不过要注意，别用错了 python 版本：

```shell
python ex01_helloworld/ex01.py
```

正常来说，输出应该是这样的：

```shell
error getting gateway: {'code': 401, 'message': '你的用户凭证不正确', 'data': {'name': 'Unauthorized', 'status': 401}}
Task was destroyed but it is pending!
task: <Task pending coro=<Client.handle_pkg() running at D:\Coding\khl.py\khl\client.py:49> wait_for=<Future pending cb=[<TaskWakeupMethWrapper object at 0x000001A83316E528>()]>>
```

你看完是不是想说：哎，这机器人是不是没有跑起来啊，开头就是个 error。别急，我们来看看报了什么错哈：「'code': 401, 'message': '你的用户凭证不正确'」喔，看起来好像是用户凭证的问题

没错，还记得我们在 ex00 里拿到的「Token」吗？现在我们还没有把「Token」填进代码里传给服务器，所以服务器也不认识我们往这「锅」里加的是什么「米」，于是就返回了「你的用户凭证不正确」这个报错信息

## 填凭证

看到 `ex01.py` 的第 3~4 行：

```python
# init Bot
bot = Bot(token='xxxxxxxxxxxxxxxxxxxxxxxxx')
```

把我们在 ex00 拿到的「Token」填进去就 ok 了，注意用引号括起来哦，这是一个 `str` 类型

填完之后保存一下代码，然后我们再来一把：

```shell
python ex01_helloworld/ex01.py
```

如果正常启动，机器人是不会有输出的，因为我们的 helloworld 是一个最简单的 bot，所以没有输出启动信息

> 如果想看看具体情况的话，也可以增加日志输出：在代码中加入以下两行（在 `bot.run()` 前加就行）：
> ```python
> import logging
> logging.basicConfig(level='INFO')
> ```
> 期望输出：`INFO:khl.receiver:[ init ] launched`

如果有问题的话检查一下身份凭证是不是填错了、python 版本对不对，

> 当然也可以[加入我们的 khl 服务器](https://kaihei.co/JJE0Es) 来让大家帮你康康
>
> 不过大家也都知道，要提高做菜水平，总得自己多练才行

## 怎么用

1. 把机器人拉到你的服务器里
    - 怎么拉？
        1. 在 [网页后台：开发者中心 - 应用](https://developer.kaiheila.cn/app/index) 中点进你的应用，
        2. 转到「机器人」-「角色权限」选项卡
        3. 这么多权限？咋选？点这几个：『通用权限』区的「管理员」+『文字权限』区的六项
        4. 把页面滚到最下面，复制「机器人邀请链接」，用浏览器打开，选择你要拉的服务器点击「邀请」即可
2. 点开你的服务器中的任意频道，看看右边的在线成员列表有没有你的机器人（可能有延迟，要等一等）
3. **在聊天框里打 `/hello`**

看看你的机器人有没有回复你 `world!`，如果你在前面增加了日志输出，命令行里也会多一行输出，长这样：

```shell
INFO:khl.bot.command:command hello was triggered by msg: /hello
```

## 这饭咋做好的？

代码不长，我直接贴过来，用注释来说明每段代码的功能

```python
from khl import Bot, Message

# 新建机器人，token 就是机器人的身份凭证
bot = Bot(token='1/MTAwMDk=/Ejx6erC9Fo7C6JfuwkZ1iw==')


# 注册指令
# @ 是「装饰器」语法，大家可以网上搜搜教程，我们这里直接用就行
# bot 是我们刚刚新建的机器人，声明这个指令是要注册到 bot 中的
# name 标示了指令的名字，名字也被用于触发指令，所以我们 /hello 才会让机器人有反应
# async def 说明这是一个异步函数，khl.py 是异步框架，所以指令也需要是异步的
# world 是函数名，可以自选；函数第一个参数的类型固定为 Message
@bot.command(name='hello')
async def world(msg: Message):
    # msg 指的是我们所发送的那句 `/hello`
    # 所以 msg.reply() 就是回复我们那句话，回复的内容是 `world!`
    await msg.reply('world!')


# 凭证传好了、机器人新建好了、指令也注册完了
# 接下来就是运行我们的机器人了，bot.run() 就是机器人的起跑线
bot.run()
```
