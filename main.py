import discord
import logging
from discord.ext import commands, tasks

import asyncio
from time_diff import calculate_time_diff
from dotenv import load_dotenv
import os

from aiohttp import web

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="$", intents=intents)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

load_dotenv()

async def start_web_server():
    PORT = os.getenv("PORT")
    app = web.Application()
    async def health_check(request):
        return web.Response(text="Bot is running")
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)

    await site.start()
    print(f"Pseudo-Webserver läuft auf Port {PORT}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    bot.loop.create_task(start_web_server())

@bot.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')
    await bot.process_commands(message)

@bot.event
async def on_guild_available(guild):
    print(f'Guild available: {guild.name}')

@commands.command()
async def init(ctx, channel_id):
    bot.channel_id = int(channel_id)
    await ctx.send(f"Channel ID: {bot.channel_id} set.")

@init.error
async def init_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a valid channel ID.")
    else:
        await ctx.send("An error occurred while setting the channel ID.")

@commands.command()
async def start(ctx):
    if not update_channel_name.is_running():
        await ctx.send("Starting countdown...")
        update_channel_name.start()

@start.error
async def start_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Not a valid channel ID.")
    else:
        await ctx.send("An error occurred while starting the countdown.")

@commands.command()
async def stop(ctx):
    if update_channel_name.is_running():
        await ctx.send("Stopping countdown...")
        update_channel_name.cancel()
    else:
        await ctx.send("Countdown is not running.")

@stop.error
async def stop_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("No arguments required.")
    else:
        await ctx.send("An error occurred while stopping the countdown.")

@tasks.loop(minutes=5)
async def update_channel_name():
    print("Trying to update channel name...")
    channel = bot.get_channel(bot.channel_id)
    time_diff = calculate_time_diff()
    try:
        await channel.edit(name=f"{time_diff}")
    except discord.errors.HTTPException as e:
        if e.status == 429:
            print(f"Rate limit exceeded. Waiting for {e.retry_after} seconds...")
            await asyncio.sleep(e.retry_after)
            await channel.edit(name=f"{time_diff}")
        else:
            print(f"Failed to update channel name: {e}")

def main():
    bot.add_command(init)
    bot.add_command(start)
    bot.add_command(stop)

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    bot.run(BOT_TOKEN, log_handler=handler)

if __name__ == "__main__":
    main()  