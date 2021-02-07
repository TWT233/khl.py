# example 03 加点辣酱：指令参数

只会喊 world! 的机器人就和白米饭一样，确实有点单调，所以我们接下来的例程就讲讲怎么加点「调料」

这个例子讲的是最基础的「辣酱」：给你的指令加点参数

## 加辣酱时要怎么加？该加多少？可以拌进饭里吗？

要定义参数其实非常简单，看 `ex03.py` 的第 20~26 行：

```python
# register command
# invoke this via saying `!roll 1 100` in channel
# or `!roll 1 100 5` to dice 5 times once
@bot.command(name='roll')
async def roll(msg: TextMsg, t_min: str, t_max: str, n: str = 1):
    result = [random.randint(int(t_min), int(t_max)) for i in range(int(n))]
    await msg.reply(f'you got:{result}')
```

我们注册了一个 `roll` 指令，但是这次的函数参数除了 `TextMsg`，还有三个 `str`，这三个 `str` 就是指令参数

指令参数首先不限数量，其次可以带默认值，用以简化指令，后面会单独讲讲

## 尝尝辣酱辣不辣

这个 `roll` 指令是投骰子的小游戏，使用方法也很简单，在频道里喊 `!roll 1 100` 或 `!roll 1 100 5`（一次投五个）

在频道里喊指令的话，指令和参数、参数和参数之间用空格隔开即可

前两个参数 `t_min` `t_max` 分别是骰子范围的下上限，最后一个参数 `n` 是骰子个数

_小心！目前 khl.py 的指令参数都是 `str` 型的，所以要自己做转换，就像代码中的 `int(t_min)` 一样_

## 辣酱有点麻：默认参数

大家可能注意到了，最后一个参数 `n` 可有可无，原因是我们在代码中已经给 `n` 设好了默认值，所以不传也是可以的

大家也可以用这个方法来简化一些指令，

## 怪怪的辣椒酱：带空格的参数

前面有说过「参数和参数之间用空格隔开即可」，那如果我们就是要含空格的指令咋办呢？

**用英文引号引起来就行**

举例：

`!cmd a "b c"` 会被解析成「给 `cmd` 指令传**两个**参数：【`a`】、【`b c`】」

`!cmd a b c` 会被解析成「给 `cmd` 指令传**三个**参数：【`a`】、【`b`】、【`c`】」
