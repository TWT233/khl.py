import json
from datetime import datetime, timedelta

from khl import Bot, Message, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types, Struct

with open('../config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Bot
bot = Bot(token=config['token'])


@bot.command()
async def card(msg: Message):
    c = Card(Module.Header('CardMessage'), Module.Section('convenient to convey structured information'))
    cm = CardMessage(c)  # Card can not be sent directly, need to wrapped with a CardMessage
    await msg.reply(cm)


@bot.command()
async def countdown(msg: Message):
    cm = CardMessage()

    c1 = Card(Module.Header('Countdown example'), color='#5A3BD7')  # color=(90,59,215) is another available form
    c1.append(Module.Divider())
    c1.append(Module.Countdown(datetime.now() + timedelta(hours=1), mode=Types.CountdownMode.SECOND))
    cm.append(c1)

    c2 = Card(theme=Types.Theme.DANGER)  # priority: color > theme, default: Type.Theme.PRIMARY
    c2.append(Module.Section('the DAY style countdown'))
    c2.append(Module.Countdown(datetime.now() + timedelta(hours=1), mode=Types.CountdownMode.DAY))
    cm.append(c2)  # A CardMessage can contain up to 5 Cards

    await msg.reply(cm)


# button example, build a card in a single statement
# btw, short code without readability is not recommended
@bot.command()
async def button(msg: Message):
    await msg.reply(
        CardMessage(
            Card(
                Module.Header('An example for button'),
                Module.Context('Take a pill, take the choice'),
                Module.ActionGroup(
                    # RETURN_VAL type(default): send an event when clicked, see print_btn_value() defined at L58
                    Element.Button('Truth', 'RED', theme=Types.Theme.DANGER),
                    Element.Button('Wonderland', 'BLUE', Types.Click.RETURN_VAL)),
                Module.Divider(),
                Module.Section(
                    'another kind of button, user will goto the link when clicks the button:',
                    # LINK type: user will open the link in browser when clicked
                    Element.Button('link button', 'https://github.com/TWT233/khl.py', Types.Click.LINK)))))


# struct example
@bot.command()
async def struct(msg: Message):
    await msg.reply(CardMessage(Card(Module.Section(Struct.Paragraph(3, 'a', 'b', 'c')))))


@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def print_btn_value(_: Bot, e: Event):
    print(f'''{e.body['user_info']['nickname']} took the {e.body['value']} pill''')


# everything done, go ahead now!
bot.run()
