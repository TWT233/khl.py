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
@bot.command(name='hello', merge_args=True)
async def roll(msg: TextMsg, params: str):
    await msg.ctx.send_temp(f'you sent params is: "{params}"', msg.author.id)

# now you can send "!hello zhangsan lisi wangwu"

# everything done, go ahead now!
bot.run()
