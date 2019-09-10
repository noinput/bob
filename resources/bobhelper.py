import datetime
import re
import sqlite3


class BobHelper:

    def __init__(self):
        pass

    # try to get the most played hero for a role and replace it with a hero emoji
    def most_played_emoji(self, player):

        # set custom emjois for roles in leaderboard [print(l) for l in message.guild.emojis]
        role_emoji = bobhelper.emojis_replace(player['maxRole'])
        hero_emoji = ''
        last_rank = ''
        
        try:
            if player['maxRole'] == 'damage':
                hero_emoji = emojis_replace(player['damageHeroes'].split(' ')[0])
                last_rank = db.rank_history_get_last(player['battletag'], 'damageRank')

            if player['maxRole'] == 'tank':
                hero_emoji = emojis_replace(player['tankHeroes'].split(' ')[0])
                last_rank = db.rank_history_get_last(player['battletag'], 'tankRank')

            if player['maxRole'] == 'support':
                hero_emoji = emojis_replace(player['supportHeroes'].split(' ')[0])
                last_rank = db.rank_history_get_last(player['battletag'], 'supportRank')
            return hero_emoji
        except:
            pass


    def rank_change_since_yesterday(self, player, html=False):
        if html:
            pass
        else:
            diff_rank = player['maxRank'] - last_rank
            diff_rank = '+{diff_rank}' if diff_rank > 0 else diff_rank
            return diff_rank

    def emojis_replace(self, emoji):
        replace_map = {
            'damage':       '<:owdmg:614835972210688000>',
            'support':      '<:owsup:614835972215144457>',
            'tank':         '<:owtank:614835972315807754>',

            'ashe':         '<:ashe:614947399181271051>',
            'bastion':      '<:bast:614947399357562908>',
            'doomfist':     '<:doom:614947399055573008>',
            'genji':        '<:genji:614947399500300316>',
            'hanzo':        '<:hanzo:614947398900383745>',
            'junkrat':      '<:junk:614947399257030686>',
            'mccree':       '<:cree:614947399357431809>',
            'mei':          '<:mei:614947399110230037>',
            'pharah':       '<:pharah:614947399701626924>',
            'reaper':       '<:reap:614947399361757229>',
            'soldier76':    '<:s76:614947399303168025>',
            'sombra':       '<:sombra:614947399273807872>',
            'symmetra':     '<:sym:614947399021887504>',
            'torbjorn':     '<:torb:614947399781056532>',
            'tracer':       '<:tracer:614947399017955341>',
            'widowmaker':   '<:widow:614947399412088833>',

            'dVa':          '<:dVa:614947399194116106>',
            'orisa':        '<:orisa:614947399839776770>',
            'reinhardt':    '<:rein:614947399462551570>',
            'roadhog':      '<:hog:614947399349305345>',
            'sigma':        '<:sigma:614947399286128640>',
            'winston':      '<:winston:614947399265157124>',
            'wreckingBall': '<:ball:614947399189921820>',
            'zarya':        '<:zarya:614947399315488769>',

            'ana':          '<:ana:614947399130939392>',
            'baptiste':     '<:bapt:614947398921486338>',
            'brigitte':     '<:brig:614947399806353427>',
            'lucio':        '<:lucio:614947399042859035>',
            'mercy':        '<:mercy:614947399265419284>',
            'moira':        '<:moira:614947399323877377>',
            'zenyatta':     '<:zen:614947399361757218>'}

        for k, v in replace_map.items():
            emoji = re.sub(k, v, emoji)

        return emoji
    
    def html_asset_path(self, asset):
        replace_map = {
            'defense':      '/static/assets/role_icons/defense.png',
            'damage':       '/static/assets/role_icons/offense.png',
            'support':      '/static/assets/role_icons/support.png',
            'tank':         '/static/assets/role_icons/tank.png',

            'ashe':         '/static/assets/hero_icons/75px-Icon-ashe.png',
            'bastion':      '/static/assets/hero_icons/75px-Icon-Bastion.png',
            'doomfist':     '/static/assets/hero_icons/75px-Icon-Doomfist.png',
            'genji':        '/static/assets/hero_icons/75px-Icon-Genji.png',
            'hanzo':        '/static/assets/hero_icons/75px-Icon-Hanzo.png',
            'junkrat':      '/static/assets/hero_icons/75px-Icon-Junkrat.png',
            'mccree':       '/static/assets/hero_icons/75px-Icon-McCree.png',
            'mei':          '/static/assets/hero_icons/75px-Icon-Mei.png',
            'pharah':       '/static/assets/hero_icons/75px-Icon-Pharah.png',
            'reaper':       '/static/assets/hero_icons/75px-Icon-Reaper.png',
            'soldier76':    '/static/assets/hero_icons/75px-Icon-Soldier_76.png',
            'sombra':       '/static/assets/hero_icons/75px-Icon-Sombra.png',
            'symmetra':     '/static/assets/hero_icons/75px-Icon-Symmetra.png',
            'torbjorn':     '/static/assets/hero_icons/75px-Icon-Torbjörn.png',
            'tracer':       '/static/assets/hero_icons/75px-Icon-Tracer.png',
            'widowmaker':   '/static/assets/hero_icons/75px-Icon-Widowmaker.png',

            'dVa':          '/static/assets/hero_icons/75px-Icon-D.Va.png',
            'orisa':        '/static/assets/hero_icons/75px-Icon-Orisa.png',
            'reinhardt':    '/static/assets/hero_icons/75px-Icon-Reinhardt.png',
            'roadhog':      '/static/assets/hero_icons/75px-Icon-Roadhog.png',
            'sigma':        '/static/assets/hero_icons/75px-Icon-Sigma.png',
            'winston':      '/static/assets/hero_icons/75px-Icon-Winston.png',
            'wreckingBall': '/static/assets/hero_icons/75px-Icon-Wrecking_Ball.png',
            'zarya':        '/static/assets/hero_icons/75px-Icon-Zarya.png',

            'ana':          '/static/assets/hero_icons/75px-Icon-Ana.png',
            'baptiste':     '/static/assets/hero_icons/75px-Icon-Baptiste.png',
            'brigitte':     '/static/assets/hero_icons/75px-Icon-Brigitte.png',
            'lucio':        '/static/assets/hero_icons/75px-Icon-Lúcio.png',
            'mercy':        '/static/assets/hero_icons/75px-Icon-Mercy.png',
            'moira':        '/static/assets/hero_icons/75px-Icon-Moira.png',
            'zenyatta':     '/static/assets/hero_icons/75px-Icon-Zenyatta.png'}

        for k, v in replace_map.items():
            asset = re.sub(k, v, asset)

        return asset

    def utcnow(self, ):
        t = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        return datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S')

    # i dont think this is working...
    def human_duration_since(self, then):
        try: 
            then = datetime.datetime.strptime(then, '%Y-%m-%d %H:%M:%S')
            #print(type(then), type(self.utcnow()))
            duration = self.utcnow() - then
            secs = int(duration.total_seconds())
            human_duration = f'{secs} seconds'
            if duration.total_seconds() > 60:
                mins, secs = divmod(int(duration.total_seconds()), 60)
                human_duration = f'{mins} minutes {secs} seconds'

            if duration.total_seconds() > 3600:
                mins, secs = divmod(int(duration.total_seconds()), 60)
                hours, mins = divmod(mins, 60)
                human_duration = f'{hours} hours {mins} minutes'
            
            if duration.total_seconds() > 86400:
                mins, secs = divmod(int(duration.total_seconds()), 60)
                hours, mins = divmod(mins, 60)
                days, hours = divmod(hours, 24)
                human_duration = f'{days} days {hours} hours'
            
            #print(f'last match updated was {human_duration} ago')
            return human_duration
        except Exception as e:
            print(f'{e}')
            print(f'last match updated was NA ago')
            return False