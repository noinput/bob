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
	if message.content.startswith('.sradd '):
		nickname = message.content.split(' ')[1]
		battletag = message.content.split(' ')[2]

		logger.info(f'{message.content} by {message.author} in {ds}')

		player = await owplayer.get(battletag.replace('#', '-'))

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
				await message.channel.send(f'{message.author.mention} {battletag} already in db')
			else:
				if db.discord_player_add_to_channel(message.channel.id, battletag, nickname, message.author.id, utcnow):
					logger.info(f'{battletag} added as {nickname} on {ds}')
					await message.channel.send(f'{message.author.mention} {battletag} added as {nickname}')
		else:
			logger.info(f'{battletag} not found on battlenet')
			await message.channel.send(f'{message.author.mention} {battletag} not found on battlenet')

	# command: -follow [player] -> stop following 'player' on discord.channel
	if message.content.startswith('.srdel '):
		battletag = message.content.split(' ')[1]
		logger.info(f'{message.content} by {message.author} in {ds}')

		# check if player exists in database
		if db.player_exists(battletag):
			logger.debug(f'{battletag} found in players db')

			# check if player is added on discord channel
			if db.discord_player_is_on_channel(battletag, message.channel.id):
				logger.debug(f'{battletag} found on {ds}')
				
				if db.discord_player_delete_from_channel(battletag, message.channel.id):
					logger.info(f'{message.author.mention} {battletag} deleted')
					await message.channel.send(f'{message.author.mention} {battletag} deleted')

			else:
				logger.info(f'{battletag} not found on {ds}')
				await message.channel.send(f'{message.author.mention} **{battletag}** does not exist')
		else:
			logger.info(f'{battletag} not found in players db')
			await message.channel.send(f'{message.author.mention} **{battletag}** does not exist')

async def main():
	x = await owplayer.get('NOONE-221541')
	print('### COMPLETED ###')
	if x:
		print('tank:', owplayer.get_roleRank('tank'))
		print('support:', owplayer.get_roleRank('support'))
		print('damage', owplayer.get_roleRank('damage'))
		print('name:', owplayer.name)
		print('level:', owplayer.level)
		print('isPrivateProfile:', getattr(owplayer, 'private'))
		print('gamesLost', owplayer.gamesLost)
		print('gamesPlayed', owplayer.gamesPlayed)
		print('gamesTied', owplayer.gamesTied)
	else:
		print(owplayer.http_last_status)
	return False
	while True:
		if not db.get_tracked_players():
			await asyncio.sleep(sleep_between_loops)
			continue

		account_ids = [account_id['accountId'] for account_id in db.get_tracked_players()]

		# create a nested list sliced every 10th account for batch API requests
		account_ids_batch = [account_ids[x:x+10] for x in range(0, len(account_ids),10)]
		matches = []

		for accounts in account_ids_batch:
			matches += await hungrypubg.get_matchlist_from_many(accounts)
			await asyncio.sleep(sleep_between_batch)

		logger.debug(f'found {len(matches)} matches from {len(account_ids)} players')

		for match_id in matches:

			if db.match_exists(match_id):
				continue

			logger.info(f'fetching match {match_id}')
			data = await hungrypubg.get_match(match_id)

			if data:
				logger.info(f'insert to db {match_id}')
				db.match_insert(data['data'])

				logger.info(f'unpacking match {match_id}')
				await unpack_match(account_ids, data)
			else:
				logger.error(f'failed to get match {match_id}')

			# sleep between match requests - not ratelimited
			await asyncio.sleep(sleep_between_matches)

		# sleep between loops
		await asyncio.sleep(sleep_between_loops)

if __name__ == '__main__':

	# create logs directory
	pathlib.Path('logs/').mkdir(parents=True, exist_ok=True)

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

	pubg_api_key = cf.get('api', 'pubg_api_key')
	loglevel = cf.get('general', 'loglevel')
	database_file = cf.get('general', 'database_file')
	ignore_time = int(cf.get('general', 'ignore_matches_older_than_hours'))

	base_dir = pathlib.Path(__file__).resolve().parent
	matches_dir = base_dir.joinpath(cf.get('paths', 'matches'))

	sleep_between_loops = int(cf.get('sleep', 'sleep_between_loops'))
	sleep_between_matches = int(cf.get('sleep', 'sleep_between_matches'))
	sleep_between_batch = int(cf.get('sleep', 'sleep_between_batch'))

	# create logger
	logger = logging.getLogger('bob')
	logger.setLevel(logging.getLevelName(loglevel))

	handler = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s %(name)10s[%(process)d] %(levelname)7s: %(message)s')
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	# file logger
	fh = TimedRotatingFileHandler('logs/bob.log', when="d", interval=1, backupCount=60)
	fh.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s %(name)10s[%(process)d] %(levelname)7s: %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)

	# start app
	logger.info(f'loglevel: {loglevel}')
	logger.info(f'config file: {config_file}')
	logger.info(f'database file: {database_file}')
	logger.info(f'match files: {matches_dir}')

	try:
		db = BobDb(database_file)
		owplayer = OWPlayer()

		bot.loop.create_task(main())
		bot.run(cf.get('discord', 'token'))
	except KeyboardInterrupt:
		sys.exit(0)
