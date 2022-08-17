import json

from khl import Bot, Message

with open('../config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Bot
bot = Bot(token=config['token'])


# doc: https://developer.kaiheila.cn/doc/http/game
# fetch current game list from kook
# find the game you want to add in this list
@bot.command(name='list')
async def list_game(_: Message):
    ret = await bot.client.fetch_game_list()
    for g in ret:
        print(f"game_name: {g.name} -- game_id: {g.id}")


# if the game you want is not in the list
# you can create name by yourself
# name : str
# icon : str (the url of icon picture)
@bot.command(name='create')
async def create_game(_: Message):
    ret = await bot.client.register_game(name="人类一败涂地",
                                         icon="https://img.kookapp.cn/assets/2022-07/rQLmLHHWF409q09q.png")
    print(f"game_name: {ret.name} -- game_id: {ret.id}")


# use game_id to set bot gaming status
@bot.command()
async def gaming(msg: Message, game_id: int):
    # game_id : int
    await bot.client.update_playing_game(game_id)
    await msg.reply('gaming!')


# set bot music status
@bot.command()
async def music(msg: Message, music_name: str, singer: str):
    # music name : str
    # singer name : str
    # music_software : Enum ['cloudmusic'、'qqmusic'、'kugou'], 'cloudmusic' in default
    await bot.client.update_listening_music(music_name, singer, "qqmusic")
    await msg.reply('listening to music!')


# delete bot status
@bot.command()
async def stop(msg: Message, d: int):
    if d == 1:
        await bot.client.stop_playing_game()
    elif d == 2:
        await bot.client.stop_listening_music()
    await msg.reply('stop')


# everything done, go ahead now!
bot.run()
