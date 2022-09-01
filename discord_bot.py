import os
from discord.ext import commands
from datetime import datetime, timedelta
from discord.ext import tasks
from math import floor
import pickle

Token = os.getenv('DISCORD_TOKEN')
Guild = os.getenv('DISCORD_GUILD')
Discord_user = os.getenv('DISCORD_USER')
bot = commands.Bot(command_prefix='!')

temp_heartbeat = [0]


@bot.command(name='heartbeat') #2 command, kulon kulon a serverekre
async def heartbeat(ctx):
    with open(f'heartbeat', 'rb') as f:
        result = pickle.load(f)
    message = 'You have no open position'
    utc_time = datetime.strptime((result['Heartbeat'][0]), "%Y-%m-%d %H:%M:%S")
    cet_time = utc_time + timedelta(hours=2)
    if float(result['Quantity'][0]) != 0.00:
        if float(result['Quantity'][0]) > 0:
            message = f'You have an open long position, opened on {result["Timeopened"][0]}'
        elif float(result['Quantity'][0]) < 0:
            message = f'You have an open short position, opened on {result["Timeopened"][0]}'
    await ctx.send(f'beep boop: {cet_time} --- {message}')


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
    position_reminder.start()
    heartbeat_reminder.start()

@tasks.loop(hours=1)
async def position_reminder():
    with open(f'heartbeat', 'rb') as f:
        result = pickle.load(f)
    if float(result['Quantity'][0]) == 0.00:
        result['Timeopened'][0] = datetime.now()
        with open(f'heartbeat', 'wb') as f:
            pickle.dump(result, f)
    else:
        counter = datetime.now() - datetime.strptime((result['Timeopened'][0]), "%Y-%m-%d %H:%M:%S.%f")
        openhours = (counter.days * 24) + (counter.seconds/60/60)
        print(counter.seconds/60/60)
        channel = bot.get_channel(1013131816137408672)
        if openhours >= 7:
            if int((datetime.now() + timedelta(hours=2)).strftime('%H')) < 9:
                pass
            await channel.send(f'<@{Discord_user}> position has been open for more than {floor(openhours)} hours')

@tasks.loop(minutes=5)
async def heartbeat_reminder():
    heartbeat_notified = temp_heartbeat[0]
    with open(f'heartbeat', 'rb') as f:
        result = pickle.load(f)
    channel = bot.get_channel(1013131816137408672)
    if (datetime.now() - datetime.strptime((result['Heartbeat'][0]), "%Y-%m-%d %H:%M:%S")).seconds > 15*60:
        if heartbeat_notified == 0:
            temp_heartbeat[0] = 1
            await channel.send(f'<@{Discord_user}> bot is dead, last hearbeat at {result["Heartbeat"][0] + timedelta(hours=2)}, error:{result["Error"]}') #user id var
    else:
        temp_heartbeat[0] = 0


bot.run(Token)