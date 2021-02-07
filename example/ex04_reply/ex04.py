import json

from khl import TextMsg, Bot, Cert

# load config from config/config.json, replace `path` points to your own config file
# config template: `./config/config.json.example`
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Cert for Bot OAuth
cert = Cert(client_id=config['client_id'],
            client_secret=config['client_secret'],
            token=config['token'])

# init Bot
bot = Bot(cmd_prefix=['!', '！'], cert=cert)


# register command
# invoke this via saying `!hello` in channel
@bot.command(name='hello')
async def roll(msg: TextMsg):
    # quote reply
    await msg.reply('world for you!')
    # msg from reply_temp & send_temp will be cleaned when you restart client or refresh browser
    await msg.reply_temp('world only for you!')

    # send to current channel
    await msg.ctx.send('world for all!')
    # send to current channel, but only visible to `msg.author`
    # same as `msg.reply_temp()`, but can set `temp_target_id` explicitly
    await msg.ctx.send_temp('world only for you too!', msg.author.id)


# everything done, go ahead now!
bot.run()
