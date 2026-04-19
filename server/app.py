import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from game_engine import GameEngine
import random, string, os

base_dir     = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, '../templates')
static_dir   = os.path.join(base_dir, '../static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = 'o-an-quan-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

active_rooms = {}   


def generate_room_id():
    while True:
        rid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if rid not in active_rooms:
            return rid


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_room')
def on_create_room(data):
    mode       = data.get('mode', 'pvp')
    difficulty = data.get('difficulty', 'medium')
    room_name  = data.get('room_name')

    if room_name:
        room_id = room_name.strip().upper()
        if not room_id:
            emit('room_error', {'message': 'Tên phòng không được để trống!'})
            return
        if room_id in active_rooms:
            emit('room_error', {'message': f'Phòng "{room_id}" đã tồn tại. Hãy chọn tên khác!'})
            return
    else:
        room_id = generate_room_id()

    engine_mode = 'pvp' if mode == 'practice' else mode
    game = GameEngine(mode=engine_mode, difficulty=difficulty)
    game.players.append(request.sid)
    active_rooms[room_id] = game

    join_room(room_id)
    emit('room_created', {'room_id': room_id, 'mode': mode})
    emit('update_board', game.get_state(), room=room_id)
    print(f"[+] Room: {room_id} | Mode: {mode}")


@socketio.on('join_room')
def on_join_room(data):
    room_id = data.get('room_id', '').strip().upper()
    if not room_id:
        emit('room_error', {'message': 'Vui lòng nhập mã phòng!'})
        return
    if room_id not in active_rooms:
        emit('room_error', {'message': f'Phòng "{room_id}" không tồn tại!'})
        return

    game = active_rooms[room_id]
    if game.mode != 'pvp':
        emit('room_error', {'message': 'Phòng này không phải chế độ PvP!'})
        return
    if len(game.players) >= 2:
        emit('room_error', {'message': f'Phòng "{room_id}" đã đầy!'})
        return

    if game.is_game_over:
        game.init_board()
        print(f"[~] Room {room_id}: rematch started")

    game.add_player(request.sid)
    join_room(room_id)
    emit('join_success', {'room_id': room_id})
    emit('game_start', {'message': 'Đã tìm thấy đối thủ!'}, room=room_id)
    emit('update_board', game.get_state(), room=room_id)
    print(f"[+] Joined: {room_id} | SID: {request.sid}")

@socketio.on('find_random_room')
def on_find_random_room():
    # REQ 4: Chỉ lấy phòng đang chờ, chưa kết thúc
    waiting = [rid for rid, g in active_rooms.items()
               if g.mode == 'pvp' and len(g.players) == 1 and not g.is_game_over]
    if not waiting:
        emit('room_error', {'message': 'Không có phòng nào đang chờ. Hãy tạo phòng mới!'})
        return
    room_id = random.choice(waiting)
    game    = active_rooms[room_id]
    game.add_player(request.sid)
    join_room(room_id)
    emit('join_success', {'room_id': room_id})
    emit('game_start', {'message': 'Đã tìm thấy đối thủ!'}, room=room_id)
    emit('update_board', game.get_state(), room=room_id)
    print(f"[+] Random join: {room_id}")


@socketio.on('make_move')
def on_make_move(data):
    room_id    = data.get('room_id')
    cell_index = data.get('cell_index')
    direction  = data.get('direction')
    if room_id not in active_rooms:
        return
    game    = active_rooms[room_id]
    success = game.process_move(cell_index, direction)
    if success:
        emit('update_board', game.get_state(), room=room_id)
        if game.mode == 'pve' and game.current_turn == 2 and not game.is_game_over:
            socketio.sleep(1)
            game.ai_make_move()
            emit('update_board', game.get_state(), room=room_id)


@socketio.on('undo_move')
def on_undo_move(data):
    room_id = data.get('room_id')
    if room_id not in active_rooms:
        return
    game = active_rooms[room_id]
    if game.mode != 'pve':
        return
    if game.undo_last_move():
        emit('update_board', game.get_state(), room=room_id)
    else:
        emit('room_error', {'message': 'Không thể undo! Chưa có nước đi nào.'})


@socketio.on('leave_room_event')
def on_leave_room(data):
    room_id = data.get('room_id')
    if not room_id or room_id not in active_rooms:
        return
    game = active_rooms[room_id]
    leave_room(room_id)

    if game.mode == 'pvp' and not game.is_game_over:
        emit('opponent_left', {'message': 'Đối thủ đã thoát. Bạn thắng!'}, room=room_id)

    if request.sid in game.players:
        game.players.remove(request.sid)

    if not game.players:
        del active_rooms[room_id]
        print(f"[-] Room deleted: {room_id}")
    else:
        print(f"[~] Room {room_id}: waiting for rejoin ({len(game.players)} player(s) left)")


@socketio.on('disconnect')
def on_disconnect():
    for room_id, game in list(active_rooms.items()):
        if request.sid in game.players:
            game.players.remove(request.sid)
            if game.mode == 'pvp' and len(game.players) > 0 and not game.is_game_over:
                emit('opponent_left', {'message': 'Đối thủ mất kết nối. Bạn thắng!'}, room=room_id)
            if not game.players:
                del active_rooms[room_id]
                print(f"[-] Room cleaned on disconnect: {room_id}")
            break


if __name__ == '__main__':
    print("Khởi động Server Ô Ăn Quan...")
    socketio.run(app, debug=True, port=5000)