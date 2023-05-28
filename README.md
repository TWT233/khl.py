# khl.py

[![pypi version](https://img.shields.io/pypi/v/khl.py?label=latest&logo=pypi)](https://pypi.org/project/khl.py/)
![GitHub last commit](https://img.shields.io/github/last-commit/TWT233/khl.py?logo=github)

[![khl server](https://www.kaiheila.cn/api/v3/badge/guild?guild_id=7236941486257903&style=3)](https://kaihei.co/JJE0Es)
![github stars](https://img.shields.io/github/stars/TWT233/khl.py?style=social)

Python SDK for [kookapp.cn](https://www.kookapp.cn/)(aka [kaiheila.cn](https://www.kaiheila.cn/)) API

# Minimal Example

```python
from khl import Bot, Message

# init Bot
bot = Bot(token='xxxxxxxxxxxxxxxxxxxxxxxxx')


# register command, send `/hello` in channel to invoke
@bot.command(name='hello')
async def world(msg: Message):
    await msg.reply('world!')


# everything done, go ahead now!
bot.run()
# now invite the bot to a server, and send '/hello' in any channel
# (remember to grant the bot with read & send permissions)
```

# INSTALL

requirement: Python >= 3.6.8

```shell
pip install khl.py
```

# Documentation

- [Guide](https://khl-py.eu.org/) (authored by [musnows](https://github.com/musnows))
- [Example](./example)
- [Wiki](https://github.com/TWT233/khl.py/wiki) (archived FAQ)

if your question has not been listed yet, please [create a issue](https://github.com/TWT233/khl.py/issues/new/choose)
or [join our talk channel](https://kaihei.co/JJE0Es) for help

# CONTRIBUTING

welcome! we are glad to get help from community hands, and don't be shy to show your code,
we can improve it together even if it's not perfect right now

if there is any bug/perf/feature request, we are willing to deal with your issue/pull request!
