from yukino import bot
from discord.ext import commands
import discord
import requests
from yukino import manager
import secrets
# import ffmpeg

@bot.command()
async def test(ctx, *, arg):
    await ctx.send(arg)
    # await ctx.send(bot.users)
    #print(ctx)

@bot.command(aliases=['conv', 'convert'])
async def _convert(ctx, url):
    async with ctx.typing():
        filename = '{}.webm'.format(secrets.token_hex(8))
        with manager.Manager(filename, 'wb') as file:
            r = requests.get(url, allow_redirects=True)
            file.write(r.content)
            # webm = ffmpeg.input(r.content)
            # audiofile = ffmpeg.output(webm.audio, )
            # file.write(r.content)
        await ctx.send('done!, you may now access the file: {filename}',\
             file=discord.File('README.md', spoiler=True)) 

@bot.command()
async def clear(ctx, amount=1):
    await ctx.channel.purge(limit=amount)
