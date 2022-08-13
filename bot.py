import discord as api
import asyncio
import os
from discord.ext import commands, flags
from discord.ext.commands import has_permissions, MissingRequiredArgument, BadArgument, MissingPermissions
from discord.utils import get
from properties import prefix, token, intents, insensitiveCase, ownerID, dagpi_token
from discord.ext import ui
import time, datetime, humanize
import json
import subprocess as sp
from Utils.utils import DMBText, DMBot, Utils
from asyncdagpi import Client
import prettify_exceptions
import mystbin
import re
import logging
from adventure import Adventure
from userphone import Userphone
import traceback

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
start = time.time()
intents = api.Intents().all()
prefixes_db_path = './prefixes.json'

def get_prefix(bot, message):
    if message.guild is None:
        return ''
    cur = bot.db.execute('SELECT prefix FROM prefixes WHERE guild_id = ?', (message.guild.id,))
    result = cur.fetchall()
    if result == []:
        if message.author.id in (376129806313455616, 528290553415335947) and bot.prefixless:
            return commands.when_mentioned_or(*['::', ''])(bot, message)
        else:
            return commands.when_mentioned_or('::')(bot, message)
    else:
        if message.author.id in (376129806313455616, 528290553415335947) and bot.prefixless:
            try:
                return commands.when_mentioned_or(*[result[0][0], ''])(bot, message)
            except TypeError:
                return commands.when_mentioned_or(*['::', ''])(bot, message)
        else:
            try:
                return commands.when_mentioned_or(result[0][0])(bot, message)
            except TypeError:
                return commands.when_mentioned_or('::')(bot, message)

bot = DMBot(command_prefix=get_prefix, intents=intents, case_insensitive=insensitiveCase, owner_ids={376129806313455616, 528290553415335947})

def who(person, command):
    trigger = f'{person} just ran {command}'
    return trigger

@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    try:
        if extension == 'jishaku':
            bot.load_extension('jishaku')
            return
        await bot.load_extension(f'Commands.{extension.capitalize()}.{extension}')
        bot.log.info(f"Extension \"{extension}\" has just been loaded")
        await ctx.message.add_reaction('\U00002705')
    except commands.ExtensionFailed as e:
        bot.log.error('Extension Failed', exc_info=True)
        await ctx.send(e)
        await ctx.message.add_reaction('\U0000274e')

@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    try:
        if extension == 'jishaku':
            bot.unload_extension('jishaku')
            return
        await bot.unload_extension(f'Commands.{extension.capitalize()}.{extension}')
        bot.log.info(f"Extension \"{extension}\" has just been unloaded")
        await ctx.message.add_reaction('\U00002705')
    except commands.ExtensionFailed as e:
        bot.log.error('Extension Failed', exc_info=True)
        await ctx.send(e)
        await ctx.message.add_reaction('\U0000274e')

@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    try:
        if extension == 'jishaku':
            await bot.reload_extension('jishaku')
            await ctx.message.add_reaction('\U00002705')
            return
        if extension == '~':
            for path in bot.cog_paths:
                bot.reload_extension(path)
        else:
            await bot.reload_extension(f'Commands.{extension.capitalize()}.{extension}')
            bot.log.info(f"Extension \"{extension}\" has just been reloaded")
        await ctx.message.add_reaction('\U00002705')
    except commands.ExtensionFailed as e:
        bot.log.error('Extension Failed', exc_info=True)
        etype = type(e)
        trace = e.__traceback__
        await ctx.send('```py\n' + ''.join(traceback.format_exception(etype, e, trace)).replace('C:\\Users\\Meisc\\Desktop\\OneDriveBackupFiles\\Documents\\Discord Bot\\The Former\\Discord Mega Bot', '[HOME PATH]').replace('C:\\Users\\Meisc\\AppData\\Local\\Programs\\Python', '[PYTHON PATH]') + '\n```')
        await ctx.message.add_reaction('\U0000274e')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    bot.log.info('Bot has successfully started!')

@bot.command(aliases=['changeprefix'])
@has_permissions(administrator=True)
async def setprefix(ctx, prefix:str):
    if bot.db.execute('SELECT prefix FROM prefixes WHERE guild_id = ?', (ctx.guild.id,)).fetchall() == []:
        cur = bot.db.execute('INSERT INTO prefixes(prefix, guild_id) VALUES (?, ?)', (prefix, ctx.guild.id,))
        bot._conn.commit()
    else:
        cur = bot.db.execute('UPDATE prefixes SET prefix = ? WHERE guild_id = ?', (prefix, ctx.guild.id,))
        bot._conn.commit()
    try:
        await ctx.guild.me.edit(nick=f'[{prefix}] Discord Mega Bot')
        await ctx.send(f'Successfully changed server prefix to `{prefix}`')
    except api.HTTPException:
        await ctx.send('Nickname must be 32 or fewer in length! Although, i did change the prefix')
    bot.log.info(f'Prefix in {ctx.guild.id} has just been changed to {prefix}')

@bot.event
async def on_command_error(ctx, error):
    desc = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
    command = ctx.command
    bot.log.error(f'Command "{command}" has just errored\n{desc}')
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.NotOwner):
        await ctx.send('You must own this bot to use this command')
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'{str(error)}')
    else:
        embed = api.Embed(title='An error occured.', description = str(error), color = 0x2F3136)
        await ctx.send(embed=embed)
        raise error

@bot.ipc.route()
async def get_member_count(data):
    guild = bot.get_guild(
        data.guild_id
    )  # get the guild object using parsed guild_id

    return guild.member_count  # return the member count to the client

@bot.ipc.route()
async def get_users(data):
    users = bot.users
    return len(users)

@bot.ipc.route()
async def get_guilds(data):
    guilds = bot.guilds
    return len(guilds)

@bot.event
async def on_message_edit(before, after):
    if after.content.startswith(tuple(get_prefix(bot, after))) and (not before.content == after.content):
        await bot.process_commands(after)
    try:
        bot.edit_history[after.id].append(after)
    except:
        bot.edit_history[after.id] = (after)

@bot.event
async def on_command_completion(ctx):
    bot._commands += 1
    bot.log.info(f'Command "{ctx.command.name}" was just invoked by "{str(ctx.author)}"')

@bot.event
async def on_message(message):
    if message.content == f'<@!{bot.user.id}>':
        embed = api.Embed(title='Hello!', color=api.Color.green(), description=f'My prefix is {get_prefix(bot, message)[2]}, and you can mention me, of course.')
        await message.channel.send(embed=embed)
    await bot.process_commands(message)

@bot.command(brief='Start an adventure, a throwback to one of my old bots :D')
async def adventure(ctx):
    advent = Adventure(bot, ctx.author, ctx.channel)
    await advent.start()

@bot.command()
async def userphone(ctx):
    phone = Userphone()
    await phone.main(ctx)

@bot.event
async def on_guild_join(guild):
    embed = api.Embed(
        title='New Server',
        description=f'I was just added to {guild.name}' + ('\n\nDo note that this may be a bot farm' if guild.member_count > 45 else '\n') + f'\nHumans: {len([c for c in guild.members if not c.bot])}, Bots: {len([c for c in guild.members if c.bot])}' + f'\nNow in {len(bot.guilds)} guilds',
        color=0x2F3136
        )
    await bot.get_channel(814761390019182623).send(embed=embed)
    bot.log.info(f'Bot has just been added to "{guild.name}"')

@bot.event
async def on_guild_remove(guild):
    embed = api.Embed(
        title='Removed From Server',
        description=f'I was just removed from {guild.name}' + f'\nNow in {len(bot.guilds)} guilds',
        color=0x2F3136
        )
    await bot.get_channel(814761390019182623).send(embed=embed)
    bot.log.info(f'Bot has just been removed from "{guild.name}"')

@bot.event
async def on_message_delete(message):
    if message.edited_at:
        del bot.edit_history[message.id]

@bot.event
async def on_event(event):
    try:
        bot.events_dispatched[event] += 1
    except:
        bot.events_dispatched[event] = 1

@flags.add_flag('--color', type=int, default=0x2F3136)
@flags.add_flag('--title', default="placeholder")
@flags.add_flag('--description', default="placeholder")
@flags.command()
async def embed_builder(ctx, **flags):
    emby = api.Embed(title=flags['title'], description=flags['description'], color=flags['color'])
    await ctx.send(embed=emby)
bot.add_command(embed_builder)

bot.run(token)
