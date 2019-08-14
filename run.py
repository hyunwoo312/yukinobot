from yukino import bot
if __name__=='__main__':
    token = open('yukino/data/token.txt', 'r')
    bot.run(token.read())
    token.close()