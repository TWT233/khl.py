import json

from khl import Bot, Message

# load config from config/config.json, replace `path` to your own config file
# config template: `./config/config.json.example`
with open('../config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Bot
bot = Bot(token=config['token'])


# register command
# invoke this via saying `!hello` in channel
@bot.command(name='hello')
async def world(msg: Message):
    # quote reply
    await msg.reply('world for you!')
    # msg from reply_temp & send_temp will be cleaned when you restart client or refresh browser
    await msg.reply('world only for you!', is_temp=True)

    # send to current channel
    await msg.ctx.channel.send('world for all!')
    # send to current channel, but only visible to `msg.author`
    # same as `msg.reply_temp()`, but can set `temp_target_id` explicitly
    await msg.ctx.channel.send('world only for you too!', temp_target_id=msg.author.id)


# everything done, go ahead now!
bot.run()
