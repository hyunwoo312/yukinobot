from yukino import bot
from time import sleep

@bot.event
async def on_ready():
    print('雪ノ下雪乃は本当にきれいな')

@bot.event
async def on_typing(channel, user, when):
    '''
    611058665503588356 is yukinobot's discord ID
    '''
    if user.id != 611058665503588356:
        async with channel.typing():
            sleep(3)
            await channel.send('uwu')

@bot.event
async def on_message(msg):
    if msg.content.lower()=='nani':
        return print('wow this kid cool')
    print(f'{msg.author.id}, {msg.channel}')


# @bot.event
# async with typing():

