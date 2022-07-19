import json

from khl import Bot, Message, EventTypes, Event
from khl.card import CardMessage, Card, Module

with open('../config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Bot
bot = Bot(token=config['token'])


# set event ADDED_REACTION
@bot.on_event(EventTypes.ADDED_REACTION)
async def reaction_reminder(b:Bot,event:Event):
    print(event.body) # print the complete `event.body`

    # fetch channel of the REACTION event
    channel = await b.fetch_public_channel(event.body['channel_id']) 
    # send a messge to inform user at current channel
    await b.send(channel,f"you add reaction{event.body['emoji']['id']}") 
    # send a messge to inform user at current channel
    # but only visible to `event.body['user_id']`
    # checkout `exp04` for `send` message
    await b.send(channel,f"you add reaction{event.body['emoji']['id']}",temp_target_id=event.body['user_id']) 


# you can use this fuction to set a role for user by checking the reaction emoji
# more information at `https://developer.kaiheila.cn/doc/http/guild-role`
@bot.on_event(EventTypes.ADDED_REACTION)
async def reaction_set_roles(b:Bot,event:Event):
    # need to fetch_guild first
    g = await b.fetch_guild('xxxxxxxxxxxxx') # input guild_id here
    # fetch user who ADDED_REACTION
    u = await b.fetch_user(event.body['user_id'])
    # fetch channel of the REACTION event
    channel = await b.fetch_public_channel(event.body['channel_id']) 
    # input role_id (int) here
    role = 4465168
    # grant_role for user who ADDED_REACTION
    await g.grant_role(u,role)
    
    # what's more,you can use reaction to set specific role for user
    # first, checkout `event.body['emoji']['id']`for the emoji you set
    # print it to make sure current `['emoji']['id']`
    # then, use `if` to compare and set different roles for user
    # it's better to use " if event.body['msg_id'] == 'msg_id' " to make sure it only respond reaction to `msg_id`
    if event.body["emoji"]['id'] == '🐷':
        await g.grant_role(u,4465168)
        await b.send(channel,f"grant_role 4465168 for you",temp_target_id=event.body['user_id']) 
    elif event.body["emoji"]['id'] == '🐯':
        await g.grant_role(u,4469565)
        await b.send(channel,f"grant_role 4469565 for you",temp_target_id=event.body['user_id']) 

# use card message to show `roles & emoji`
# you can find emoji at `https://www.webfx.com/tools/emoji-cheat-sheet/#`
# example as `example.png` 
@bot.command()
async def RoleSet(msg:Message):
    cm = CardMessage()
    c1 = Card(Module.Header('Add reaction to get a role for yourself!'), Module.Context('Waiting for more roles...'))
    c1.append(Module.Divider())
    c1.append(Module.Section('「:pig:」test1  「:tiger:」test2\n'))
    cm.append(c1)
    await msg.ctx.channel.send(cm)


# everything done, go ahead now!
bot.run()
