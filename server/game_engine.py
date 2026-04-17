import random
from ai import OAnQuanAI
from stone import GameBoard, Stone

class GameEngine:
    def __init__(self, mode='pvp', difficulty='medium'):
        self.mode = mode
        self.difficulty = difficulty
        self.players = []
        self.current_turn = 1 
        self.is_game_over = False
        
        if self.mode == 'pve':
            self.ai = OAnQuanAI(difficulty=self.difficulty)
        else:
            self.ai = None
        
        self.board = []
        self.scores = {1: 0, 2: 0}
        self.anim_log = [] # Lưu nhật ký các bước để Client chạy hoạt ảnh
        self.init_board()

    def init_board(self):
        self.board = [{'quan': 0, 'dan': 5} for _ in range(12)]
        self.board[5] = {'quan': 1, 'dan': 0}
        self.board[11] = {'quan': 1, 'dan': 0}
        self.scores = {1: 0, 2: 0}
        self.is_game_over = False
        self.current_turn = 1
        self.anim_log = []

    def add_player(self, sid):
        if len(self.players) < 2:
            self.players.append(sid)

    def _get_step(self, player, direction):
        if player == 1:
            return 1 if direction == 'right' else -1
        else:
            return -1 if direction == 'right' else 1

    def process_move(self, cell_index, direction):
        if self.is_game_over:
            return False

        if cell_index in [5, 11] or self.board[cell_index]['dan'] == 0:
            return False 
            
        if self.current_turn == 1 and cell_index not in range(6, 11):
            return False 
        if self.current_turn == 2 and cell_index not in range(0, 5):
            return False 
            
        step = self._get_step(self.current_turn, direction)
        self.anim_log = [] # Reset log cho turn mới
        
        stones_to_sow = self.board[cell_index]['dan']
        self.board[cell_index]['dan'] = 0
        current_idx = cell_index
        
        # Log: Bốc quân (h1)
        self.anim_log.append({"type": "pick", "cell": current_idx, "hand": "h1"})
        
        while True:
            while stones_to_sow > 0:
                current_idx = (current_idx + step) % 12
                self.board[current_idx]['dan'] += 1
                stones_to_sow -= 1
                
                # Log: Di chuyển (h1) tới ô tiếp theo rồi nhả quân (h2)
                self.anim_log.append({"type": "move", "cell": current_idx, "hand": "h1"})
                self.anim_log.append({"type": "drop", "cell": current_idx, "hand": "h2"})
                
            next_idx = (current_idx + step) % 12
            
            if self.board[next_idx]['quan'] == 0 and self.board[next_idx]['dan'] == 0:
                # Log: Trỏ vào ô trống kiểm tra (h3)
                self.anim_log.append({"type": "check", "cell": next_idx, "hand": "h3"})
                self._check_and_capture(current_idx, next_idx, step)
                break 
                
            elif next_idx in [5, 11]:
                break
                
            else:
                stones_to_sow = self.board[next_idx]['dan']
                self.board[next_idx]['dan'] = 0
                current_idx = next_idx
                # Log: Bốc quân nối chuyền (h1)
                self.anim_log.append({"type": "pick", "cell": current_idx, "hand": "h1"})
                
        if self._check_game_over():
            self.is_game_over = True
            self._sweep_board()
        else:
            self._switch_turn()
            
        return True

    def _check_and_capture(self, current_idx, empty_idx, step):
        capture_idx = (empty_idx + step) % 12
        
        if self.board[capture_idx]['quan'] == 0 and self.board[capture_idx]['dan'] == 0:
            return
            
        if capture_idx in [5, 11] and self.board[capture_idx]['quan'] > 0:
            if self.board[capture_idx]['dan'] < 5:
                return 

        points = (self.board[capture_idx]['quan'] * 10) + self.board[capture_idx]['dan']
        self.scores[self.current_turn] += points
        
        self.board[capture_idx]['quan'] = 0
        self.board[capture_idx]['dan'] = 0
        
        # Log: Bốc quân ăn được (h1)
        self.anim_log.append({"type": "capture", "cell": capture_idx, "hand": "h1"})
        
        next_empty_idx = (capture_idx + step) % 12
        if self.board[next_empty_idx]['quan'] == 0 and self.board[next_empty_idx]['dan'] == 0:
            self.anim_log.append({"type": "check", "cell": next_empty_idx, "hand": "h3"})
            self._check_and_capture(capture_idx, next_empty_idx, step)

    def _switch_turn(self):
        self.current_turn = 2 if self.current_turn == 1 else 1
        my_cells = range(6, 11) if self.current_turn == 1 else range(0, 5)
        has_stones = any((self.board[i]['dan'] > 0) for i in my_cells)
        if not has_stones:
            self._borrow_and_distribute(my_cells)

    def _borrow_and_distribute(self, my_cells):
        self.scores[self.current_turn] -= 5 
        for i in my_cells:
            self.board[i]['dan'] += 1

    def _check_game_over(self):
        quan_5_empty = (self.board[5]['quan'] == 0 and self.board[5]['dan'] == 0)
        quan_11_empty = (self.board[11]['quan'] == 0 and self.board[11]['dan'] == 0)
        return quan_5_empty and quan_11_empty

    def _sweep_board(self):
        for i in range(6, 11):
            self.scores[1] += self.board[i]['dan']
            self.board[i]['dan'] = 0
        for i in range(0, 5):
            self.scores[2] += self.board[i]['dan']
            self.board[i]['dan'] = 0

    def ai_make_move(self):
        if self.is_game_over or self.current_turn != 2 or self.ai is None:
            return
        
        mock_board = GameBoard()
        mock_board.next_stone_id = 0
        for idx, cell_data in enumerate(self.board):
            mock_board.cells[idx].stones = []
            for _ in range(cell_data['quan']):
                mock_board.cells[idx].stones.append(Stone(mock_board.next_stone_id, "Quan", ""))
                mock_board.next_stone_id += 1
            for _ in range(cell_data['dan']):
                mock_board.cells[idx].stones.append(Stone(mock_board.next_stone_id, "Dan", ""))
                mock_board.next_stone_id += 1
                
        for player_id, score in self.scores.items():
            quans = score // 10
            dans = score % 10
            captured_list = mock_board.player1_captured if player_id == 1 else mock_board.player2_captured
            for _ in range(quans): captured_list.append(Stone(0, "Quan", ""))
            for _ in range(dans): captured_list.append(Stone(0, "Dan", ""))
                
        best_move = self.ai.get_best_move(mock_board)
        if best_move:
            self.process_move(best_move[0], best_move[1])

    def get_state(self):
        return {
            'board': self.board,
            'scores': self.scores,
            'turn': self.current_turn,
            'is_game_over': self.is_game_over,
            'winner': 1 if self.scores[1] > self.scores[2] else 2 if self.scores[2] > self.scores[1] else 0,
            'anim_log': self.anim_log
        }