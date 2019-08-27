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

    def discord_player_add_to_channel(self, discord_channel_id, battletag, nickname, discord_user_id, added_date_utc):
        sql = '''
        INSERT INTO discord_channel_players (
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
                discord_user_id,
                added_date_utc))
            self._commit()
            return True

        except Exception as e:
            print(f'{e}')
            return False

    def discord_player_delete_from_channel(self, battletag, discord_channel_id):
        sql = 'DELETE FROM discord_channel_players WHERE battletag=(?) AND channelId=(?)'
        self.cursor.execute(sql, (battletag, discord_channel_id))
        self._commit()
        return True
    
    def discord_player_is_on_channel(self, battletag, discord_channel_id):
        sql = 'SELECT battletag FROM discord_channel_players WHERE battletag=(?) AND channelId=(?)'
        row = self.cursor.execute(sql, (battletag, discord_channel_id)).fetchall()

        return True if len(row) > 0 else False
    
    def discord_admin_add_to_channel(self, discord_channel_id, discord_user_id, added_date_utc):
        sql = '''
        INSERT INTO discord_channel_admins (
        channelId,
        discordUser,
        addedDateUtc)
        VALUES (?, ?, ?)
        '''
        try:
            self.cursor.execute(sql, (
                discord_channel_id,
                discord_user_id,
                added_date_utc))
            self._commit()
            return True

        except Exception as e:
            print(f'{e}')
            return False
    
    def discord_admin_delete_from_channel(self, discord_channel_id, discord_user_id):
        sql = 'DELETE FROM discord_channel_admins WHERE channelId=(?) AND discordUser=(?)'
        self.cursor.execute(sql, (discord_channel_id, discord_user_id))
        self._commit()
        return True
    
    def discord_admin_on_channel(self, discord_channel_id, discord_user_id):
        sql = 'SELECT discordUser FROM discord_channel_admins WHERE channelId=(?) AND discordUser=(?)'
        row = self.cursor.execute(sql, (discord_channel_id, discord_user_id)).fetchall()

        return True if len(row) > 0 else False

    def discord_user_is_allowed_delete(self, battletag, discord_user_id):
        sql = 'SELECT battletag FROM discord_channel_players WHERE battletag=(?) AND addedByDiscordUser=(?)'
        row = self.cursor.execute(sql, (battletag, discord_user_id)).fetchall()

        if len(row) > 0:
            return True
        else:
            return False
    
    #testx = db.discord_channel_names(message.channel.id)
    #print(testx['serverName'], testx['channelName'])
    def discord_channel_names(self, discord_channel_id):
        sql = 'SELECT * FROM discord_channels WHERE channelId=(?)'
        row = self.cursor.execute(sql, (discord_channel_id, )).fetchall()

        return row[0] if len(row) > 0 else False

    def discord_channel_exist(self, discord_channel_id):
        sql = 'SELECT channelId FROM discord_channels WHERE channelId=(?)'
        row = self.cursor.execute(sql, (discord_channel_id, )).fetchall()

        return True if len(row) > 0 else False

    def discord_channel_insert(self, discord_server_id, discord_server_name, discord_channel_id, discord_channel_name):
        sql = '''
        INSERT INTO discord_channels (
            serverId,
            serverName,
            channelId,
            channelName)
        VALUES (?, ?, ?, ?)
        '''
        try:
            self.cursor.execute(sql, (
                discord_server_id,
                discord_server_name,
                discord_channel_id,
                discord_channel_name))
            self._commit()
            return True

        except Exception as e:
            print(f'{e}')
            return False
    
    def discord_channel_update(self, discord_server_id, discord_server_name, discord_channel_id, discord_channel_name):
        sql = '''
        UPDATE discord_channels SET
            serverId=(?),
            serverName=(?),
            channelId=(?),
            channelName=(?)
        WHERE
            channelId=(?)'''

        try:
            self.cursor.execute(sql, (
                discord_server_id, discord_server_name, discord_channel_id, discord_channel_name, discord_channel_id))
            self._commit()
            return True
        
        except Exception as e:
            print(f'{e}')
            return False

    # default for damageRank, tankRank and supportRank has to be 1 to work with sqlite MAX 
    def get_leaderboard(self, discord_channel_id=0):
        sql = '''
        SELECT
            discord_channel_players.battletag,
            discord_channel_players.nickname,
            discord_channel_players.channelId,

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

            MAX(players.damageRank, players.tankRank, players.supportRank) as dmg,
            
            CASE
                WHEN players.damageRank > players.tankRank AND players.damageRank > players.supportRank THEN 'damage'
                WHEN players.tankRank > players.damageRank AND players.tankRank > players.supportRank THEN 'tank'
                WHEN players.supportRank > players.damageRank AND players.supportRank > players.tankRank THEN 'support'
                ELSE False
            END AS dmgType
        
        FROM
            discord_channel_players
        INNER JOIN players ON discord_channel_players.battletag = players.battletag    
        WHERE
            discord_channel_players.channelId=(?)
        ORDER BY
            CAST(dmg AS int) DESC
        '''

        row = self.cursor.execute(sql, (discord_channel_id, )).fetchall()

        nicks = []
        leaderboard = []

        if len(row) > 0:
            for player in row:
                if player['nickname'] not in nicks:
                    leaderboard.append(player)
                    nicks.append(player['nickname'])

        return leaderboard