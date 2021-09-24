import json

from khl import Bot, Message, CommandRule

with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Bot
bot = Bot(token=config['token'])
# init Rule,bot param this is required
rule = CommandRule(bot)


# register command and add a rule
# invoke this via saying `/hello @bot_name` in channel
@bot.command(name='hello', rules=[rule.at_me()])
async def world(msg: Message, *args):
    await msg.reply('world!')


@bot.command(name='at_all', rules=[rule.at_all()])
async def yes(msg: Message, *args):
    await msg.reply('yes!')


# you can write a rule
def myrule1(msg: Message, *args, **kwargs):
    return msg.content.find('khl') != -1


def myrule2(param: str):
    def func(msg: Message, *args, **kwargs):
        return msg.content.find(param) != -1

    return func


# use rule1 or rule2, please try

@bot.command(name='testrule', rules=[myrule1])
# @bot.command(name='testrule', rules=[myrule2('khl')])
async def test(msg: Message, *args):
    await msg.reply('yes!')


# everything done, go ahead now!
bot.run()
