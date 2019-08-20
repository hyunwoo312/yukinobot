from yukino import bot
from yukino import manager
if __name__=='__main__':
    with manager.Manager('yukino/data/token.txt') as token:
        bot.run(token.read())
