from flask import Flask, render_template, redirect, g, request, url_for, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
import uuid
from controller import Controller
from constants import *


app = Flask(__name__)
app.config.from_pyfile('config.py')
socketio = SocketIO(app)
db = SQLAlchemy(app)


class Player(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    is_owner = db.Column(db.Boolean, nullable=False)
    disconnected = db.Column(db.Boolean, nullable=False)
    lobby_id = db.Column(db.String(8), db.ForeignKey(
        'lobby.id'), nullable=False)
    lobby = db.relationship('Lobby', back_populates='players')

    def __repr__(self):
        return 'Player {} with id {} in lobby {}'.format(self.username, self.id, self.lobby_id)


class Lobby(db.Model):
    id = db.Column(db.String(8), primary_key=True)
    players = db.relationship('Player', back_populates='lobby')

    def __repr__(self):
        return 'Lobby with id {} and users {}'.format(self.id, self.players)


db.create_all()

#########################
# UTIL FUNCTIONS
#########################


def gen_lobby_id():
    """
    Generate a unique 8-character lobby id.
    """
    while True:
        id = str(uuid.uuid4()).split('-')[0]
        if not Lobby.query.filter_by(id=id).first():
            break
    return id


def gen_player_id(short=False):
    """
    No need to check for duplicates here because this is a full uuid
    """
    return str(uuid.uuid4())


def get_lobby_owner(lobby_id):
    owner = Player.query.filter_by(lobby_id=lobby_id, is_owner=True).first()
    if not owner:
        owner = Player.query.filter_by(lobby_id=lobby_id).first()
        owner.is_owner = True
        db.session.commit()
    return owner

#########################
# ROUTES
#########################


@app.route('/')
def index():
    return render_template('homepage.html')


@app.route('/create-lobby', methods=['GET', 'POST'])
def create_lobby():
    """
    For a GET, return the template for this page.
    For a POST, is a username is supplied then 
    """
    print("Got request to create lobby")
    if request.method == 'GET':
        return render_template('create-lobby.html')
    if 'username' not in request.form:
        return render_template('create-lobby.html', state={'error': True, 'msg': 'No username provided. Please provide a username.'})
    try:
        username = request.form['username']
        lobby_id = gen_lobby_id()
        player_id = gen_player_id()
        lobby = Lobby(id=lobby_id)
        user = Player(id=player_id, username=username, lobby_id=lobby_id,
                      is_owner=True, disconnected=False)
        lobby.players.append(user)
        db.session.add(lobby)
        db.session.commit()
        session['lobby_id'] = lobby_id
        session['player_id'] = player_id
        return redirect(url_for('game', lobby_id=lobby_id))
    except Exception as e:
        print(e)
        return render_template('create-lobby.html', state={'error': True, 'msg': 'Something went wrong. Please try again.'})


@app.route('/join-lobby', methods=['GET', 'POST'])
def join_lobby():
    if request.method == 'GET':
        return render_template('join-lobby.html')
    msg = None
    try:
        username = request.form['username']
        lobby_id = request.form['code']
        if 'username' not in request.form or 'code' not in request.form:
            msg = 'Please supply both a username and a game code.'
            raise ValueError
        lobby = Lobby.query.filter_by(id=lobby_id).first()
        if not lobby:
            msg = 'Invalid game code required. Please check code and try again.'
            raise ValueError
        if username in [u.username for u in lobby.players]:
            msg = 'This username is taken. Please pick another username.'
            raise ValueError
        if len(lobby.players) == MAX_PLAYERS:
            msg = 'The player limit for this lobby has been reached.'
            raise ValueError
        player_id = gen_player_id()
        session['player_id'] = player_id
        session['lobby_id'] = lobby_id
        user = Player(id=player_id, username=username, lobby_id=lobby_id,
                      is_owner=False, disconnected=False)
        lobby.players.append(user)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('game', lobby_id=lobby_id))
    except ValueError:
        return render_template('join-lobby.html', state={'error': True, 'msg': msg})
    except Exception as e:
        print("UH OH")
        print(e)
        return render_template('join-lobby.html', state={'error': True, 'msg': 'Something went wrong. Please try again.'})


@app.route('/game/<lobby_id>', methods=['GET'])
def game(lobby_id):
    player_id = session.get('player_id')
    players = Lobby.query.filter_by(id=lobby_id).first().players
    owner = get_lobby_owner(lobby_id)
    payload = {
        'players': [{'player_id': p.id, 'username': p.username} for p in players],
        'lobby_id': lobby_id,
        'owner_uuid': owner.id,
        'uuid': player_id,
    }
    return render_template('game.html', state=payload)


#########################
# SOCKETIO EVENTS
#########################
@socketio.on('connect')
def on_connect():
    player_id = session.get('player_id')
    print("Player id is {}".format(player_id))
    player = Player.query.filter_by(id=player_id).first()
    if player:
        payload = {'uuid': player.id}
        emit('connected', payload, to=request.sid)


@socketio.on('join')
def join():
    try:
        # Get user id and room id
        lobby_id = session.get('lobby_id')
        player_id = session.get('player_id')
        owner = get_lobby_owner(lobby_id)
        lobby = Lobby.query.filter_by(id=lobby_id).first()
        print("LOBBY IS: {}".format(lobby))
        # Add user to socketio room
        join_room(lobby_id)

        payload = {
            'player_data': [{'uuid': u.id, 'username': u.username, 'disconnected': u.disconnected} for u in lobby.players],
            'owner_uuid': owner.id,
            'lobby_id': lobby_id
        }

        emit('joined', payload, to=lobby_id)
    except Exception as e:
        print(e)
        print("Error joining room")
        pass


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', to=room)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
