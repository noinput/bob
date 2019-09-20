import sqlite3

from resources.bobhelper import BobHelper


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
        INSERT INTO discordChannelPlayers (
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
        sql = 'DELETE FROM discordChannelPlayers WHERE battletag=(?) AND channelId=(?)'
        self.cursor.execute(sql, (battletag, discord_channel_id))
        self._commit()
        return True
    
    def discord_player_is_on_channel(self, battletag, discord_channel_id):
        sql = 'SELECT battletag FROM discordChannelPlayers WHERE battletag=(?) AND channelId=(?)'
        row = self.cursor.execute(sql, (battletag, discord_channel_id)).fetchall()

        return True if len(row) > 0 else False
    
    def discord_admin_add_to_channel(self, discord_channel_id, discord_user_id, added_date_utc):
        sql = '''
        INSERT INTO discordChannelAdmins (
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
        sql = 'DELETE FROM discordChannelAdmins WHERE channelId=(?) AND discordUser=(?)'
        self.cursor.execute(sql, (discord_channel_id, discord_user_id))
        self._commit()
        return True
    
    def discord_admin_on_channel(self, discord_channel_id, discord_user_id):
        sql = 'SELECT discordUser FROM discordChannelAdmins WHERE channelId=(?) AND discordUser=(?)'
        row = self.cursor.execute(sql, (discord_channel_id, discord_user_id)).fetchall()

        return True if len(row) > 0 else False

    def discord_user_is_allowed_delete(self, battletag, discord_user_id):
        sql = 'SELECT battletag FROM discordChannelPlayers WHERE battletag=(?) AND addedByDiscordUser=(?)'
        row = self.cursor.execute(sql, (battletag, discord_user_id)).fetchall()

        if len(row) > 0:
            return True
        else:
            return False
    
    #testx = db.discord_channel_names(message.channel.id)
    #print(testx['serverName'], testx['channelName'])
    def discord_channel_names(self, discord_channel_id):
        sql = 'SELECT * FROM discordChannels WHERE channelId=(?)'
        row = self.cursor.execute(sql, (discord_channel_id, )).fetchall()

        return row[0] if len(row) > 0 else False

    def discord_channel_exist(self, discord_channel):
        sql = '''
        SELECT
            channelId 
        FROM 
            discordChannels 
        WHERE 
            channelId=(?)
        OR 
            short=(?)'''
        row = self.cursor.execute(sql, (discord_channel, discord_channel)).fetchall()

        return row[0] if len(row) > 0 else False

    def discord_channel_insert(self, discord_server_id, discord_server_name, discord_channel_id, discord_channel_name, short):
        sql = '''
        INSERT INTO discordChannels (
            serverId,
            serverName,
            channelId,
            channelName,
            short)
        VALUES (?, ?, ?, ?, ?)
        '''
        try:
            self.cursor.execute(sql, (
                discord_server_id,
                discord_server_name,
                discord_channel_id,
                discord_channel_name,
                short))
            self._commit()
            return True

        except Exception as e:
            print(f'{e}')
            return False
    
    def discord_channel_update(self, discord_server_id, discord_server_name, discord_channel_id, discord_channel_name, short):
        sql = '''
        UPDATE discordChannels SET
            serverId=(?),
            serverName=(?),
            channelId=(?),
            channelName=(?),
            short=(?)
        WHERE
            channelId=(?)'''

        try:
            self.cursor.execute(sql, (
                discord_server_id, discord_server_name, discord_channel_id, discord_channel_name, short, discord_channel_id))
            self._commit()
            return True
        
        except Exception as e:
            print(f'{e}')
            return False
    
    def discord_get_channel_ids_for_leaderboards(self):
        sql = 'SELECT DISTINCT channelId FROM discordChannelPlayers'
        row = self.cursor.execute(sql).fetchall()

        return row if len(row) > 0 else False

    def rank_history_insert(self, battletag):
        sql = '''
        INSERT INTO 
            rankHistory
        SELECT
            players.apiLastChecked,
            players.battletag,
            players.damageRank,
            players.tankRank,
            players.supportRank,
            players.gamesLost,
            players.gamesPlayed,
            players.gamesTied,
            players.gamesWon,
            players.timePlayed from players
        WHERE 
            battletag=(?)
            '''
        try:
            self.cursor.execute(sql, (battletag, ))
            self._commit()
            return True

        except Exception as e:
            print(f'{e}')
            return False
    
    def rank_history_get_last(self, battletag, role):
        sql = '''
        SELECT *
        FROM
            rankHistory
        WHERE
            battletag=(?)
            AND (rankHistory.damageRank > 1 OR rankHistory.tankRank > 1 OR rankHistory.supportRank > 1)
            AND rankHistory.gamesPlayed >= 5
            AND rankHistory.dateUtc >= date('now', '-1 day')
            AND rankHistory.dateUtc < date('now')
        ORDER BY dateUtc
        DESC
        LIMIT 1
            '''
        
        row = self.cursor.execute(sql, (battletag, )).fetchall()

        if len(row) > 0:
            for r in row:
                return r[role]

        return False

    # default for damageRank, tankRank and supportRank has to be 1 to work with sqlite MAX 
    def get_leaderboard(self, discord_channel_id=0):
        sql = '''
        SELECT
            discordChannelPlayers.battletag,
            discordChannelPlayers.nickname,
            discordChannelPlayers.channelId,

            players.damageHeroes,
            players.damageRank,
            players.tankHeroes,
            players.tankRank,
            players.supportHeroes,
            players.supportRank,
            players.gamesLost,
            players.gamesPlayed,
            players.gamesTied,
            players.gamesWon,
            players.timePlayed,
            players.private,
            players.lastGamePlayed,
            players.apiLastChecked,
            players.apiLastStatus,
            players.addedDateUtc,

            MAX(players.damageRank, players.tankRank, players.supportRank) as maxRank,
            
            CASE
                WHEN players.damageRank > players.tankRank AND players.damageRank > players.supportRank 
                        THEN 'damage'
                WHEN players.tankRank > players.damageRank AND players.tankRank > players.supportRank
                        THEN 'tank'
                WHEN players.supportRank > players.damageRank AND players.supportRank > players.tankRank
                        THEN 'support'
                ELSE False
            END AS maxRole
        
        FROM
            discordChannelPlayers
        INNER JOIN players ON discordChannelPlayers.battletag = players.battletag    
        WHERE
            discordChannelPlayers.channelId=(?)
            AND (players.damageRank > 1 OR players.tankRank > 1 OR players.supportRank > 1)
            AND players.gamesPlayed >= 5
            AND players.lastGamePlayed >= date('now','-7 day')
        ORDER BY
            CAST(maxRank AS int) DESC
        '''

        row = self.cursor.execute(sql, (discord_channel_id, )).fetchall()
        nicks = []
        leaderboard = []
        bobhelper = BobHelper()

        if len(row) > 0:
            for player in row:
                if player['nickname'] not in nicks:
                    #player['lastGamePlayedHuman'] = bobhelper.human_duration_since(player['lastGamePlayed'])
                    leaderboard.append(player)
                    nicks.append(player['nickname'])

        return leaderboard