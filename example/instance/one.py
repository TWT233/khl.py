from khl import bot , Bot , Message , api #引入khl.py框架
from khl.card import CardMessage , Card , Module
import random
import os
import stat

bot = Bot(token="1/MTM2OTk=/kqk/pdBPJwDb3DJv4SJfOA==") #链接机器人

print("机器人已成功启动")
@bot.command(name="reg")
async def hep(msg : Message , o):
    hep = CardMessage(Card(Module.Header('用户:[ '+msg.author.nickname+' ]注册了一个社区账户'), Module.Section('请及时删除注册消息,以免账户被盗')))
    await msg.ctx.channel.send(hep) #输出提示信息
    print("用户[ "+msg.author.nickname+" ]执行了reg命令")
@bot.command(name="help")
async def hep(msg : Message): #注册/hel命令函数
    #await msg.ctx.channel.send("/help : 查询命令")
    #await msg.ctx.channel.send("/author : 查询作者") #输出提示信息
    hep = CardMessage(Card(Module.Header('命令'), Module.Section('/help (可添加参数): 获取帮助\n/author : 查询作者')))
    await msg.ctx.channel.send(hep) #输出提示信息
    print("用户[ "+msg.author.nickname+" ]执行了help命令")
@bot.command(name="author")
async def hep(msg : Message): #注册/author命令函数
    await msg.ctx.channel.send("该机器人由 @陆御 架构及建设") #输出提示信息
    print("用户[ "+msg.author.nickname+" ]执行了author命令")
@bot.command(name="poker")
async def hep(msg : Message , o): #注册/poker命令函数
    await msg.ctx.channel.send("卡牌游戏正在测试中!!!") #输出提示信息
	#生成玩家及AI的牌
	#玩家*6
    a = ['3','4','5','6','7','8','9','10','J','Q','K','A','2']
    b = ['3','4','5','6','7','8','9','10','J','Q','K','A','2']
    c = ['3','4','5','6','7','8','9','10','J','Q','K','A','2']
    d = ['3','4','5','6','7','8','9','10','J','Q','K','A','2']
    e = ['3','4','5','6','7','8','9','10','J','Q','K','A','2']
    f = ['3','4','5','6','7','8','9','10','J','Q','K','A','2']
    g = ['方块','梅花','红心','黑桃']
	#AI*1
    ms = ['3','4','5','6','7','8','9','10','J','Q','K','A','2']
    mk = ['方块','梅花','红心','黑桃']
	#随机生成玩家及AI的牌
	#玩家
    one = random.choice(a)
    wwo = random.choice(b)
    three = random.choice(c)
    four = random.choice(d)
    five = random.choice(e)
    six = random.choice(f)
    ######
    oe = random.choice(g)
    #AI
    seven = random.choice(ms)
    ######
    se = random.choice(mk)
    #判断条件
    if o == '1':
        if a.index(one) > ms.index(seven):
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
        elif a.index(one) < mk.index(se):
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
        else:
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                    await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("平局,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
    elif o == '2':
        if a.index(one) > ms.index(seven):
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
        elif a.index(one) < mk.index(se):
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
        else:
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("平局,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
    elif o == '3':
        if a.index(one) > ms.index(seven):
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
        elif a.index(one) < mk.index(se):
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
        else:
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("平局,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
    elif o == '4':
        if a.index(one) > ms.index(seven):
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
        elif a.index(one) < mk.index(se):
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
        else:
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("平局,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
    elif o == '5':
        if a.index(one) > ms.index(seven):
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
        elif a.index(one) < mk.index(se):
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
        else:
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("平局,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
    elif o == '6':
        if a.index(one) > ms.index(seven):
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
        elif a.index(one) < mk.index(se):
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
        else:
            if g.index(oe) > mk.index(se):
                await msg.ctx.channel.send("你赢了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            elif g.index(oe) < mk.index(se):
                await msg.ctx.channel.send("你输了,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
            else:
                await msg.ctx.channel.send("平局,你的牌是["+oe+one+"],我的牌是["+se+seven+"]")
    else:
        await msg.ctx.channel.send("参数值错误")
    print("用户[ "+msg.author.nickname+" ]执行了poker命令")

bot.run() #启动/启动机器人
