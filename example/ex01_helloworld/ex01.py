from khl import TextMsg, Bot, Cert

# init Cert for Bot OAuth
cert = Cert(client_id='xxxxxxxx', client_secret='xxxxxxxx', token='xxxxxxxx')

# init Bot
bot = Bot(cmd_prefix=['!', '！'], cert=cert)


# register command
# invoke this via saying `!hello` in channel
@bot.command(name='hello')
async def roll(msg: TextMsg):
    await msg.reply('world!')


# everything done, go ahead now!
bot.run()
