from yukino import bot
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

# youtube download options
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
    AudioSegment.converter = which(
        "ffmpeg")  # defaulting ffmpeg as a converter
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
            # deleting webm files cz they r huge;; audio files are tiny in comparison
            cachemanager(webmdir)
        return discord.File(audiofile, spoiler=False)
    except:
        return None


def cachemanager(directory):
    cachesize = 0
    for file in os.listdir(directory):
        cachesize += os.path.getsize(directory+file)
    if cachesize >= 200000000:
        os.remove(directory+os.listdir(directory)[random.randint(0, 3)])
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
			print("Before Data Servers\n")
			if dataservers["AnimeThemes"] in url:
				# extracts videoname
				filename = url.split('/')[-1].split('.')[0]
				# animetheme only has Openings and Endings
				ftype = audiotype[0] if '-OP' in url else audiotype[1]
				audiofile = converttoaudio(ftype=ftype, url=url, filename=filename)
			if audiofile == None:
				print("We reachedd Exception\n")
				raise Exception  # error thrown by converttoaudio
			await ctx.send(	
				'File conversion complete! The following is the converted {} file of {}'
				.format(audiofileext[0][1:], filename), file=audiofile)
			# Helper Functions at the bottom
			print("Before Connect")
			await connect(ctx)
			print("Before Play but After Connect")
			#await playSong(ctx, filename)
			print("After Play")
		except:
			await ctx.send('∑（｡･Д･｡）??? The File Conversion Has Failed. ( •᷄ὤ•᷅)？')


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
        'id': 10087  # ,
        # 'search': 'Katanagatari'
    }
    url = 'https://graphql.anilist.co'

    response = requests.post(
        url, json={'query': query, 'variables': variables})
    await ctx.send(response.json())


@bot.command(aliases=['p', 'pla'])
async def play(ctx, url: str):

    await connect(ctx)

    # If Song.mp3 exists, True.
    # If Song.mp3 doesn't exist, False
    song_there = os.path.isfile("song.mp3")

    try:
        # If Song is in use, we go to except statement
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

        # Downloads audio to current directory
        ydl.download([url])

	#Searches current directory where code was executed (Current Directory is run.py location)
    for file in os.listdir("./"):
        # Rename Song file to uniformed name
        if file.endswith(".mp3"):

            # save name of file
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice = get(bot.voice_clients, guild=ctx.guild)
    # Plays the song and "after" displays message when its done
    voice.play(discord.FFmpegPCMAudio("song.mp3"),
               after=lambda e: print("Song done!"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.50

    # Prints out the song that is being played
    nname = name.rsplit("-", 2)
    await ctx.send(f"Playing: {nname[0]}")
    print("playing\n")

# Helper Functions

'''
Purpose: Helper function that  
Parameters: Ctx, file name of the converted file
'''
async def playSong(ctx, filename: str):

    # Change Directory to where Song File is downloaded to
    os.chdir("yukino/data/audiofiles/Openings")

    voice = get(bot.voice_clients, guild=ctx.guild)

	#Adds .mp3 to the end of file name
    trueFileName = filename + ".mp3"
    print("The File Name is:", trueFileName)

	#Finds the correct file and plays it
    voice.play(discord.FFmpegPCMAudio(trueFileName),
               after=lambda e: print("Song done!"))

    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.50

	#Sends back to Channel the name of file
    nname = filename.rsplit("-", 2)
    await ctx.send(f"Playing: {nname[0]}")

'''
Purpose: Helper function that Connects to the channel User who called Command is in 
Parameters: Ctx
'''
async def connect(ctx):

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


@bot.command()
async def _test(ctx, url):
    print("DannyIsGod")
