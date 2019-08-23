import sqlite3

class BobDb:

	def __init__(self, db):
		self.db = db
		self.con = sqlite3.connect(self.db)
		self.con.row_factory = sqlite3.Row
		self.cursor = self.con.cursor()

	def _commit(self):
		self.con.commit()

	def get_leaderboard(self, discord_channel_id=0):
		sql = '''
		SELECT 
			discord_channels.battletag,
			discord_channels.nickname,
			discord_channels.channelId,
			
			players.damageHeroes,
			MAX(players.damageRank),
			players.tankHeroes,
			MAX(players.tankRank),
			players.supportHeroes,
			MAX(players.supportRank),
			players.gamesLost,
			players.gamesPlayed,
			players.gamesTied,
			players.timePlayed,
			players.private,
			players.lastGamePlayed,
			players.apiLastChecked,
			players.apiLastStatus,
			players.addedDateUtc

		FROM
			discord_channels
		INNER JOIN players ON discord_channels.battletag = players.battletag	
		WHERE
			discord_channels.channelId=(?)
		GROUP BY
			discord_channels.nickname
		ORDER BY 
			players.damageRank
		'''
		row = self.cursor.execute(sql, (discord_channel_id, )).fetchall()

		if len(row) > 0:
			for r in row:
				print(r['battletag'], r['nickname'], r['apiLastStatus'])

		print(len(row))

db = BobDb('bob.db')

db.get_leaderboard()
dev_channel = 613551977455943680
db.get_leaderboard(dev_channel)

overwatch_norge = 303681642126376961
db.get_leaderboard(overwatch_norge)
