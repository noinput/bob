import asyncio
import argparse
import base64
import configparser
import discord
import hashlib
import json
import logging
import os
import pathlib
import sys
import time
import re

from logging.handlers import TimedRotatingFileHandler

from resources.bobdb import BobDb
from resources.bobhelper import BobHelper
from resources.owplayer import OWPlayer


bot = discord.Client()

@bot.event
async def on_ready():
        logger.info(f'logged in as {bot.user.name} - Discord.py: v{discord.__version__}')

@bot.event
async def on_message(message):
    if str(message.channel.type) != 'text':
        return

    ds = f'{str(bot.get_channel(message.channel.id)).title()} @ {str(bot.get_guild(message.guild.id))}'

    # command: boblink -> replies with bot invite link
    if message.content == 'boblink':
         await message.channel.send(
            f'https://discordapp.com/oauth2/authorize?&client_id={bot.user.id}&scope=bot&permissions=0')

    # command: .srgiveadmin [@mention] (owner and guild members with manage guild permissions only)
    if message.content.startswith('.srgiveadmin'):
        if message.author.id == discord_owner_id or message.author.guild_permissions.manage_guild:
            logger.info(f'{message.content} by {message.author} in {ds}')

            if len(message.content.split(' ')) != 2:
                await message.channel.send(f'Syntax: `.srgiveadmin @mention`')

            else:
                discord_mention = message.content.split(' ')[1]
                discord_user_id = ''.join(i for i in discord_mention if i.isdigit())

                if db.discord_admin_on_channel(message.channel.id, discord_user_id):
                    await message.channel.send(f'{discord_mention} is already an admin')
                else:
                    if db.discord_admin_add_to_channel(message.channel.id, discord_user_id, bobhelper.utcnow()):
                        await message.channel.send(f'{discord_mention} - welcome to the higher ups')

    # command: .srtakeadmin [@mention] (owner and guild members with manage guild permissions only)
    if message.content.startswith('.srtakeadmin'):
        if message.author.id == discord_owner_id or message.author.guild_permissions.manage_guild:
            logger.info(f'{message.content} by {message.author} in {ds}')

            if len(message.content.split(' ')) != 2:
                await message.channel.send(f'{message.author.mention} Syntax: `.srtakeadmin @mention`')

            else:
                discord_mention = message.content.split(' ')[1]
                discord_user_id = ''.join(i for i in discord_mention if i.isdigit())

                if db.discord_admin_on_channel(message.channel.id, discord_user_id):
                    if db.discord_admin_delete_from_channel(message.channel.id, discord_user_id):
                        await message.channel.send(f'{discord_mention} removed as **admin** on **{bot.get_channel(message.channel.id)}**')
                else:
                        await message.channel.send(f'{discord_mention} is not an **admin** on **{bot.get_channel(message.channel.id)}**')

    # command: .sradd [nick] [battletag] -> add [battletag] as [nick] to leaderboard on current discord_channel
    if message.content.startswith('.sradd'):
        logger.info(f'{message.content} by {message.author} in {ds}')

        if len(message.content.split(' ')) != 3:
            await message.channel.send(f'{message.author.mention} Syntax: `.sradd nickname battletag#999` - Example: `.sradd Chaos Chaos#1999`')

        else:
            nickname = message.content.split(' ')[1]
            battletag = message.content.split(' ')[2].replace('#', '-')

            player = await owplayer.get(battletag)

            # check if player exists on battlenet
            if player:
                logger.debug(f'{battletag} found on battlenet')

                # check if player exists in database
                if db.player_exists(battletag):
                    logger.debug(f'{battletag} found in players db')
                else:
                    if db.player_insert(battletag, bobhelper.utcnow()):
                        logger.info(f'{battletag} added to players db')

                # check if player is already added on discord channel
                if db.discord_player_is_on_channel(battletag, message.channel.id):
                    logger.info(f'{battletag} already added on {ds}')
                    await message.channel.send(f'{message.author.mention} **{battletag}** already added!')
                else:
                    if db.discord_player_add_to_channel(message.channel.id, battletag, nickname, message.author.id, bobhelper.utcnow()):
                        logger.info(f'{battletag} added as {nickname} on {ds}')
                        await message.channel.send(f'{message.author.mention} **{battletag}** added as **{nickname}**')
            else:
                logger.info(f'{battletag} not found on battlenet')
                await message.channel.send(f'{message.author.mention} **{battletag}** not found on battlenet - make sure the battletag is **CaSeSeNiTiVe#1234**')

    # command: .srdel [battletag] -> removes [battletag] for leaderboard on current discord_channel
    if message.content.startswith('.srdel'):
        logger.info(f'{message.content} by {message.author} in {ds}')

        if len(message.content.split(' ')) != 2:
            await message.channel.send(f'{message.author.mention} Syntax: `.srdel battletag#999` - Example: `.sradd Chaos#1999`')

        else:
            battletag = message.content.split(' ')[1].replace('#', '-')

            allow = False

            if db.discord_user_is_allowed_delete(battletag, message.author.id):
                allow = True

            # check if message author is owner, har manage server or is admin on channel
            if (message.author.id == discord_owner_id or
                message.author.guild_permissions.manage_guild or
                db.discord_admin_on_channel(message.channel.id, message.author.id)):
                allow = True

            # check if player exists in database
            if db.player_exists(battletag):
                logger.debug(f'{battletag} found in players db')

                # check if discord user is allowed to delete
                if not allow:
                    await message.channel.send(f'{message.author.mention} not allowed')

                else:
                    # check if player is added on discord channel
                    if db.discord_player_is_on_channel(battletag, message.channel.id):
                        logger.debug(f'{battletag} found on {ds}')

                        if db.discord_player_delete_from_channel(battletag, message.channel.id):
                            logger.info(f'{message.author.mention} {battletag} deleted')
                            await message.channel.send(f'{message.author.mention} **{battletag}** removed')

                    else:
                        logger.info(f'{battletag} not found on {ds}')
                        await message.channel.send(f'{message.author.mention} **{battletag}** does not exist')
            else:
                logger.info(f'{battletag} not found in players db')
                await message.channel.send(f'{message.author.mention} **{battletag}** does not exist')

    if message.content.startswith('.leaderboards'):
        logger.info(f'{message.content} by {message.author} in {ds}')

            # check if message author is owner, har manage server or is admin on channel
        if (message.author.id == discord_owner_id or
            message.author.guild_permissions.manage_guild or
            db.discord_admin_on_channel(message.channel.id, message.author.id)):

            cid = message.content.split(' ')[1] if len(message.content.split(' ')) == 2 else message.channel.id

            discord_embed = build_discord_leaderboard_embed(cid)
            if discord_embed is not False:
                await message.channel.send(embed=discord_embed)

def build_discord_leaderboard_embed(discord_channel_id):
    leaderboard = db.get_leaderboard(discord_channel_id)
    discord_names = db.discord_channel_names(discord_channel_id)
    if len(leaderboard) == 0 or not discord_names:
        return False

    server_name = discord_names['serverName']
    channel_name = discord_names['channelName']
    leaderboard_url =  f"{web_base_url}{discord_names['short']}"

    embed=discord.Embed(
        title=f':trophy: Leaderboards for {channel_name} @ {server_name} :trophy:',
        description=f'use command **boblink** to invite B.o.B to your own server.\n`.sradd [nick] [battletag]` to join the leaderboards!')

    embed_rank_table = ''
    i = 0
    for i, player in enumerate(leaderboard):
        if i >= 10:
            break

        # set custom emjois for roles in leaderboard [print(l) for l in message.guild.emojis]
        role_emoji = bobhelper.emojis_replace(player['maxRole'])
        hero_emoji = ''
        last_rank = False

        # try to get the most played hero for a role and replace it with a hero emoji
        try:
            if player['maxRole'] == 'damage':
                hero_emoji = bobhelper.emojis_replace(player['damageHeroes'].split(' ')[0])
                last_rank = db.rank_history_get_last(player['battletag'], 'damageRank')

            if player['maxRole'] == 'tank':
                hero_emoji = bobhelper.emojis_replace(player['tankHeroes'].split(' ')[0])
                last_rank = db.rank_history_get_last(player['battletag'], 'tankRank')

            if player['maxRole'] == 'support':
                hero_emoji = bobhelper.emojis_replace(player['supportHeroes'].split(' ')[0])
                last_rank = db.rank_history_get_last(player['battletag'], 'supportRank')

        except Exception as e:
            print(e)

        battletag_short = player['battletag'].split('-')[:-1]
        entry = f"\n{i+1}. {hero_emoji} **{player['nickname']}** ({' '.join(battletag_short)}){role_emoji}**{player['maxRank']}**"
        
        if last_rank is not False:
            diff_rank = player['maxRank'] - last_rank
            entry +=  f' (+{diff_rank})' if diff_rank > 0 else f' ({diff_rank})'

        embed_rank_table += entry

        if i % 10 == 0 and i >= 5:
            embed.add_field(name=f'\u200B', value=f'{embed_rank_table}', inline=False)
            embed_rank_table = ''

    if len(embed_rank_table) > 0:
        embed.add_field(name=f'\u200B', value=f'{embed_rank_table}', inline=False)

    embed.add_field(name=f'\u200B', value=f'**[SEE FULL LIST]({leaderboard_url})**', inline=False)
    print(len(embed))

    return embed if i >= 4 else False

async def update_players_db():
    await asyncio.sleep(10)

    while True:

        players = db.player_get_battletags()
        count_total = len(players)
        count_ok = 0
        count_fail = 0
        count_404 = 0
        count_private = 0

        for i, player in enumerate(players):

            battletag = player['battletag']
            status = 'FAIL'

            if await owplayer.get(battletag):

                old_player_stats = db.player_get(battletag)

                if owplayer.gamesPlayed != old_player_stats['gamesPlayed']:
                    lastGamePlayed = bobhelper.utcnow()
                else:
                    lastGamePlayed = old_player_stats['lastGamePlayed']

                if lastGamePlayed is None or lastGamePlayed is '0':
                    lastGamePlayed = bobhelper.utcnow()

                data = {
                'damageRank':       owplayer.get_roleRank('damage'),
                'tankRank':         owplayer.get_roleRank('tank'),
                'supportRank':      owplayer.get_roleRank('support'),
                'gamesLost':        owplayer.gamesLost,
                'gamesPlayed':      owplayer.gamesPlayed,
                'gamesTied':        owplayer.gamesTied,
                'gamesWon':         owplayer.gamesWon,
                'timePlayed':       owplayer.timePlayed,
                'private':          owplayer.private,
                'lastGamePlayed':   lastGamePlayed,
                'apiLastChecked':   bobhelper.utcnow(),
                'apiLastStatus':    owplayer.http_last_status,
                }

                # get sorted hero list (by time played)
                sorted_heroes = owplayer.sorted_heroes
                if sorted_heroes is not False:

                    if len(sorted_heroes['damage_heroes']) > 0:
                        data['damageHeroes'] = ' '.join(sorted_heroes['damage_heroes'])

                    if len(sorted_heroes['tank_heroes']) > 0:
                        data['tankHeroes'] = ' '.join(sorted_heroes['tank_heroes'])

                    if len(sorted_heroes['support_heroes']) > 0:
                        data['supportHeroes'] = ' '.join(sorted_heroes['support_heroes'])

                logger.debug(f'{battletag} data: {data}')

                if db.player_update(battletag, data):
                    if owplayer.gamesPlayed != old_player_stats['gamesPlayed']:
                            if db.rank_history_insert(battletag):
                                logger.debug(f'saved rankHistory for {battletag}')
                    status = 'OK'
                    count_ok += 1

                if owplayer.private:
                    status = 'private'
                    count_private += 1
            else:
                if db.player_update(battletag, {'apiLastStatus': owplayer.http_last_status}):
                    status = f'failed to get player from api - {owplayer.http_last_status}'
                    count_fail += 1 

            if owplayer.http_last_status == 404:
                status = '404 (not found)'
                count_404 += 1

            out = f'{battletag:<30} {status:<15} [{i}/{count_total} ok:{count_ok} fail:{count_fail} private:{count_private} 404:{count_404}]'

            if status == 'FAIL':
                logger.critical(out)
            else:
                logger.debug(out)

        # sleep between loops
        await asyncio.sleep(sleep_between_loops)

# update db
async def discord_save_channels():
    while True:
        for server in bot.guilds:
            for channel in server.channels:
                if channel.type == discord.ChannelType.text:
                    # hashlib + re - MOVE THIS TO DB PY?
                    # generate unique ID. assume no collision
                    sha1 = hashlib.sha1(str(channel.id).encode('utf-8'))
                    result = base64.b64encode(sha1.digest())
                    regex = re.compile('[^a-zA-Z]')
                    short_id = regex.sub('', str(result)[0:6])

                    if db.discord_channel_exist(channel.id):
                        db.discord_channel_update(server.id, server.name, channel.id, channel.name, short_id)
                    else:
                        db.discord_channel_insert(server.id, server.name, channel.id, channel.name, short_id)

        await asyncio.sleep(180)


# schedule: daily leaderboards ## ADD MORE VERBOSE OUTPUT TO CONSOLE
## need fix - THIS WILL NOT WORK IF BOT IS STARTED SAME DAY SINCE current = now.day etc
async def post_daily_leaderboards():
    await asyncio.sleep(10)
    
    current = bobhelper.utcnow().day

    while True:
        now = bobhelper.utcnow()

        if now.hour >= 20:
            if now.day != current:
                logger.info(f'seems we have a new day on our hands! day changed from {current} to {now.day}')
                discord_channel_ids = db.discord_get_channel_ids_for_leaderboards()
                
                for cid in discord_channel_ids:
                    discord_embed = build_discord_leaderboard_embed(cid['channelId'])
                    
                    if discord_embed is not False:
                        channel = bot.get_channel(cid['channelId'])

                        if channel is not None:
                            message = '**A NEW DAY!** Leaderboards are posted at 10PM UTC!'
                            await channel.send(message, embed=discord_embed)
                
                current = now.day

        await asyncio.sleep(60)


if __name__ == '__main__':

    # get config file
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='configfile (default: config.ini)', default='config.ini')

    config_file = parser.parse_args().config

    if not os.path.isfile(config_file):
        print(f'!!! CONFIG FILE NOT FOUND: {config_file}')
        sys.exit(0)

    # read config file
    cf = configparser.ConfigParser()
    cf.read(config_file)

    loglevel = cf.get('general', 'loglevel')
    database_file = cf.get('general', 'database_file')
    ignore_time = int(cf.get('general', 'ignore_matches_older_than_hours'))

    base_dir = pathlib.Path(__file__).resolve().parent
    logs_dir = base_dir.joinpath(cf.get('paths', 'logs'))

    sleep_between_loops = int(cf.get('timers', 'sleep_between_loops'))

    discord_owner_id = int(cf.get('discord', 'owner_id'))

    web_base_url = cf.get('web', 'base_url')

    # create logs directory
    pathlib.Path(logs_dir).mkdir(parents=True, exist_ok=True)
    
    # create logger
    logger = logging.getLogger('bob')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(name)s[%(process)d] %(levelname)7s: %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.getLevelName(loglevel))
    logger.addHandler(handler)

    # file logger
    fh = TimedRotatingFileHandler('logs/bob.log', when="d", interval=1, backupCount=60)
    fh.setLevel(logging.DEBUG)
    
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # start app
    logger.info(f'loglevel: {loglevel}')
    logger.info(f'config file: {config_file}')
    logger.info(f'database file: {database_file}')
    logger.info(f'logs directory: {logs_dir}')
    logger.info(f'discord owner: {discord_owner_id}')
    logger.info(f'web base url: {web_base_url}')
    logger.info(f'----------------------')
    
    try:
        bobhelper = BobHelper()
        db = BobDb(database_file)
        owplayer = OWPlayer()

        bot.loop.create_task(update_players_db())
        bot.loop.create_task(discord_save_channels())
        bot.loop.create_task(post_daily_leaderboards())

        bot.run(cf.get('discord', 'token'))
    
    except KeyboardInterrupt:
        sys.exit(0)
