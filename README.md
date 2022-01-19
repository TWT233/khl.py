# khl.py

[![pypi version](https://img.shields.io/pypi/v/khl.py?label=latest&logo=pypi)](https://pypi.org/project/khl.py/)
![GitHub last commit](https://img.shields.io/github/last-commit/TWT233/khl.py?logo=github)

[![khl server](https://img.shields.io/badge/JOIN%20OUR%20CHAT-%23khl.py-blue)](https://kaihei.co/JJE0Es)
![github stars](https://img.shields.io/github/stars/TWT233/khl.py?style=social)

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


# register command, send `/hello` in channel to invoke
@bot.command(name='hello')
async def world(msg: Message):
    await msg.reply('world!')


# everything done, go ahead now!
bot.run()
# now invite the bot to a server, and send '/hello' in any channel
# (remember to grant the bot with read & send permissions)
```

For more example and tutorial, please turn to [example](./example)

# short-term roadmap

## feat

- [ ] helper function for apis
- [ ] card message(structure)

# CONTRIBUTION

welcome! we are glad to get help from community hands, and don't be shy to show your code, we can improve it together
even if it's not perfect right now

if there is any bug/perf/feature request, we are willing to deal with your issue/pull request!

the only red tape:

only accept commits satisfying [Conventional Commits convention](https://github.com/commitizen/cz-cli)

search plugins with keyword `commitizen` for your editor/IDE, then addict to write commit message