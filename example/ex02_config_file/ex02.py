import json

from khl import Message, Bot

# load config from config/config.json, replace `path` to your own config file
# config template: `./config/config.json.example`
with open('../config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Bot
bot = Bot(token=config['token'])


# register command
# invoke this via saying `/hello` in channel
@bot.command(name='hello')
async def world(msg: Message):
    await msg.reply('world!')


# everything done, go ahead now!
bot.run()
