[> 加入我们的 khl 服务器 | Join our server on khl](https://kaihei.co/JJE0Es)

# khl.py

Python SDK for [kaiheila.cn](https://www.kaiheila.cn/) API

# install

Python requirement: >= Python 3.6

```shell
pip install khl.py
```

# quickly enroll

Minimal example:

```python
from khl import Bot, Message

# init Bot
bot = Bot(token='xxxxxxxxxxxxxxxxxxxxxxxxx')


# register command
# invoke this via saying `/hello` in channel
@bot.command(name='hello')
async def world(msg: Message):
    await msg.reply('world!')


# everything done, go ahead now!
bot.run()
# now invite the bot to a server, and type '/hello'(in any channel)
# (remember to grant the bot with read & send permissions)
```

For more example and tutorial, please turn to [example](./example)

## notes for Mac OSX users:

if you encounter this error:

```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1123)
```

please install certificate manually, turning to this post for guide:

[certificate verify failed: unable to get local issuer certificate](https://stackoverflow.com/a/58525755)

# short-term roadmap

## feat

- regex lexer
- bot.on_event()
- helper function for apis

# commit message rules

only accept commits satisfying [Conventional Commits convention](https://github.com/commitizen/cz-cli)

search plugins with keyword `commitizen` for your editor/IDE, then addict to write commit message
