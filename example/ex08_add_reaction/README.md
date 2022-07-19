# example 08 互动起来：消息回应

在之前的[exp05](../ex05_event)中，我们知道bot可以处理一些`Event`事件

在[interface.py](../../khl/interface.py)中，你可以看到更多`EventTypes`的具体事件。

其中，消息回应涉及到的事件是`ADDED_REACTION`

## 观测回应：设置evnet事件

看`ex08.py`的13-15行，这里我们设置了bot去观测事件`ADDED_REACTION`

~~~python
@bot.on_event(EventTypes.ADDED_REACTION)
async def reaction_reminder(b:Bot,event:Event):
~~~

在观测到用户给某一条消息添加回应后，bot会发送一条消息，告知用户添加了表情回应

~~~python
    # fetch channel of the REACTION event
    channel = await b.fetch_public_channel(event.body['channel_id']) 
    # send a messge to inform user at current channel
    await b.send(channel,f"you add reaction{event.body['emoji']['id']}") 
~~~

建议先使用`print(event.body)`了解`event.body`的结构。当然，你还可以去阅读官方API文档[【频道相关事件】](https://developer.kaiheila.cn/doc/event/channel#%E9%A2%91%E9%81%93%E6%B6%88%E6%81%AF%E6%9B%B4%E6%96%B0)来了解这部分内容。

* 22年6月下旬KOOK统一了emoji显示的格式，修复了同一个emoji会有两个`['emoji']['id']`的BUG。

~~~
{'channel_id': '添加回应的文字频道id', 'emoji': {'id': '💜', 'name': '💜'}, 'user_id': '添加回应的用户id', 'msg_id': '添加了回应的消息id'}
~~~

## 添加角色：通过特定emoji为用户添加特定角色

了解了上面的event方式后，你现在可以让机器人来为用户添加角色。这在一些服务器的“上色频道”中非常好用。

既然要让机器人根据emoji添加不同的角色，首先我们需要制作一个emoji和角色对应的`card messgae`

~~~python
@bot.command()
async def RoleSet(msg:Message):
    cm = CardMessage()
    c1 = Card(Module.Header('Add reaction to get a role for yourself!'), Module.Context('Waiting for more roles...'))
    c1.append(Module.Divider())
    c1.append(Module.Section('「:pig:」test1  「:tiger:」test2\n'))
    cm.append(c1)
    await msg.ctx.channel.send(cm)
~~~

需要注意的是，`['emoji']['id']`和KOOK所用emoji网站[Webfx](https://www.webfx.com/tools/emoji-cheat-sheet/#)上的编号有所不同。如果想让机器人发送的消息里面包含emoji，需要使用`Webfx`网站上的编号；而如果想实现判断用户回应的emoji，则需要使用`event.body["emoji"]['id']` 

> 最好的办法当然是用`print`把卡片消息中包含的emoji对应的`event.body["emoji"]['id']`打印出来

当我们知道了回应表情的`['emoji']['id']`和服务器的角色ID(`role_id`)后，就可以在用户给这条卡片消息添加回应后，让机器人根据回应表情的`['emoji']['id']`来设置不同的角色

---

看`ex08.py`的30-41行，在设置角色之前，我们先要通过Bot获取服务器id，返回一个**服务器**对象【[Guild](../../khl/guild.py)】；并获取添加了回应的**用户**对象【[User](../../khl/user.py)】

~~~python
    # need to fetch_guild first
    g = await b.fetch_guild('5134217138075250') # input guild_id here
    # fetch user who ADDED_REACTION
    u = await b.fetch_user(event.body['user_id'])
    # fetch channel of the REACTION event
    channel = await b.fetch_public_channel(event.body['channel_id']) 
~~~

在服务器管理后台中，你可以右键复制用户角色(role)的ID并给机器人设置上，这样机器人才能给用户添加角色

* 22年6月下旬KOOK统一了emoji显示的格式，修复了同一个emoji会有两个`['emoji']['id']`的BUG。为了避免KOOK后续可能还会修改`['emoji']['id']`，本exp代码中`if`的判断一定要以当前打印的`['emoji']['id']`为准，否则会因为id不同导致无法正常匹配。

*  注意：第39行的`role_id`传参是int类型，而不是str

`if`判断的代码示例如下
~~~python
    if event.body["emoji"]['id'] == '🐷':
        await g.grant_role(u,4465168)
        await b.send(channel,f"grant_role 4465168 for you",temp_target_id=event.body['user_id']) 
    elif event.body["emoji"]['id'] == '🐯':
        await g.grant_role(u,4469565)
        await b.send(channel,f"grant_role 4469565 for you",temp_target_id=event.body['user_id']) 
~~~

这里建议添加一个判断语句，来保证设置角色功能只对某一条消息生效。要不然就乱套啦！

~~~python
if event.body['msg_id'] == '消息ID' 
~~~

## 自己动手：丰衣足食

除了添加角色后，机器人还可以撤销用户的角色，给服务器添加/删除用户角色

你可以查看[khl/guild.py](../../khl/guild.py)中的函数接口，尝试使用这些功能

引用大佬的话：“只看菜谱不动手的人，等锅都生锈了都学不会做饭”

----

下面是让机器人通过emoji设置用户角色的示例图

![example](./example.png)
