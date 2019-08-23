import sqlite3

class BobDb:

	def __init__(self, db):
		self.db = db
		self.con = sqlite3.connect(self.db)
		self.con.row_factory = sqlite3.Row
		self.cursor = self.con.cursor()

	def _commit(self):
		self.con.commit()

	def player_insert(self, battletag, added_date_utc):
		sql = '''
		INSERT INTO players (
		battletag,
		addedDateUtc)
		VALUES (
		?, ?)
		'''
		try:
			self.cursor.execute(sql, (
				battletag,
				added_date_utc))
			self._commit()
			return True
		
		except Exception as e:
			print(f'{e}')
			return False

	def player_update(self, battletag, data):
		update = ', '.join([f'{k}=(?)' for k in data.keys()])
		sql = f'UPDATE players SET {update} WHERE battletag=(?)'
		values = list(data.values())
		values.append(battletag)
		self.cursor.execute(sql, values)
		if self.cursor.rowcount > 0:
			self._commit()
			return True
		else:
			return False

	def player_delete(self, battletag):
		sql = 'DELETE FROM players WHERE battletag=(?)'
		self.cursor.execute(sql, (battletag, ))
		self._commit()
		return True
	
	def player_exists(self, battletag):
		sql = 'SELECT battletag FROM players WHERE battletag=(?)'
		row = self.cursor.execute(sql, (battletag, )).fetchall()
		
		return True if len(row) > 0 else False
	
	def player_get(self, battletag):
		sql = 'SELECT * FROM players WHERE battletag=(?)'
		row = self.cursor.execute(sql, (battletag, )).fetchall()
		
		return row[0] if len(row) > 0 else False

	def player_get_battletags(self):
		sql = 'SELECT battletag FROM players'
		row = self.cursor.execute(sql, ).fetchall()
		
		return row
	
	def discord_player_add_to_channel(self, discord_channel_id, battletag, nickname, discord_user, added_date_utc):
		sql = '''
		INSERT INTO discord_channels (
		channelId,
		battletag,
		nickname,
		addedByDiscordUser,
		addedDateUtc)
		VALUES (
		?, ?, ?, ?, ?)
		'''
		try:
			self.cursor.execute(sql, (
				discord_channel_id,
				battletag,
				nickname,
				discord_user,
				added_date_utc))
			self._commit()
			return True

		except Exception as e:
			print(f'{e}')
			return False

	def discord_player_delete_from_channel(self, battletag, discord_channel_id):
		sql = 'DELETE FROM discord_channels WHERE battletag=(?) AND channelId=(?)'
		self.cursor.execute(sql, (battletag, discord_channel_id))
		self._commit()
		return True
	
	def discord_player_is_on_channel(self, battletag, discord_channel_id):
		sql = 'SELECT battletag FROM discord_channels WHERE battletag=(?) AND channelId=(?)'
		row = self.cursor.execute(sql, (battletag, discord_channel_id)).fetchall()

		return True if len(row) > 0 else False
	
	### EDITED TO HERE
	def player_update_name(self, account_id, player_name):
		if self.player_exists(account_id):
			sql = 'UPDATE players SET playerName=(?) WHERE accountId=(?)'
			row = self.cursor.execute(sql, (player_name, account_id))

			self._commit()
			return True

	def player_follow_insert(self, discord_channel_id, account_id):
		sql = '''
		INSERT INTO discord_channels (channelId, accountId)
		VALUES (?, ?)
		'''
		self.cursor.execute(sql, (discord_channel_id, account_id))

		self._commit()
		return True

	def player_follow_delete(self, discord_channel_id, account_id):
		sql = 'DELETE FROM discord_channels WHERE channelId=(?) AND accountId=(?)'
		self.cursor.execute(sql, (discord_channel_id, account_id))
		self._commit()
		return True

	def player_follow_exists(self, discord_channel_id, account_id):
		sql = 'SELECT * FROM discord_channels WHERE channelId=(?) AND accountId=(?)'
		row = self.cursor.execute(sql, (discord_channel_id, account_id)).fetchone()
		
		if row and [len(row) > 0]:
			return True
		else:
			return False

	def player_match_exists(self, match_id, account_id):
		sql = 'SELECT * FROM player_matches WHERE matchId=(?) AND accountId=(?)'
		row = self.cursor.execute(sql, (match_id, account_id)).fetchone()

		if row and [len(row) > 0]:
			return True
		else:
			return False

	def player_match_insert(self, match_id, data):
		sql = '''
		INSERT INTO player_matches (
		matchId, 
		accountId,
		DBNOs,
		assists,
		boosts,
		damageDealt,
		deathType,
		headshotKills,
		heals,
		killPlace,
		killStreaks,
		kills,
		longestKill,
		name,
		playerId,
		revives,
		rideDistance,
		roadKills,
		swimDistance,
		teamKills,
		timeSurvived,
		vehicleDestroys,
		walkDistance,
		weaponsAcquired,
		winPlace)
		VALUES (
		?, ?, ?, ?, ?, ?, ?, ?, 
		?, ?, ?, ?, ?, ?, ?, ?, 
		?, ?, ?, ?, ?, ?, ?, ?, 
		?)
		'''
		try:
			self.cursor.execute(sql, (
				match_id,
				data['playerId'],
				data['DBNOs'],
				data['assists'],
				data['boosts'],
				data['damageDealt'],
				data['deathType'],
				data['headshotKills'],
				data['heals'],
				data['killPlace'],
				data['killStreaks'],
				data['kills'],
				data['longestKill'],
				data['name'],
				data['playerId'],
				data['revives'],
				data['rideDistance'],
				data['roadKills'],
				data['swimDistance'],
				data['teamKills'],
				data['timeSurvived'],
				data['vehicleDestroys'],
				data['walkDistance'],
				data['weaponsAcquired'],
				data['winPlace']))
			self._commit()
			return True

		except Exception as e:
			print(f'player_match_insert failed: {e}')
			return False
	
	def get_tracked_players(self):
		sql = 'SELECT accountId FROM players WHERE track=1'
		row = self.cursor.execute(sql).fetchall()

		if row and [len(row) > 0]:
			return row
		else:
			return False
	
	def get_player_name_from_disord_user(self, discord_user):
		sql = 'SELECT playerName FROM players WHERE discordUser=(?) LIMIT 1'
		row = self.cursor.execute(sql, (discord_user, )).fetchone()

		if row and [len(row) > 0]:
			return row[0]
		else:
			return False
	
	def get_account_ids_for_discord_channel(self, discord_channel):
		sql = f'SELECT accountId FROM discord_channels WHERE channelId=(?)'

		row = self.cursor.execute(sql, (discord_channel, )).fetchall()

		if row and [len(row) > 0]:
			return row
		else:
			return []

	def get_discord_channels_for_players(self, account_ids):
		search = ' OR '.join(['accountId=(?)' for account_id in account_ids])
		sql = f'SELECT DISTINCT channelId FROM discord_channels WHERE {search}'

		row = self.cursor.execute(sql, account_ids).fetchall()

		if row and [len(row) > 0]:
			return row
		else:
			return []

	def player_match_last_20_avg(self, account_id):
		sql = f'''
		SELECT
			avg(damageDealt) as damageDealt,
			avg(kills) as kills
		FROM
			(SELECT
			player_matches.matchId,
			player_matches.name,
			player_matches.kills,
			player_matches.damageDealt,
			matches.createdAt
		FROM
			player_matches
		INNER JOIN matches ON player_matches.matchId = matches.id
		WHERE player_matches.accountId=(?)
		ORDER BY matches.createdAt
		DESC
		LIMIT 20);
		'''
		row = self.cursor.execute(sql, (account_id, )).fetchone()

		if row and [len(row) > 0]:
			return row
		else:
			return False