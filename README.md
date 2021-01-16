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

from khl import TextMsg, Bot
from khl.webhook import Cert, WebhookClient

cert = Cert(client_id='xxxxxx', client_secret='xxxxxx', token='xxxxxx', verify_token='xxxxxx')

bot = Bot(cmd_prefix=['!', '！'], net_client=WebhookClient(cert=cert, compress=True))


@bot.command(name='roll')
async def roll(msg: TextMsg):
    await bot.send(msg.target_id, f'you got: {random.randint(1, 6)}')


bot.run()
```

## Why `WebhookClient`

There will be multiple ways for Bots to connect to kaiheila.cn, such as Webhook mentioned above, and WebSocket which is
still WIP

Thus, to make our code easily comprehended and maintained in the future, we choose to leave WebhookClient here, though
there is only Webhook now.

# short-term roadmap

## docs:

- [x] docs init
- [x] detailed docstring

## perf:

- [x] check `SN`

## feat:

### T1:

- [ ] support websocket (active @TWT233)
- [ ] command & arg parse system
    - [ ] sub command system (active @fi6)

### T2:
- [ ] log system
- [ ] `MsgCtx` design
- [ ] command alias

## bug fix:

- [x] error parsing str in `."` pattern (cmd_prefix+unclosing quote)

# commit message rules

only accept commits satisfying [Conventional Commits convention](https://github.com/commitizen/cz-cli)

search plugins with keyword `commitizen` for your editor/IDE, then addict to write commit message