import asyncio
import aiohttp
import json

class OWPlayer:

	def __init__(self):
		
		self.api_timeout = 10
		self.headers = {
			'Accept': 'application/json',
			'Content-Type': 'application/json; charset=UTF-8'}

	async def _http_get(self, api_resource):
		try:
			async with aiohttp.ClientSession() as session:
				r = await session.get(api_resource, headers=self.headers, timeout=self.api_timeout)
				if r.status == 200:
					return await r.json()
				else:
					self.http_last_status = r.status
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
		for ratings in self.player['ratings']:
			if ratings['role'] == role:
				return ratings['level']

		return False

	@property
	def name(self):
		return self.player['name']

	@property
	def level(self):
		return self.player['level']

	@property
	def private(self):
		return self.player['private']

	@property
	def gamesLost(self):
		return self.player['competitiveStats']['careerStats']['allHeroes']['game']['gamesLost']

	@property
	def gamesPlayed(self):
		return self.player['competitiveStats']['careerStats']['allHeroes']['game']['gamesPlayed']

	@property
	def gamesTied(self):
		return self.player['competitiveStats']['careerStats']['allHeroes']['game']['gamesTied']

	@property
	def timePlayed(self):
		return self.player['competitiveStats']['careerStats']['allHeroes']['game']['timePlayed']