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

from logging.handlers import TimedRotatingFileHandler

from resources.bobdb import BobDb
from resources.owplayer import OWPlayer


bot = discord.Client()

@bot.event
async def on_ready():
		logger.info(f'logged in as {bot.user.name} - Discord.py: v{discord.__version__}')

@bot.event
async def on_message(message):
	ds = f'{bot.get_guild(message.guild.id)} @ {bot.get_channel(message.channel.id)}'
	utcnow = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

	# command: boblink -> replies with bot invite link
	if message.content == 'boblink':
		 await message.channel.send(
		 	f'https://discordapp.com/oauth2/authorize?&client_id={bot.user.id}&scope=bot&permissions=0')

	# command: +follow [player] -> start following 'player' on discord.channel
	if message.content.startswith('.sradd'):
		logger.info(f'{message.content} by {message.author} in {ds}')

		if len(message.content.split(' ')) != 3:
			await message.channel.send(f'{message.author.mention} Syntax: `.sradd nickname battletag#999` - Example: `.sradd Chaos Chaos#1999`')
			return

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
			await message.channel.send(f'{message.author.mention} **{battletag}** not found on battlenet')

	# command: -follow [player] -> stop following 'player' on discord.channel
	if message.content.startswith('.srdel'):
		logger.info(f'{message.content} by {message.author} in {ds}')

		if len(message.content.split(' ')) != 2:
			await message.channel.send(f'{message.author.mention} Syntax: `.srdel battletag#999` - Example: `.sradd Chaos#1999`')
			return

		allow = False
		battletag = message.content.split(' ')[1].replace('#', '-')
		#print((message.author.server_permissions.manage_server))
		
		if db.discord_user_is_allowed_delete(battletag, message.author.id):
			print('is addedbydiscorduser')
			allow = True
		if message.author.id == discord_owner_id:
			print('owner')
			allow = True

		#if not message.author.server_permissions.manage_server or not db.discord_user_is_allowed_delete(battletag, message.author.id):

		## ADD CHECK IF USER IN EXISTS IN DB
		if not db.discord_user_is_allowed_delete(battletag, message.author.id):
			await message.channel.send(f'{message.author.mention} not allowed')
			return

		##### WORK IN PROGRESS DISCORD PREMISSIONS

		# check if player exists in database
		if db.player_exists(battletag):
			logger.debug(f'{battletag} found in players db')

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
		
		for i, player in enumerate(players):
			
			battletag = player['battletag']
			status = 'FAIL'
			
			if await owplayer.get(battletag):
				
				utcnow = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

				old_player_stats = db.player_get(battletag)

				if owplayer.gamesPlayed != old_player_stats['gamesPlayed']:
					
					lastGamePlayed = utcnow
					logger.info(f'## A NEW GAME WAS PLAYED !! {battletag} ##')
					logger.info(old_player_stats['lastGamePlayed'])
					logger.info(type(old_player_stats['lastGamePlayed']))
					logger.info(type(utcnow))
					if isinstance(old_player_stats['lastGamePlayed'], datetime.datetime):
						print('YES!!!')
						then = old_player_stats['lastGamePlayed']
						duration = utcnow - then
						mins, secs = divmod(int(duration.total_seconds()), 60)
						logger.debug(f'last match updated was {mins}mins {secs}seconds ago')
					# THIS CAN BE REMOVED WHEN NOT DEBUGGING!!! ##
					else:
						then = utcnow
						logger.info(then)
						logger.info(f'match played was first change seen saved lastGamePlayed as {lastGamePlayed} for {battletag}')
				else:
					lastGamePlayed = old_player_stats['lastGamePlayed']
					count_inactive += 1
				
				data = {
				'damageRank':		owplayer.get_roleRank('damage'),
				'tankRank':			owplayer.get_roleRank('tank'),
				'supportRank':		owplayer.get_roleRank('support'),
				'gamesLost':		owplayer.gamesLost,
				'gamesPlayed':		owplayer.gamesPlayed,
				'gamesTied':		owplayer.gamesTied,
				'timePlayed':		owplayer.timePlayed,
				'private':			owplayer.private,
				'lastGamePlayed':	lastGamePlayed,
				'apiLastChecked':	utcnow,
				'apiLastStatus':	owplayer.http_last_status,
				}
				
				logger.debug(f'datadict: {data}')

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
	logger.setLevel(logging.getLevelName(loglevel))

	handler = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s %(name)s[%(process)d] %(levelname)7s: %(message)s')
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	# file logger
	fh = TimedRotatingFileHandler('logs/bob.log', when="d", interval=1, backupCount=60)
	fh.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s %(name)s[%(process)d] %(levelname)7s: %(message)s')
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
