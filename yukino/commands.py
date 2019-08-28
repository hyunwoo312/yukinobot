from yukino import bot, jikan
from discord.ext import commands
import discord
import requests
from yukino import manager
import secrets
from pydub import AudioSegment
from pydub.utils import which
from os import listdir
from discord.utils import get
import os
import random
import youtube_dl
# import ffmpeg
audiodir = 'yukino/data/audiofiles/'
webmdir = 'yukino/data/cache/'
queriesdir = 'yukino/data/queries/'
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
    "Openings.moe": "openings.moe",
    "AniList": "https://graphql.anilist.co/",
    "MyAnimeList": "https://myanimelist.net/animelist/"
}

#youtube download options
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
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

@bot.command(aliases=['al'])
async def AnimeList(ctx, id):
    variables = {'id':int(id)}
    with manager.Manager(queriesdir+'AL_test.txt') as file:
        query = file.read()
    '''
    posts a GraphQL query to Anilist
    serialize the file as a json response then returns the titles
    '''
    response = requests.post(dataservers["AniList"], json={'query':query, 'variables':variables}).json()
    title1 = response['data']['Media']['title']['english']
    title2 = response['data']['Media']['title']['native']
    await ctx.send(title1+' '+title2)

@bot.command(aliases=['mal'])
async def MyanimeList(ctx, id):
    '''
    MyAnimeList's official API has been down for an extended period of time.
    I was planning on doing my own webscraping to do queries and other various
    functions, but I found a Jikan's unofficial MAL api python wrapper.
    This command will use Jikan's python MAL api.
    '''
    pass
	
@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, url: str):

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

	# If Song.mp3 exists, True.
	# If Song.mp3 doesn't exist, False 
	song_there = os.path.isfile("song.mp3")

	try:
		#If Song is in use, we go to except statement
	    if song_there:
	        os.remove("song.mp3")
	        print("Removed old song file")
	except PermissionError:
	    print("Trying to delete song file, but it's being played")
	    await ctx.send("ERROR: Music playing")
	    return

	await ctx.send("Getting everything ready now")

	# Passing in our options to youtube_dl
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
	    print("Downloading audio now\n")

	    #Downloads audio
	    ydl.download([url])

	for file in os.listdir("./"):
		#Rename Song file to uniformed name
	    if file.endswith(".mp3"):

	    	#save name of file
	        name = file
	        print(f"Renamed File: {file}\n")
	        os.rename(file, "song.mp3")

	# Plays the song and "after" displays message when its done
	voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("Song done!"))
	voice.source = discord.PCMVolumeTransformer(voice.source)
	voice.source.volume = 0.07

	#Prints out the song that is being played
	nname = name.rsplit("-", 2)
	await ctx.send(f"Playing: {nname[0]}")
	print("playing\n")


@bot.command()
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

@bot.command(pass_context=True)
async def _test(ctx, url):
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

	# If Song.mp3 exists, True.
	# If Song.mp3 doesn't exist, False 
	song_there = os.path.isfile("song.mp3")

	try:
		#If Song is in use, we go to except statement
	    if song_there:
	        os.remove("song.mp3")
	        print("Removed old song file")
	except PermissionError:
	    print("Trying to delete song file, but it's being played")
	    await ctx.send("ERROR: Music playing")
	    return

	await ctx.send("Getting everything ready now")

	# Passing in our options to youtube_dl
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
	    print("Downloading audio now\n")

	    #Downloads audio
	    ydl.download([url])

	for file in os.listdir("./"):
		#Rename Song file to uniformed name
	    if file.endswith(".mp3"):

	    	#save name of file
	        name = file
	        print(f"Renamed File: {file}\n")
	        os.rename(file, "song.mp3")

	# Plays the song and "after" displays message when its done
	voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print("Song done!"))
	voice.source = discord.PCMVolumeTransformer(voice.source)
	voice.source.volume = 0.07

	#Prints out the song that is being played
	nname = name.rsplit("-", 2)
	await ctx.send(f"Playing: {nname[0]}")
	print("playing\n")