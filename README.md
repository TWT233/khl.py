# khl.py

SDK for kaiheila.cn in python

# install

Python requirement: >= Python 3.6

```shell
pip install khl.py
```

# quickly enroll

```python
from khl import TextMsg, Bot, Cert

# init Cert and Bot
cert = Cert(client_id='xxxxxxxx', client_secret='xxxxxxxx', token='xxxxxxxx')
bot = Bot(cmd_prefix=['!', '！'], cert=cert)


@bot.command(name='hello')
async def roll(msg: TextMsg):
    await msg.reply('world!')


bot.run()
# now invite the bot to ur server,
# and type '!hello'(in any channel) to check ur san today!
# (remember to grant read & send permissions to the bot first)
```

## notes for Mac OSX users:

if you encounter this error:

```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1123)
```

please install certi manually, turning to this post for guide:

[certificate verify failed: unable to get local issuer certificate](https://stackoverflow.com/a/58525755)

# short-term roadmap

## refactor

### T1:

- [ ] btn handler(ongoing)

### T2:

- [x] rename files according to PEP8
- [ ] wrap functions for convenient

## perf:

- [ ] refactor `Msg`, support multimedia msg (active @TWT233)
    - [x] introduce `MsgCtx` with this

## feat:

### T1:

- [x] `on_textMsg()`
- [ ] command & arg parse system(long term design needed)
- [x] event listener for bot
    - [x] find another approach to handle msg
    - [x] utilize event listener
- [x] add get for net client
- [x] command group
- [ ] upload assets
- [ ] event class(interface)

### T2:

- [x] log system
- [x] `MsgCtx` design
- [x] command alias
- [ ] bot send args (done by @fi6, waiting for merge)
- [ ] no prefix commands
    - [ ] fix `cmd_prefix=[]`
- [ ] more kinds of msg
- [ ] action result

# commit message rules

only accept commits satisfying [Conventional Commits convention](https://github.com/commitizen/cz-cli)

search plugins with keyword `commitizen` for your editor/IDE, then addict to write commit message
