# example 06 挑食

## rule

添加规则用来设置在什么情况下会触发函数,例如@机器人,或者只有特定频道,角色才会触发

示例中的用例都十分简单

## 使用示例


可以自定义rule,但是必须是异步函数,返回值为True
```python
async def simple_rule(msg: Msg, *args) -> bool:
    if msg.content.find("bot"):
        return True
    return False
```


也可以直接调用Rule中编写好的规则
```python
from khl import Rule

@bot.command(name='hello', rule=Rule.at_me())
async def roll(msg: TextMsg, *args):
    await msg.reply(f'hello')
```