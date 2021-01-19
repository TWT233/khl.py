# khl.py

SDK for kaiheila.cn in python

# install

Python requirement: >= Python 3.6

```shell
pip install khl.py
```

# quickly enroll

```python
import random

from khl import TextMsg, Bot, Cert

cert = Cert(client_id='xxxxxx', client_secret='xxxxxx', token='xxxxxx')
bot = Bot(cmd_prefix=['!', '！'], cert=cert)


@bot.command(name='roll')
async def roll(session):
    await session.reply(f'{random.randint(int(session.args[0]), int(session.args[1]))}')


bot.run()
# now invite the bot to ur server,
# and type '!roll 1 100'(in any channel) to check ur san today!
# (remember to grant read & send permissions to the bot first)
```

# short-term roadmap

## docs:

- [x] docs init
- [x] detailed docstring

## perf:

- [x] check `SN`
- [ ] refactor `Msg`, support multimedia msg (active @TWT233)
    - [ ] introduce `MsgCtx` with this
- [ ] check

## feat:

### T1:

- [x] support websocket
- [ ] command & arg parse system
    - [x] sub command system (active @fi6 @TWT233)
- [ ] event listener for bot

### T2:

- [ ] log system
- [ ] `MsgCtx` design
- [ ] command alias

## bug fix:

- [x] error parsing str in `."` pattern (cmd_prefix+unclosing quote)

# commit message rules

only accept commits satisfying [Conventional Commits convention](https://github.com/commitizen/cz-cli)

search plugins with keyword `commitizen` for your editor/IDE, then addict to write commit message
