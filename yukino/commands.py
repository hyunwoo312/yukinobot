from yukino import bot
from discord.ext import commands
import discord
import requests
from yukino import manager
import secrets
from pydub import AudioSegment
from pydub.utils import which
from os import listdir
# import ffmpeg
audiodir = 'yukino/data/audiofiles/'
webmdir = 'yukino/data/webmcache/'
audiotype = [
    'Openings',
    'Endings', 
    'Inserts'
]

audiofileext = [
    '.mp3', 
    '.webm',
    '.wav'
]

dataservers = {
    "AnimeThemes": "animethemes.moe",
    "Openings.moe": "openings.moe"
}

def converttoaudio(ftype, url, filename=secrets.token_hex(16), directory=audiodir, ext=audiofileext[0]):
    '''
    filename is defaulted to a 16-hex randomized string;; filename must be a string
    directory is defaulted to audiodir;; directory must be a string 
    ext is defaulted to mp3;; must be a string preceiding with '.'
    ftype is a string value that organizes audiofiles into subdirectories
    ...
    this function returns a discord.File object, None if error
    '''
    AudioSegment.converter = which("ffmpeg") #defaulting ffmpeg as a converter
    try:
        audiofile = directory+ftype+'/'+filename+ext
        webmfile = webmdir+filename+audiofileext[1]
        if filename+ext in listdir(audiodir+ftype):
            return discord.File(audiofile, spoiler=False)
        else:
            if filename+audiofileext[1] not in listdir(webmdir):
                with manager.Manager(webmfile, 'wb') as file:
                    r = requests.get(url, allow_redirects=True)
                    file.write(r.content)
            audio = AudioSegment.from_file(webmfile, 'webm')
            audio.export(audiofile, format=ext[1:])
        return discord.File(audiofile, spoiler=False)
    except:
        return None
    
@bot.command()
async def test(ctx, *, arg):
    await ctx.send(arg)

@bot.command(aliases=['conv', 'cv', 'convert'])
async def _convert(ctx, url):
    async with ctx.typing():
        try:
            if dataservers["AnimeThemes"] in url:
                filename = url.split('/')[-1].split('.')[0] #extracts videoname
                ftype = audiotype[0] if '-OP' in url else audiotype[1]#animetheme only has Openings and Endings
            audiofile = converttoaudio(ftype=ftype, url=url, filename=filename)
            if audiofile == None:
                raise Exception #error thrown by converttoaudio
            await ctx.send(
                'File conversion complete! The following is the converted {} file of {}'
                .format(audiofileext[0][1:], filename), file=audiofile)
        except:
            await ctx.send('∑（｡･Д･｡）??? The File Conversion Has Failed. ( •᷄ὤ•᷅)？')

@bot.command()
async def clear(ctx, amount=1):
    await ctx.channel.purge(limit=amount)
