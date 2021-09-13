import json
from khl import Bot, Message, MessageRule

with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Bot
bot = Bot(token=config['token'])
# init Rule,now this is required
rule = MessageRule(bot)


# register command and add a rule
# invoke this via saying `/hello @bot_name` in channel
@bot.command(name='hello', rule=rule.at_me)
async def world(msg: Message, *args):
    await msg.reply('world!')

# everything done, go ahead now!
bot.run()
