from flask import Flask, jsonify
from flask import request

from resources.bobdb import BobDb


app = Flask(__name__)

@app.route("/")
def index():
    return 'theres nothing here...'

@app.route('/json/player/<battletag>')
def jsonplayer(battletag):
    db = BobDb('bob.db')
    playerdata = db.player_get(battletag)
    
    if not playerdata:
        return jsonify({'data': { 'status' :'NOT_FOUND' }})
    
    return jsonify({
        'data': {
            'status'            :'OK',
            'battletag'         :playerdata['battletag'],
            'damageHeroes'      :playerdata['damageHeroes'],
            'damageRank'        :playerdata['damageRank'],
            'tankHeroes'        :playerdata['tankHeroes'],
            'tankRank'          :playerdata['tankRank'],
            'supportHeroes'     :playerdata['supportHeroes'],
            'supportRank'       :playerdata['supportRank'],
            'gamesLost'         :playerdata['gamesLost'],
            'gamesPlayed'       :playerdata['gamesPlayed'],
            'gamesTied'         :playerdata['gamesTied'],
            'gamesWon'          :playerdata['gamesWon'],
            'timePlayed'        :playerdata['timePlayed'],
            'private'           :playerdata['private'],
            'lastGamePlayed'    :playerdata['lastGamePlayed'],
            'apiLastChecked'    :playerdata['apiLastChecked'],
            'apiLastStatus'     :playerdata['apiLastStatus'],
            'addedDateUtc'      :playerdata['addedDateUtc']}
        })

if __name__ == '__main__':
    app.run(debug=True, port=5557, host='0.0.0.0')
