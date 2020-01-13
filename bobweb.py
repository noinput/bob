from flask import Flask, jsonify
from flask import render_template
from flask import request

from flask import send_from_directory

import os

from resources.bobdb import BobDb
from resources.bobhelper import BobHelper


app = Flask(__name__,
    static_url_path='/static',
    static_folder='webstats/static',
    template_folder='webstats/templates')


@app.route("/")
def index():
    return 'theres nothing here...'

@app.route('/favicon.ico')
@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/player/<battletag>')
def player(battletag):
    db = BobDb('bob.db')
    playerdata = db.player_get(battletag)
    
    if not playerdata:
        return 'theres nothing here...'
    
    return render_template(
        'player.html',
        last_played_ago=last_played_ago,
        player=playerdata)

@app.route('/leaderboards/<id>')
def leaderboards(id):
    print(id)
    try:
        db = BobDb('bob.db')

        discord_channel = db.discord_channel_exist(id)

        if not discord_channel:
            return 'theres nothing here...'

        discord_channel_id = discord_channel['channelId']
        
        players = db.get_leaderboard(discord_channel_id)
        discord_names = db.discord_channel_names(discord_channel_id)

        return render_template(
            'leaderboard.html',
            players=players,
            server_name=discord_names['serverName'],
            channel_name=discord_names['channelName'],
            last_played_ago=last_played_ago,
            get_html_icon=get_html_icon)

    except Exception as e:
        print(f'### FAIL: {e}')
        return 'theres nothing here...'

def last_played_ago(then):

    bobhelper = BobHelper()
    duration = bobhelper.human_duration_since(then)

    if duration is not False:
        return f'{duration} ago'
    else:
        return ''

def get_html_icon(hero):
    bobhelper = BobHelper()
    html = bobhelper.html_asset_path(hero)
    return html

## BRUK CONFIG
if __name__ == '__main__':
    app.run(debug=True, port=63443, ssl_context=('webstats/cert/cert.pem', 'webstats/cert/privkey.pem'), host='0.0.0.0')
    #app.run(debug=True, port=5557, host='0.0.0.0')
