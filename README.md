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

## docs

- [ ] examples & tutorials (active @TWT233)
- [ ] docstring (v0.0.10)

## perf:

- [ ] refactor `Msg`, support multimedia msg (active @TWT233)
  - [ ] add kinds of multimedia msg (v0.0.10)
- [ ] async bot.run() (v0.0.11)

## feat:

### T1:

- [ ] new events, new handler system (v0.0.10)
- [ ] upload assets (v0.0.10)
- [ ] no prefix commands (v0.0.10)
  - [ ] fix `cmd_prefix=[]`

### T2:

- [ ] bot send args (done by @fi6, waiting for merge)
  - [ ] needs more practice and design
- [ ] command & arg parse system(long term design needed)
- [ ] event class(interface)

# commit message rules

only accept commits satisfying [Conventional Commits convention](https://github.com/commitizen/cz-cli)

search plugins with keyword `commitizen` for your editor/IDE, then addict to write commit message
