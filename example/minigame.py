import copy, json, random, re

from khl import TextMsg, Bot, Cert

with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

cert = Cert(client_id=config['client_id'],
            client_secret=config['client_secret'],
            token=config['token'])

bot = Bot(cmd_prefix=['!', '！'], cert=cert)


@bot.command(name='24')
async def twenty_four(msg: TextMsg):
    cards = [random.randint(1, 13) for i in range(4)]
    await msg.reply(f'来一把紧张刺激的 24 点！输入算式进行推导，输入「退出」结束游戏')
    step = msg
    while len(cards) != 1 or cards[0] != 24:
        await step.reply(f'现在你手上有：{cards}，怎么凑 24 点呢？')
        step = await msg.ctx.wait_user(msg.author_id, timeout=30)
        if not step:
            return await msg.reply('超时啦！游戏结束！')
        if step.content == '退出':
            return await step.reply('这不再来一把？')
        if not re.match(r'[\d+\-*/]+', step.content):
            continue
        n_c = copy.deepcopy(cards)
        used = [int(i) for i in re.findall(r'\d+', step.content)]
        if 0 in map(lambda x: n_c.remove(x) if x in n_c else 0, used):
            await step.reply('有错误！')
        else:
            cards = n_c + [eval(step.content)]
    await step.reply('你赢啦！')


bot.run()
