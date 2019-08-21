from yukino import bot
from time import sleep

@bot.event
async def on_ready():
    print('雪ノ下雪乃は本当にきれいな')

# @bot.event
# async def on_typing(channel, user, when):
#     '''
#     611058665503588356 is yukinobot's discord ID
#     '''
#     if user.id != 611058665503588356:
#         async with channel.typing():
#             sleep(1)
#             await channel.send('uwu')

# @bot.event
# async def on_message(msg):
#     if msg.content.lower()=='nani':
#         await print('wow this kid cool')
#     await msg.channel.send('{msg.author.id}, {msg.channel}, {msg.content}')


# @bot.event
# async with typing():

