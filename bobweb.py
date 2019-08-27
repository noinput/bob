import datetime

from flask import Flask, jsonify
from flask import render_template

from flask import send_from_directory

import os

from resources.bobdb import BobDb

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
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route("/profile/<battletag>")
def profile(battletag):
    playerstats = owdb.playerGetDBdata(btag=battletag)
    if not owdb.playerInDB(battletag):
        return f'player not found {battletag}'
    else:
        return f"Hello player: {battletag} {playerstats}"

@app.route("/leaderboards/<discord_channel_id>")
def leaderboards(discord_channel_id):
    print(discord_channel_id)
    try:
        db = BobDb('bob.db')
        #discord_channel = owdb.discord_channel_exist(short)
        #if discord_channel:
            #average_sr, num_players, sqldata = get_sql(discord_channel['channel_id'])
        players = db.get_leaderboard(discord_channel_id)
        return render_template('leaderboard.html',
            players=players)
        """
            average_sr=average_sr,
            num_players=num_players,
            sqldata=sqldata,
            server_name=discord_channel['server_name'],
            channel_name=discord_channel['channel_name'])"""
        #else:
            #return 'theres nothing here...'

    except Exception as e:
        print(e)

## BRUK CONFIG
if __name__ == '__main__':
    app.run(debug=True, port=63443, ssl_context=('webstats/cert/cert.pem', 'webstats/cert/privkey.pem'), host='0.0.0.0')
    #app.run(debug=True, port=5557, host='0.0.0.0')
