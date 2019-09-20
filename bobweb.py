import datetime

from flask import Flask, jsonify
from flask import render_template

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

@app.route('/robots.txt')
def robots():
    return 'User-agent: *\nDisallow: /'

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'webstats/static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route("/profile/<battletag>")
def profile(battletag):
    playerstats = owdb.playerGetDBdata(btag=battletag)
    if not owdb.playerInDB(battletag):
        return f'player not found {battletag}'
    else:
        return f"Hello player: {battletag} {playerstats}"

@app.route("/leaderboards/<id>")
def leaderboards(id):
    print(id)
    try:
        db = BobDb('bob.db')

        discord_channel = db.discord_channel_exist(id)
        
        print('####', discord_channel)

        if not discord_channel:
            print('why the fq this trigger')
            return 'theres nothing here...'

        discord_channel_id = discord_channel['channelId']
        print('####', discord_channel_id)
        
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
        print(e)
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
