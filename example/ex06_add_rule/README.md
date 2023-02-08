# example 06 来电话啦：条件消息

在使用机器人的时候，有时候需要处理一些特定条件下的消息

让我们看看在来「电话」时，机器人怎么识别这些条件吧！

## 打给你的电话：at机器人

看`exp06.py`14-18行，这是最基本的打给机器人的电话（即@机器人）

~~~~python
# register command and add a rule
# invoke this via saying `/hello @{bot_name}` in channel
@bot.command(name='hello', rules=[Rule.is_bot_mentioned(bot)])
async def world(msg: Message, mention_str: str):
    await msg.reply(f'world! I am mentioned with {mention_str}')
~~~~

当有人键入`/hello @机器人`时，机器人会回复`world! I am mentioned with @机器人`。

`{mention_str}`作为第二个参数，指代的是我们@的对象

你只需要修改`name`和`reply`，即可自定义触发这条指令的条件以及内容

## 打给别人的电话：at其他人

除了接听打给自己的电话，机器人还可以看到你打电话给别人

~~~python
@bot.command(rules=[Rule.is_mention_all])
async def yes(msg: Message, mention_str: str):
    await msg.reply(f'yes! mentioned all with {mention_str}')
~~~

`Rule.is_mention_all`指代任何用户被@提及

当你使用`/yes @用户A`时，机器人便会回复`yes! mentioned all with @用户A`

## 窥探聊天内容：找寻关键字

除了上面这两个已经内置的rules，你还可以自定义自己的rules

~~~python
# besides built-in rules in Rule.*, you can define your own rules
def my_rule(msg: Message) -> bool:
    return msg.content.find('khl') != -1


# this command can only be triggered with msg that contains 'khl' such as /test_mine khl-go
@bot.command(name='test_mine', rules=[my_rule])
async def test_mine(msg: Message, comment: str):
    await msg.reply(f'yes! {comment} can trigger this command')
~~~

上面这个rules的触发条件为，有人键入`/test_mine`，且后面的消息中包含了`khl`这个字符串

如`/test_mine khl-go`，机器人会回复`yes! khl-go can trigger this command`

## 窥探特定的内容：制作你自己的规则

看`exp06.py`的37-48行，这里给出了一个自定义规则的示例

当你键入`/test_decorator 2022-06-23`，机器人会回复`yes! today is 2022-06-23`

必须要是当天日期，机器人才会回复你哦

当然，如果你键入的日期规则不准确（比如2022-6-23），机器人也不会理你的
