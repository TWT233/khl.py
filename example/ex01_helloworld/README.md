# example 01 Hello, World!

这节就开始做饭了，我们也自然是从简单开始，先来练练「白米饭」：

学代码不写 helloworld，就好比游北京不到长城，所以我们上手也是写个 helloworld

## 跑代码

样例代码已经写好了，就是这个文件夹中的 `ex01_helloworld.py`，我们先下载一下代码：

```shell
github clone https://github.com/TWT233/khl.py.git
cd khl.py/example
```

运行代码也很简单，不过要注意，别用错了 python 版本：

```shell
python ex01_helloworld/ex01_helloworld.py
```

正常来说，输出应该是这样的：

```shell
[INFO] 2021-02-06 19:32:09,340 @ khl.Bot(run): launching
[ERROR] 2021-02-06 19:32:09,586 @ khl.WebsocketClient(_main): error getting gateway: {'code': 401, 'message': '你的用户凭证不正确', 'data': {'name': 'Unauthorized', 'status': 401}}
[INFO] 2021-02-06 19:32:09,587 @ khl.Bot(run): see you next time
```

你看完可能就会说：哎，这机器人根本就没有跑起来啊，还报了个错，来看看报了什么错哈：「'code': 401, 'message': '你的用户凭证不正确'」喔，看起来好像是用户凭证的问题

没错，还记得我们在 ex00 里拿到的身份凭证吗？我们还没有把身份凭证填进代码里，所以服务器也不认识我们往这「锅」里加的是什么「米」，于是就返回了「你的用户凭证不正确」这个报错信息

## 填凭证

我们看到 `ex01_helloworld.py` 的第 3~4 行：

```python
# init Cert for Bot OAuth
cert = Cert(client_id='xxxxxxxx', client_secret='xxxxxxxx', token='xxxxxxxx')
```

把我们在 ex00 拿到的「Client Id」「Token」「Client Secret」对号入座填进去就 ok 了，注意用引号括起来

填完之后保存一下代码，然后我们再来一把：

```shell
python ex01_helloworld/ex01_helloworld.py
```

这个时候输出应该就只有一行：

```
[INFO] 2021-02-06 19:46:59,441 @ khl.Bot(run): launching
```

而且看起来程序还在运行，这就说明我们填凭证完成了，如果有问题的话检查一下身份凭证是不是填错了、python 版本对不对

## 怎么用

1. 把机器人拉到你的服务器里
   - 怎么拉？
     1. 在 [网页后台：开发者中心 - 机器人](https://developer.kaiheila.cn/bot/index) 中点进你的机器人面板
     2. 点左边的控制栏中的「设置」-「邀请」选项卡
     3. 这么多权限不知道咋选？上面的「消息权限」区四个全勾上、下面的单勾一个「管理员」就行，我们前期简单为主
     4. 把页面滚到最下面，复制「机器人邀请链接」，用浏览器打开，选择你要拉的服务器点击「邀请」即可
2. 点开你的服务器中的任意频道，看看右边的在线成员列表有没有你的机器人
3. **在聊天框里打 `!hello`**

看看你的机器人有没有回复你 `world!`，而且此时打开我们开着机器人的命令行，输出应该多了一条，长这样：

```shell
[INFO] 2021-02-06 19:59:05,187 @ khl.Bot(_text_handler): cmd triggered: hello with ['hello']
```

## 这饭咋做好的？

代码不长，我直接贴过来，用注释来说明每段代码的功能

```python
from khl import TextMsg, Bot, Cert

# 填凭证
cert = Cert(client_id='xxxxxxxx', client_secret='xxxxxxxx', token='xxxxxxxx')

# 新建机器人
# cmd_prefix 设定了机器人可识别的命令前缀
# cert 就是机器人和服务器通信所用到的凭证，刚刚填好的
bot = Bot(cmd_prefix=['!', '！'], cert=cert)


# 注册指令
# @ 是「装饰器」语法，大家可以网上搜搜教程，我们这里直接用就行
# bot 是我们刚刚新建的机器人，说明了这个指令是注册到 bot 中
# name 标示了指令的名字，名字也被用于触发指令，所以我们才能 !hello
# async def 说明这是一个异步函数，khl.py 是异步框架，所以指令也需要是异步的
# roll 是函数名，可以自选；第一个参数的类型固定为 TextMsg
@bot.command(name='hello')
async def roll(msg: TextMsg):
    # msg 指的是我们所发送的那句 `!hello`
    # 所以 msg.reply() 就是回复我们那句话，回复的内容是 `world!`
    await msg.reply('world!')


# 凭证传好了、机器人新建好了、指令也注册完了
# 接下来就是运行我们的机器人了，bot.run() 就是机器人的起跑线
bot.run()

```
