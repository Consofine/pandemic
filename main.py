from flask import render_template, redirect, g, Flask, request, url_for, session, jsonify
from sqlite3 import dbapi2 as sqlite3
from os import path
import json
import requests
from util import generate_id

app = Flask(__name__)

# Import game logic here


valid_moves = [
    'MOVE_ADJ',
    'MOVE_DIRECT',
    'MOVE_CHARTER',
    'MOVE_SHUTTLE'
]

app.config.from_pyfile('config.py')


def cursor_to_dict_array(cur):
    columns = [column[0] for column in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db_file = app.config["DATABASE"]
        exists = path.isfile(db_file)
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        if not exists:
            qry = open('schema.sql', 'r').read()
            c = db.cursor()
            c.executescript(qry)
            db.commit()
            c.close()

    # Make sure database has tables
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/game/end", methods=['PUT'])
def end_game():
    session.pop('game_started', None)

    return jsonify({
        "success": True
    })



@app.route('/game/move', methods=['PUT'])
def game_move():
    if not session.get('game_started'):
        return jsonify({
            "error" : "There is no game yet!"
        }), 400
    if 'move' not in request.json:
        return jsonify({
            "error" : "No move passed!"
        }), 400
    move = request.json['move']
    if move not in valid_moves:
        return jsonify({
            "error" : "{} is an invalid move".format(move)
        }), 400


    # Handle the move with the expected parameter 


    return jsonify({
        'success' : True
    })


@app.route('/game', methods=["POST"])
def create_game():
    if session.get('game_started'):
        return jsonify({
            "error": "Game already started!"
        }), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'insert into players (player_id) values (?)',
        (
            '1'
        )
    )
    project_id = cursor.lastrowid
    db.commit()
    db.close()

    session['game_started'] = True

    return jsonify({
        "success": True
    })


@app.route('/game', methods=["GET"])
def fetch_games():
    db = get_db()
    cursor = db.cursor()
    cur = db.execute('select * from players')
    entries = cursor_to_dict_array(cur)
    return jsonify({
        'entries': entries
    })


@app.route('/', methods=["GET"])
def base():
    db = get_db()

    return json.dumps({
        "success": True
    })


@app.route('/game/<id>', methods=["GET"])
def fetch_game():
    print("hi")
    # if not session.get('logged_in'):
    #     return redirect("/login")
    # return redirect("/home")
