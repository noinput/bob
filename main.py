import asyncio
import argparse
import configparser
import datetime
import discord
import json
import logging
import os
import pathlib
import sys
import time
import re

from logging.handlers import TimedRotatingFileHandler

from resources.bobdb import BobDb
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
    utcnow = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

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
                    if db.discord_admin_add_to_channel(message.channel.id, discord_user_id, utcnow):
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
                    if db.player_insert(battletag, utcnow):
                        logger.info(f'{battletag} added to players db')

                # check if player is already added on discord channel
                if db.discord_player_is_on_channel(battletag, message.channel.id):
                    logger.info(f'{battletag} already added on {ds}')
                    await message.channel.send(f'{message.author.mention} **{battletag}** already added!')
                else:
                    if db.discord_player_add_to_channel(message.channel.id, battletag, nickname, message.author.id, utcnow):
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

            embed=discord.Embed(
                title=f':trophy: Leaderboards for {ds} :trophy:',
                description=f'use command **boblink** to invite B.o.B to your own server.\n`.sradd [nick] [battletag]` to join the leaderboards!')

            leaderboard = db.get_leaderboard(cid)

            embed_rank_table = ''

            for i, player in enumerate(leaderboard):
                if i >= 10:
                    break

                # set custom emjois for roles in leaderboard [print(l) for l in message.guild.emojis]
                role_emoji = emojis_replace(str(player['dmgType']))
                hero_emoji = ''

                # try to get the most played hero for a role and replace it with a hero emoji
                try:
                    if player['dmgType'] == 'damage':
                        hero_emoji = emojis_replace(player['damageHeroes'].split(' ')[0])

                    if player['dmgType'] == 'tank':
                        hero_emoji = emojis_replace(player['tankHeroes'].split(' ')[0])

                    if player['dmgType'] == 'support':
                        hero_emoji = emojis_replace(player['supportHeroes'].split(' ')[0])
                    #print(hero_emoji)
                except:
                    pass

                entry = f"\n{i+1}. {hero_emoji} **{player['nickname']}** ({player['battletag']}){role_emoji}**{player['dmg']}**"
                embed_rank_table += entry

                if i % 10 == 0 and i > 5:
                    embed.add_field(name=f'\u200B', value=f'{embed_rank_table}', inline=False)
                    embed_rank_table = ''

            if len(embed_rank_table) > 0:
                embed.add_field(name=f'\u200B', value=f'{embed_rank_table}', inline=False)

            await message.channel.send(embed=embed)

async def main():
    await asyncio.sleep(10)

    while True:

        players = db.player_get_battletags()
        count_total = len(players)
        count_ok = 0
        count_fail = 0
        count_404 = 0
        count_private = 0
        count_inactive = 0

        ## inactive and fail dupli count - intended or bug?
        for i, player in enumerate(players):

            battletag = player['battletag']
            status = 'FAIL'

            if await owplayer.get(battletag):

                utcnow = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                old_player_stats = db.player_get(battletag)

                if owplayer.gamesPlayed != old_player_stats['gamesPlayed']:

                    ## DEBUG OUTPUT - WE WILL USE THIS TO CALCULATE INACTIVITY
                    lastGamePlayed = utcnow

                    if isinstance(old_player_stats['lastGamePlayed'], datetime.datetime):
                        then = old_player_stats['lastGamePlayed']
                        duration = utcnow - then
                        mins, secs = divmod(int(duration.total_seconds()), 60)
                        logger.debug(f'last match updated was {mins}mins {secs}seconds ago')

                    ## memba to move this shit when not debugging
                    else:
                        then = utcnow
                        logger.info(then)
                        logger.info(f'match played was (FIRST CHANGE ON SEEN ON PROFILE) -> saved lastGamePlayed as {lastGamePlayed} for {battletag}')
                else:
                    lastGamePlayed = old_player_stats['lastGamePlayed']
                    count_inactive += 1

                if lastGamePlayed is None:
                    lastGamePlayed = utcnow

                data = {
                'damageRank':       owplayer.get_roleRank('damage'),
                'tankRank':         owplayer.get_roleRank('tank'),
                'supportRank':      owplayer.get_roleRank('support'),
                'gamesLost':        owplayer.gamesLost,
                'gamesPlayed':      owplayer.gamesPlayed,
                'gamesTied':        owplayer.gamesTied,
                'timePlayed':       owplayer.timePlayed,
                'private':          owplayer.private,
                'lastGamePlayed':   lastGamePlayed,
                'apiLastChecked':   utcnow,
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

            out = f'{battletag:<30} {status:<15} [{i}/{count_total} ok:{count_ok} inactive:{count_inactive} fail:{count_fail} private:{count_private} 404:{count_404}]'

            if status == 'FAIL':
                logger.critical(out)
            else:
                logger.info(out)

        # sleep between loops
        await asyncio.sleep(sleep_between_loops)

def emojis_replace(emoji):

    replace_map = {
        'damage': '<:owdamage:614835972210688000>',
        'support': '<:owsupport:614835972215144457>',
        'tank': '<:owtank:614835972315807754>',

        '^ashe$':       '<:owashe:614947399181271051>',
        'bastion':      '<:owbastion:614947399357562908>',
        'doomfist':     '<:owdoomfist:614947399055573008>',
        'genji':        '<:owgenji:614947399500300316>',
        'hanzo':        '<:hanzo:614947398900383745>',
        'junkrat':      '<:owjunkrat:614947399257030686>',
        'mccree':       '<:owmccree:614947399357431809>',
        'mei':          '<:owmei:614947399110230037>',
        'pharah':       '<:owpharah:614947399701626924>',
        'reaper':       '<:owreaper:614947399361757229>',
        'soldier76':    '<:owsoldier76:614947399303168025>',
        'sombra':       '<:owsombra:614947399273807872>',
        'symmetra':     '<:owsymmetra:614947399021887504>',
        'torbjorn':     '<:owtorbjorn:614947399781056532>',
        'tracer':       '<:owtracer:614947399017955341>',
        'widowmaker':   '<:owwidowmaker:614947399412088833>',

        'dVa':          '<:owdVa:614947399194116106>',
        'orisa':        '<:oworisa:614947399839776770>',
        'reinhardt':    '<:owreinhardt:614947399462551570>',
        'roadhog':      '<:owroadhog:614947399349305345>',
        'sigma':        '<:owsigma:614947399286128640>',
        'winston':      '<:owwinston:614947399265157124>',
        'wreckingBall': '<:owwreckingBall:614947399189921820>',
        'zarya':        '<:owzarya:614947399315488769>',

        'ana':          '<:owana:614947399130939392>',
        'baptiste':     '<:owbaptiste:614947398921486338>',
        'brigitte':     '<:owbrigitte:614947399806353427>',
        'lucio':        '<:owlucio:614947399042859035>',
        'mercy':        '<:owmercy:614947399265419284>',
        'moira':        '<:owmoira:614947399323877377>',
        'zenyatta':     '<:owzenyatta:614947399361757218>'}

    for k, v in replace_map.items():
        emoji = re.sub(k, v, emoji)

    return emoji

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
    
    try:
        db = BobDb(database_file)
        owplayer = OWPlayer()

        bot.loop.create_task(main())
        bot.run(cf.get('discord', 'token'))
    except KeyboardInterrupt:
        sys.exit(0)
