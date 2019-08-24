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

			players.battletag,
			players.damageHeroes,
			MAX(players.damageRank) as damageRank,
			players.tankHeroes,
			MAX(players.tankRank) as tankRank,
			players.supportHeroes,
			MAX(players.supportRank) as supportRank,
			players.gamesLost,
			players.gamesPlayed,
			players.gamesTied,
			players.timePlayed,
			players.private,
			players.lastGamePlayed,
			players.apiLastChecked,
			players.apiLastStatus,
			players.addedDateUtc,

			MAX(players.damageRank, players.tankRank, players.supportRank) as dmg,

		CASE
			WHEN damageRank > tankRank AND damageRank > supportRank THEN damageRank
			WHEN tankRank > damageRank AND tankRank > supportRank THEN tankRank
			WHEN supportRank > damageRank AND supportRank > tankRank THEN supportRank
			ELSE '0'
		END AS dmgScore,
		
		CASE
			WHEN damageRank > tankRank AND damageRank > supportRank THEN 0
			WHEN tankRank > damageRank AND tankRank > supportRank THEN 1
			WHEN supportRank > damageRank AND supportRank > tankRank THEN 2
			ELSE -1
		END AS dmgType
	
		FROM
  			discord_channels
  		INNER JOIN players ON discord_channels.battletag = players.battletag
		WHERE
			discord_channels.channelId=(?)

		ORDER BY
			dmgScore DESC
		'''
		row = self.cursor.execute(sql, (discord_channel_id, )).fetchall()
"""
		GROUP BY
			discord_channels.nickname
"""
		rank = 1
		nicks = []
		if len(row) > 0:
			for i, r in enumerate(row):
				if r['nickname'] not in nicks:
					print(i, r['battletag'], r['nickname'], r['apiLastStatus'], 
						r['damageRank'], r['tankRank'], r['supportRank'], r['dmg'])
					nicks.append(r['nickname'])
					print(nicks)
					rank += 1

		print(len(row))

db = BobDb('bob_dummy.db')

overwatch_norge = 303681642126376961
db.get_leaderboard(overwatch_norge)


"""
Hi. 
I have two tables. `players` and `discord_channels`. 

The players table holds the relevant:
battletag (unique player name), rank, games played, time played, etc

the discord_channels table holds:
battletag, nickname, discordChannelId

- a player can be added on multiplie discord channels with different nicknames - but relating to unique battletag in players table.
- a player can have multiplie battletags - but the same nickname (to avoid multiplie entries on a leaderboard for smurf accounts)

What im trying to do is get a leaderboard list based on these conditions
- a unique list pr discord channel id
- i want to sort the list by the MAX of any of the values damageRank, tankRank, supportRank
player1 (nickname: David) is ranked damage: 4300 tank: 4000, support: 3500
player2 (nickname: Joe) is ranked damage: 3800, tank: 4100, support: 4100
player3 (nickname: Joe) is ranked damage: 3800, tank: 4100, support: 4500

the list would look like this:
player3 - 4500 (support)
player1 - 4200 (damage)

** player2 (would not show since player3 is also called Joe but has a higher rank)
"""