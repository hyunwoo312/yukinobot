from yukino import bot
from discord.ext import commands
import discord
import requests
from yukino import manager

@bot.command()
async def test(ctx, *, arg):
    await ctx.send(arg)
    # await ctx.send(bot.users)
    #print(ctx)

@bot.command(aliases=['conv', 'convert'])
async def _convert(ctx, url):
    async with ctx.typing():
        r = requests.get(url, allow_redirects=True)
        open('test.webm', 'wb').write(r.content)
