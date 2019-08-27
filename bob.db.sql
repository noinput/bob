BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "rankHistory" (
	"dateUtc"	TEXT,
	"battletag"	TEXT,
	"damageRank"	INTEGER,
	"tankRank"	INTEGER,
	"supportRank"	INTEGER,
	"gamesLost"	INTEGER,
	"gamesPlayed"	INTEGER,
	"gamesTied"	INTEGER,
	"gamesWon"	INTEGER,
	"timePlayed"	TEXT,
	FOREIGN KEY("battletag") REFERENCES "players"("battletag") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "players" (
	"battletag"	TEXT UNIQUE,
	"damageHeroes"	TEXT,
	"damageRank"	INTEGER DEFAULT 1,
	"tankHeroes"	TEXT,
	"tankRank"	INTEGER DEFAULT 1,
	"supportHeroes"	TEXT,
	"supportRank"	INTEGER DEFAULT 1,
	"gamesLost"	INTEGER DEFAULT 0,
	"gamesPlayed"	INTEGER DEFAULT 0,
	"gamesTied"	INTEGER DEFAULT 0,
	"gamesWon"	INTEGER DEFAULT 0,
	"timePlayed"	TEXT,
	"private"	TEXT,
	"lastGamePlayed"	TEXT,
	"apiLastChecked"	TEXT,
	"apiLastStatus"	TEXT,
	"addedDateUtc"	TEXT
);
CREATE TABLE IF NOT EXISTS "discord_channels" (
	"serverId"	TEXT,
	"serverName"	TEXT,
	"channelId"	TEXT UNIQUE,
	"channelName"	TEXT,
	"short"	TEXT
);
CREATE TABLE IF NOT EXISTS "discord_channel_admins" (
	"channelId"	INTEGER,
	"discordUser"	INTEGER,
	"addedDateUtc"	TEXT,
	FOREIGN KEY("channelId") REFERENCES "discord_channel_players"("channelId") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "botActions" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"dateUtc"	TEXT,
	"action"	TEXT,
	"isCompleted"	TEXT
);
CREATE TABLE IF NOT EXISTS "seasons" (
	"season"	INTEGER,
	"startDateUtc"	TEXT,
	"endDateUtc"	TEXT
);
CREATE TABLE IF NOT EXISTS "discord_channel_players" (
	"channelId"	INTEGER,
	"battletag"	TEXT,
	"nickname"	TEXT,
	"addedByDiscordUser"	TEXT,
	"addedDateUtc"	TEXT,
	FOREIGN KEY("battletag") REFERENCES "players"("battletag") ON DELETE CASCADE
);
COMMIT;
