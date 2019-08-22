BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "players" (
	"battletag"	TEXT UNIQUE,
	"damageHeroes"	TEXT,
	"damageRank"	INTEGER,
	"tankHeroes"	TEXT,
	"tankRank"	INTEGER,
	"supportHeroes"	TEXT,
	"supportRank"	INTEGER,
	"gamesLost"	INTEGER,
	"gamesPlayed"	INTEGER,
	"gamesTied"	INTEGER,
	"timePlayed"	TEXT,
	"private"	TEXT,
	"lastGamePlayed"	TEXT,
	"apiLastChecked"	TEXT,
	"apiLastStatus"	TEXT,
	"addedDateUtc"	TEXT
);
CREATE TABLE IF NOT EXISTS "seasons" (
	"season"	INTEGER,
	"startDate"	TEXT,
	"endDate"	TEXT
);
CREATE TABLE IF NOT EXISTS "discord_channels" (
	"channelId"	INTEGER,
	"battletag"	TEXT,
	"nickname"	TEXT,
	"addedByDiscordUser"	TEXT,
	"addedDateUtc"	TEXT,
	FOREIGN KEY("battletag") REFERENCES "players"("battletag") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "statsHistory" (
	"date"	TEXT,
	"battletag "	TEXT,
	"damageRank"	INTEGER,
	"tankRank"	INTEGER,
	"supportRank"	INTEGER,
	"gamesLost"	INTEGER,
	"gamesPlayed"	INTEGER,
	"gamesTied"	INTEGER,
	"gamesWon"	INTEGER,
	"timePlayed"	TEXT,
	FOREIGN KEY("battletag ") REFERENCES "players"("battletag") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "botActions" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"date"	TEXT,
	"action"	TEXT,
	"isCompleted"	TEXT
);
COMMIT;
