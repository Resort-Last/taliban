import os
from discord.ext import commands
from datetime import datetime, timedelta


Token = os.getenv('DISCORD_TOKEN')
Guild = os.getenv('DISCORD_GUILD')
Channel = "80-as-evek"
bot = commands.Bot(command_prefix='!')



@bot.command(name='heartbeat') #2 command, kulon kulon a serverekre
async def heartbeat(ctx):
    with open('heartbeat_log.txt') as f:
        lines = f.readlines()
        utc_time = datetime.strptime(lines[0][0:20], "%Y-%m-%d %H:%M:%S")
        cet_time = utc_time + timedelta(hours=2)
    await ctx.send(cet_time)


@bot.command(name='slave') #2 command, kulon kulon a serverekre
async def heartbeat(ctx):
    lines = 'yes Master? How may I help you today? '
    await ctx.send(lines)



@bot.event
async def on_ready():
    for guild in bot.guilds: #in case your bot is connected to multiple servers
        if guild.name == Guild:
            break

    print(f'{bot.user.name} has connected to {guild.name} id {guild.id}')



bot.run(Token)