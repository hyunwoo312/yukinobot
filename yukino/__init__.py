from discord.ext import commands

bot = commands.Bot(command_prefix='$', case_insensitive='True',\
    description='Type $help to see the list of commands available\
        and perhaps any cool details about me ❄❄❄', owner_id=476251120453550091\
            , self_bot='False')

# bot.activities('application')
import yukino.commands
import yukino.events