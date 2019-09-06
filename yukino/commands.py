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
from datetime import datetime
import os
import random
import youtube_dl
# import ffmpeg
audiodir = 'yukino/data/audiofiles/'
webmdir = 'yukino/data/cache/'
queriesdir = 'yukino/data/queries/'
today = datetime.today().isoformat().split('T')[0] # 'YYYY-MM-DD'
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
async def MyAnimeList(ctx, action, _type, *, arg=None):
    '''
    MyAnimeList's official API has been down for an extended period of time.
    I was planning on doing my own webscraping to do queries and other various
    functions, but I found a Jikan's unofficial MAL api python wrapper.
    This command will use Jikan's python MAL api.
    Available action parameters are:
    seasons/years; search; 
    '''
    try:
        async with ctx.typing():
            action = action.lower()
            _type = _type.lower()
            if action == 'request':
                # returns years and seasons for which MAL has anime data
                if _type == 'seasons' or _type == 'years':
                    malseasonarchive = jikan.season_archive()['archive']
                    years = []
                    seasons = malseasonarchive[0]['seasons']
                    for archive in malseasonarchive:
                            years.append(archive['year'])
                    await ctx.send(
                        'The following are the years and seasons for which MyAnimeList has anime data:\nSeasons = {}\nYears = {}'.format(
                            seasons, years
                        )
                    )
                elif _type == 'profile':
                    profile = jikan.user(username=arg, request=_type)
                    await ctx.send(profile)
                elif _type == 'animelist':
                    animelist = jikan.user(username=arg, request=_type)['anime'] #argument parameter eg completed
                    _list = ''
                    for i in animelist:
                        _list =  _list+'|'+i['title']+'|'
                    await ctx.send(_list)
            # searches MAL for several things
            elif action == 'search':
                if _type not in ['anime', 'manga', 'person', 'character']:
                    raise ValueError
                await ctx.send('Search Results:\n')
                # using jikan to search
                seach_result = jikan.search(_type, arg, parameters={'limit':3, 'order_by':'title'})
                top3res = seach_result['results']
                if _type == 'anime':
                    for anime in top3res:
                        status = 'Airing'
                        if anime['airing'] == False:
                            status = 'Aired from {} to {}'.format(
                                anime['start_date'].split('T')[0], anime['end_date'].split('T')[0]
                            )
                        else: # true
                            if today < anime['start_date'].split('T')[0]:
                                status = 'To be aired'
                        score = 'N/A' if anime['score'] == 0 else anime['score']
                        response = '>>> {}\n{}\nStatus: {}\nScore: {}\nSynopsis: {}\n\n'.format(
                            anime['title'] ,anime['url'], status, score, anime['synopsis']
                        )
                        await ctx.send(response)
                elif _type == 'manga':
                    pass
                elif _type == 'person':
                    pass
                else: #'character':
                    pass
            else:
                raise Exception
    except:
        await ctx.send('... there is an error. Perhaps check for typos. - 雪ノ下雪乃')

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


@bot.command()
async def _test(ctx, url):
    print("DannyIsGod")
