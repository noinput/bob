import asyncio
import aiohttp
import json
import time

class OWPlayer:

	def __init__(self, timelimit=2):
		
		self.last_run = self._time
		self.timelimit = timelimit
		self.api_timeout = 11
		self.headers = {
			'Accept': 'application/json',
			'Content-Type': 'application/json; charset=UTF-8'}

	async def _http_get(self, api_resource):
		
		# only do one request every 3 seconds
		if self.last_run <= self._time:
			self.last_run = self._time + self.timelimit
			await asyncio.sleep(0)
		else:
			sleep_time = self.last_run - self._time
			self.last_run = self.last_run + self.timelimit
			await asyncio.sleep(sleep_time)
		
		try:
			async with aiohttp.ClientSession() as session:
				r = await session.get(api_resource, headers=self.headers, timeout=self.api_timeout)
				self.http_last_status = r.status
				if r.status == 200:
					return await r.json()
				else:
					return False
		except asyncio.TimeoutError:
			print(f'timed out {api_resource}')
			return False

		except Exception as e:
			print(f'_http_get failed: ({r.status}) {e}')
			return False

	async def get(self, battletag, platform='pc'):
		r = await self._http_get(f'https://ovrstat.com/stats/{platform}/{battletag}')
		if r:
			self.player = r
			return True

		return False

	def get_roleRank(self, role):
		try:
			for ratings in self.player['ratings']:
				if ratings['role'] == role:
					return ratings['level']
		except (KeyError, TypeError):
			return 0

	@property
	def battletag(self):
		if 'name' in self.player:
			return self.player['name']
		return False

	@property
	def level(self):
		if 'level' in self.player:
			return self.player['level']
		return False

	@property
	def private(self):
		if 'private' in self.player:
			return self.player['private']
		return False

	@property
	def gamesLost(self):
		try:
			return self.player['competitiveStats']['careerStats']['allHeroes']['game']['gamesLost']
		except (KeyError, TypeError):
			return 0
	
	@property
	def gamesPlayed(self):
		try:
			return self.player['competitiveStats']['careerStats']['allHeroes']['game']['gamesPlayed']
		except (KeyError, TypeError):
			return 0
	
	@property
	def gamesTied(self):
		try:
			return self.player['competitiveStats']['careerStats']['allHeroes']['game']['gamesTied']
		except (KeyError, TypeError):
			return 0
	
	@property
	def timePlayed(self):
		try:
			return self.player['competitiveStats']['careerStats']['allHeroes']['game']['timePlayed']
		except (KeyError, TypeError):
			return 0
	
	@property
	def _time(self):
		return int(time.time())

	@property
	def _utcnow(self):
		return  datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')