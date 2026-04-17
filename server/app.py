from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from game_engine import GameEngine
import random
import string

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'o-an-quan-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Lưu trữ state của các phòng
active_rooms = {}

def generate_room_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_room')
def on_create_room(data):
    mode = data.get('mode', 'pvp')
    difficulty = data.get('difficulty', 'medium')
    room_id = generate_room_id()
    
    join_room(room_id)
    active_rooms[room_id] = GameEngine(mode=mode, difficulty=difficulty)
    
    emit('room_created', {'room_id': room_id})
    emit('update_board', active_rooms[room_id].get_state(), room=room_id)
    print(f"Room created: {room_id} - Mode: {mode}")

@socketio.on('join_room')
def on_join_room(data):
    room_id = data.get('room_id')
    if room_id in active_rooms:
        join_room(room_id)
        active_rooms[room_id].add_player(request.sid)
        emit('game_start', {'message': 'Game is ready!'}, room=room_id)
        emit('update_board', active_rooms[room_id].get_state(), room=room_id)
    else:
        emit('error', {'message': 'Phòng không tồn tại!'})

@socketio.on('make_move')
def on_make_move(data):
    room_id = data.get('room_id')
    cell_index = data.get('cell_index')
    direction = data.get('direction')
    
    if room_id in active_rooms:
        game = active_rooms[room_id]
        
        success = game.process_move(cell_index, direction)
        
        if success:
            emit('update_board', game.get_state(), room=room_id)
            
            if game.mode == 'pve' and game.current_turn == 2:
                socketio.sleep(1)
                game.ai_make_move()
                emit('update_board', game.get_state(), room=room_id)

if __name__ == '__main__':
    print("Khởi động Server Ô Ăn Quan...")
    socketio.run(app, debug=True, port=5000)