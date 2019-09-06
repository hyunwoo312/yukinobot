from discord.ext import commands
from jikanpy import Jikan
import sqlite3

bot = commands.Bot(command_prefix='$', case_insensitive='True',\
    description='Type $help to see the list of commands available\
        and perhaps any cool details about me ❄❄❄', self_bot=False)
jikan = Jikan()
db = sqlite3.connect('yukino/data/yukinodatabase.db')

# bot.activities('application')
import yukino.commands
import yukino.events