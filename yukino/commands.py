from yukino import bot
from discord.ext import commands

@bot.command()
async def test(ctx, *, arg):
    await ctx.send(arg)

@bot.command()
@commands.is_owner()  # The account that owns the bot
async def dm(ctx):
    memberID = "ID OF RECIPIENT"
    person = await bot.get_user_info(memberID)
    await bot.send_message(person, "WHAT I'D LIKE TO SAY TO THEM")
    await bot.delete_message(ctx.message)