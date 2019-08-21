from yukino import bot, manager
from discord.ext import commands
import discord
import requests
import secrets
from pydub import AudioSegment
from pydub.utils import which
from discord.utils import get
import os
import random
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

players = {}

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
        if filename+ext in os.listdir(audiodir+ftype):
            return discord.File(audiofile, spoiler=False)
        else:
            if filename+audiofileext[1] not in os.listdir(webmdir):
                with manager.Manager(webmfile, 'wb') as file:
                    r = requests.get(url, allow_redirects=True)
                    file.write(r.content)
            audio = AudioSegment.from_file(webmfile, 'webm')
            audio.export(audiofile, format=ext[1:])
            cachemanager(webmdir) # deleting webm files cz they r huge;; audio files are tiny in comparison
        return discord.File(audiofile, spoiler=False)
    except:
        return None

def cachemanager(directory):
    cachesize = 0
    for file in os.listdir(directory):
        cachesize += os.path.getsize(directory+file)
    if cachesize >= 200000000:
        os.remove(directory+os.listdir(directory)[random.randint(0,3)])
        print('cacheresized')
    
@bot.command()
async def test(ctx, *, arg):
    await ctx.send(arg)

@bot.command()
async def clear(ctx, amount=1):
    await ctx.channel.purge(limit=amount)

@bot.command()
async def ping(ctx):
    pong = bot.latency * 1000
    await ctx.send('the current ping is {:.5}ms'.format(pong))

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
            ctx.send('∑（｡･Д･｡）??? The File Conversion Has Failed. ( •᷄ὤ•᷅)？')

@bot.command()
async def anilist(ctx):
    query = '''
    query ($id: Int) {
    Media (id: $id, type: ANIME) { 
        id
        title {
        romaji
        english
        native
        }
    }
    }
    '''

    # Define our query variables and values that will be used in the query request
    variables = {
        'id': 10087#,
        #'search': 'Katanagatari'
    }
    url = 'https://graphql.anilist.co'

    response = requests.post(url, json={'query': query, 'variables': variables})
    await ctx.send(response.json())

@bot.command()
async def play(ctx, url: str):
	
	# If Song.mp3 exists, True.
	# If Song.mp3 doesn't exist, False 
	song_Exists = os.path.isfile("song.mp3")

	#If True
	if song_Exists:
		os.remove("song.mp3")
		await ctx.send(f"Removed Old Song file")


@bot.command(aliases=['join'])
async def connect(ctx):
	global voice
	
	# gets the Channel we're in
	channel = ctx.message.author.voice.channel

	voice = get(bot.voice_clients, guild=ctx.guild)

	# If Yukino is already in a different voice channel and is connected, move to current channel
	if voice and voice.is_connected():
		await voice.move_to(channel)
	else:
		voice = await channel.connect()

	await ctx.send(f"Joined {channel}")

	# Uncomment this code if there's a bug where you have to
	# disconnect Yukino to play the next song

	#await voice.disconnect()	

	# If Yukino is already in a different voice channel and is connected, move to current channel
	#if voice and voice.is_connected():
	#	await voice.move_to(channel)
	#else:
	#	voice = await channel.connect()

@bot.command(aliases=['dc', 'disc'])
async def disconnect(ctx):

	# gets the Channel we're in
	channel = ctx.message.author.voice.channel

	voice = get(bot.voice_clients, guild=ctx.guild)
	# If Yukino is already in a different voice channel and is connected, disconnect it
	if voice and voice.is_connected():
		await voice.disconnect()
        # await ctx.send(f"Yukino Bot has been Killed in Channel {channel} D:")
	else:
		# If its not in a channel at all
		await ctx.send("Baka. Yukino is not in a Channel!")