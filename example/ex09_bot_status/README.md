# example 09 快乐活动：在玩状态

KOOK更新了在玩状态的api接口，允许我们给bot上一个`在玩`状态，和用户打游戏的时候显示的游戏状态一样。

本exp便是一个给bot上在玩状态的教程

>文档：https://developer.kaiheila.cn/doc/http/game



## 1.打游戏！

要想让bot和我们一起玩上游戏，首先我们需要获取对应游戏的id

见`ex09.py`的`L13-20`，这里我们从官方那儿获取到已有游戏名和id。因为这个列表已经很长了，所以我们就不让bot进行reply，而是直接在控制台打印输出。

打印的一部分示例如下：
```
game_name: 英雄与将军 -- game_id: 363871
game_name: 全面战争：三国 -- game_id: 363876
game_name: 终极将军：内战 -- game_id: 363878
game_name: Goose Goose Duck -- game_id: 385090
game_name: 战机：二战空战英雄 -- game_id: 385091
game_name: Natural Selection 2 -- game_id: 385103
```

你可以在列表里面查找有没有你想给bot上的游戏的id。如果有，那就太好了！

### 1.1 给bot上游戏动态

见`L33-37`，直接将id给我们的bot传过去，bot就会开始玩这个id对应的游戏啦！
```python
# use game_id to set bot gaming status
@bot.command()
async def gaming(msg: Message, game_id: int):
    # game_id : int
    await bot.client.update_playing_game(game_id)
    await msg.reply('gaming!')
```

### 1.2 手动创建一个游戏

如果你想让bot玩的游戏没有在列表中，那么我们就需要自己创建一个游戏

见`L23-30`，这里我们调用官方提供的接口，传入游戏名（name）和游戏图标（icon）参数，创建出一个对应的游戏。在最后的`print`会打印一个游戏对象的值，其中包含了游戏名和游戏id。

```
game_name: 人类一败涂地 -- game_id: 465201
```

有了id之后，就可以用上面的方法让bot玩上这个游戏啦！

----

## 2.听音乐！

除了玩游戏，bot还可以听歌呢！

见`L41-48`，这里我们只需要传入音乐名和歌手名，就可以让bot听歌啦！

其中音乐软件是一个枚举值，目前官方提供了3种音乐软件（对应显示的logo不同），分别为网易云、qq音乐、酷狗音乐。你可以根据自己的喜好进行修改。
```python
# set bot music status
@bot.command()
async def music(msg: Message, music: str, singer: str):
    # music name : str
    # singer name : str
    # music_software : Enum ['cloudmusic'、'qqmusic'、'kugou'], 'cloudmusic' in default
    await bot.client.update_listening_music(music, singer, "qqmusic")
    await msg.reply('listening to music!')
```

## 3.让bot休息一下

玩了那么久游戏，不休息一下咋行？

见`L51-58`，这里让bot休息被分为了两种情况，1代表游戏，2代表听音乐。只需要操作这个指令的时候添加一个参数d，即可让bot休息下来哦！
```python
# delete bot status
@bot.command()
async def stop(msg: Message, d: int):
    if d == 1:
        await bot.stop_playing_game()
    elif d == 2:
        await bot.stop_listening_music()
    await msg.reply('stop')
```

好啦，快去试试给bot加上这个新功能吧！