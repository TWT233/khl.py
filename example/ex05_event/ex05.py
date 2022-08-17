import json
from datetime import datetime

from khl import Bot, EventTypes, Event

# load config from config/config.json, replace `path` to your own config file
# config template: `./config/config.json.example`
with open('../config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Bot
bot = Bot(token=config['token'])


# register event handler
# handle function params need to be: (Bot, Event)
# for more event types, please turn to ``EventTypes``
@bot.on_event(EventTypes.UPDATED_MESSAGE)
async def update_reminder(b: Bot, event: Event):
    """
    :param b: the Bot which received ``event``, useful if you wanna put event handler in another place
    :param event: the event object, refer to khl document for the details of event, document to ``UPDATED_MESSAGE``:
     https://developer.kaiheila.cn/doc/event/channel#%E9%A2%91%E9%81%93%E6%B6%88%E6%81%AF%E6%9B%B4%E6%96%B0
    """
    channel = await b.client.fetch_public_channel(event.body['channel_id'])
    updated_at = datetime.fromtimestamp(event.body["updated_at"] / 1000)  # ms timestamp -> POSIX timestamp
    await b.client.send(channel, f'msg {event.body["msg_id"]} was updated at {updated_at}')


async def delete_catcher(b: Bot, event: Event):
    channel = await b.client.fetch_public_channel(event.body['channel_id'])
    await b.client.send(channel, f'msg {event.body["msg_id"]} was deleted...')


# besides decorator, you can also add event handler via this method
# useful when event handler is defined in another place
bot.add_event_handler(EventTypes.DELETED_MESSAGE, delete_catcher)

# everything done, go ahead now!
bot.run()
