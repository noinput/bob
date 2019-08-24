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
	
	def discord_user_is_allowed_delete(self, battletag, discord_user_id):
		sql = 'SELECT battletag FROM discord_channels WHERE battletag=(?) AND addedByDiscordUser=(?)'
		row = self.cursor.execute(sql, (battletag, discord_user_id)).fetchall()

		if len(row) > 0:
			return True
		else:
			return False