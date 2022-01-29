import datetime
import json

from khl import Bot, Message
from khl.command import Rule

with open('../config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Bot
bot = Bot(token=config['token'])


# register command and add a rule
# invoke this via saying `/hello @{bot_name}` in channel
@bot.command(name='hello', rules=[Rule.is_bot_mentioned(bot)])
async def world(msg: Message, mention_str: str):
    await msg.reply(f'world! I am mentioned with {mention_str}')


@bot.command(rules=[Rule.is_mention_all])
async def yes(msg: Message, mention_str: str):
    await msg.reply(f'yes! mentioned all with {mention_str}')


# besides built-in rules in Rule.*, you can define your own rules
def my_rule(msg: Message) -> bool:
    return msg.content.find('khl') != -1


# this command can only be triggered with msg that contains 'khl' such as /test_mine khl-go
@bot.command(name='test_mine', rules=[my_rule])
async def test_mine(msg: Message, comment: str):
    await msg.reply(f'yes! {comment} can trigger this command')


# a example to combine decorator and rule
def is_contains(keyword: str):
    def func(msg: Message):
        return msg.content.find(keyword) != -1

    return func


# Q: how to trigger this command?
@bot.command(name='test_decorator', rules=[is_contains(str(datetime.date.today()))])
async def test_decorator(msg: Message, date: str):
    await msg.reply(f'yes! today is {date}')


# everything done, go ahead now!
bot.run()
