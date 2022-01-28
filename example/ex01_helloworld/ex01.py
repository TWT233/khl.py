from khl import Bot, Message

# init Bot
bot = Bot(token='xxxxxxxxxxxxxxxxxxxxxxxxx')


# register command
# invoke this via saying `/hello` in channel
@bot.command(name='hello')
async def world(msg: Message):  # when `name` is not set, the function name will be used
    await msg.reply('world!')


# everything done, go ahead now!
bot.run()
