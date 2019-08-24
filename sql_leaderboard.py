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
			players.damageRank,
			players.tankHeroes,
			players.tankRank,
			players.supportHeroes,
			players.supportRank,
			players.gamesLost,
			players.gamesPlayed,
			players.gamesTied,
			players.timePlayed,
			players.private,
			players.lastGamePlayed,
			players.apiLastChecked,
			players.apiLastStatus,
			players.addedDateUtc,

			MAX(players.damageRank, players.tankRank, players.supportRank) as dmg

		FROM
			discord_channels
		INNER JOIN players ON discord_channels.battletag = players.battletag	
		WHERE
			discord_channels.channelId=(?)
		ORDER BY
			CAST(dmg AS int) DESC
		'''
		row = self.cursor.execute(sql, (discord_channel_id, )).fetchall()

		rank = 1
		nicks = []
		if len(row) > 0:
			for i, r in enumerate(row):
				if r['nickname'] not in nicks:
					print(rank, r['battletag'], r['nickname'], r['apiLastStatus'], 
						r['damageRank'], r['tankRank'], r['supportRank'], r['dmg'])
					nicks.append(r['nickname'])
					rank += 1
		print(len(row))

db = BobDb('bob_dummy.db')

overwatch_norge = 303681642126376961
db.get_leaderboard(overwatch_norge)