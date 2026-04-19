import copy
from ai import OAnQuanAI
from stone import GameBoard, Stone


class GameEngine:
    def __init__(self, mode='pvp', difficulty='medium'):
        self.mode = mode
        self.difficulty = difficulty
        self.players = []
        self.current_turn = 1
        self.is_game_over = False
        self.ai = OAnQuanAI(difficulty=self.difficulty) if self.mode == 'pve' else None
        self.board = []
        self.scores = {1: 0, 2: 0}
        self.anim_log = []
        self._undo_snapshot = None   # Lưu 1 snapshot để undo (chỉ cho PvE)
        self.init_board()

    def init_board(self):
        self.board = [{'quan': 0, 'dan': 5} for _ in range(12)]
        self.board[5]  = {'quan': 1, 'dan': 0}
        self.board[11] = {'quan': 1, 'dan': 0}
        self.scores = {1: 0, 2: 0}
        self.is_game_over = False
        self.current_turn = 1
        self.anim_log = []
        self._undo_snapshot = None

    def add_player(self, sid):
        if len(self.players) < 2:
            self.players.append(sid)
    def _save_undo_snapshot(self):
        """Lưu trạng thái trước khi người chơi đi (chỉ PvE)."""
        self._undo_snapshot = {
            'board':        copy.deepcopy(self.board),
            'scores':       copy.deepcopy(self.scores),
            'current_turn': self.current_turn,
            'is_game_over': self.is_game_over,
        }

    def undo_last_move(self):
        """Khôi phục về snapshot trước đó. Trả về True nếu thành công."""
        if self._undo_snapshot is None:
            return False
        snap = self._undo_snapshot
        self.board        = snap['board']
        self.scores       = snap['scores']
        self.current_turn = snap['current_turn']
        self.is_game_over = snap['is_game_over']
        self.anim_log     = []
        self._undo_snapshot = None   # Chỉ undo được 1 lần liên tiếp
        return True

    def _get_step(self, player, direction):
        """
        Xác định bước di chuyển (+1/-1) trên vòng tròn 12 ô.
        P1 (dưới) và P2 (trên) dùng cùng quy ước nội bộ.
        Frontend đã xử lý quy đổi hướng tương đối cho P2.
        """
        if player == 1:
            return 1 if direction == 'left' else -1
        else:
            return -1 if direction == 'left' else 1

    def process_move(self, cell_index, direction):
        if self.is_game_over:
            return False
        if cell_index in [5, 11] or self.board[cell_index]['dan'] == 0:
            return False

        if self.mode == 'pve' and self.current_turn == 1:
            self._save_undo_snapshot()

        step = self._get_step(self.current_turn, direction)
        self.anim_log = []

        stones_in_hand = self.board[cell_index]['dan']
        self.board[cell_index]['dan'] = 0
        current_idx = cell_index
        self.anim_log.append({"type": "pick", "cell": current_idx})

        while True:
            # Rải quân
            while stones_in_hand > 0:
                current_idx = (current_idx + step) % 12
                self.board[current_idx]['dan'] += 1
                stones_in_hand -= 1
                self.anim_log.append({"type": "drop", "cell": current_idx})

            next_idx = (current_idx + step) % 12

            if (self.board[next_idx]['dan'] > 0 or self.board[next_idx]['quan'] > 0) \
                    and next_idx not in [5, 11]:
                stones_in_hand = self.board[next_idx]['dan']
                self.board[next_idx]['dan'] = 0
                current_idx = next_idx
                self.anim_log.append({"type": "pick", "cell": current_idx})
                continue

            break  

        self._check_capture_chain(current_idx, step)

        if self._check_game_over():
            self.is_game_over = True
            self._sweep_board()
        else:
            self._switch_turn()

        return True

    def _check_capture_chain(self, current_idx, step):
        """Xử lý ăn quân liên hoàn."""
        while True:
            empty_idx   = (current_idx + step) % 12
            capture_idx = (empty_idx   + step) % 12

            if self.board[empty_idx]['dan'] == 0 and self.board[empty_idx]['quan'] == 0:
                has_stones = self.board[capture_idx]['dan'] > 0 or self.board[capture_idx]['quan'] > 0
                if has_stones:
                    # Luật Quan non: không ăn Quan nếu ít hơn 5 dân
                    if capture_idx in [5, 11] and self.board[capture_idx]['quan'] > 0:
                        if self.board[capture_idx]['dan'] < 5:
                            break

                    self.anim_log.append({"type": "slap_empty", "cell": empty_idx})
                    points = (self.board[capture_idx]['quan'] * 10) + self.board[capture_idx]['dan']
                    self.scores[self.current_turn] += points
                    self.board[capture_idx]['quan'] = 0
                    self.board[capture_idx]['dan']  = 0
                    self.anim_log.append({"type": "capture", "cell": capture_idx})
                    current_idx = capture_idx
                    continue
            break

    def _switch_turn(self):
        self.current_turn = 2 if self.current_turn == 1 else 1
        my_cells = range(6, 11) if self.current_turn == 1 else range(0, 5)
        if not any(self.board[i]['dan'] > 0 for i in my_cells):
            self.scores[self.current_turn] -= 5
            for i in my_cells:
                self.board[i]['dan'] += 1

    def _check_game_over(self):
        return self.board[5]['quan'] == 0 and self.board[11]['quan'] == 0

    def _sweep_board(self):
        """Vét bàn khi hết 2 Quan."""
        for i in range(6, 11):
            self.scores[1] += self.board[i]['dan']
            self.board[i]['dan'] = 0
        for i in range(0, 5):
            self.scores[2] += self.board[i]['dan']
            self.board[i]['dan'] = 0

    def _extract_to_obj_board(self):
        """Chuyển Dictionary board → Object board để AI tính toán."""
        mock_board = GameBoard()
        mock_board.next_stone_id = 0
        for idx, cell in enumerate(self.board):
            mock_board.cells[idx].stones = []
            for _ in range(cell['quan']):
                mock_board.cells[idx].stones.append(Stone(mock_board.next_stone_id, "Quan", ""))
                mock_board.next_stone_id += 1
            for _ in range(cell['dan']):
                mock_board.cells[idx].stones.append(Stone(mock_board.next_stone_id, "Dan", ""))
                mock_board.next_stone_id += 1
        for pid in [1, 2]:
            q, d = self.scores[pid] // 10, self.scores[pid] % 10
            lst = mock_board.player1_captured if pid == 1 else mock_board.player2_captured
            for _ in range(q): lst.append(Stone(0, "Quan", ""))
            for _ in range(d): lst.append(Stone(0, "Dan", ""))
        return mock_board

    def ai_make_move(self):
        if self.is_game_over or self.current_turn != 2 or self.ai is None:
            return
        obj_board = self._extract_to_obj_board()
        best_move = self.ai.get_best_move(obj_board)
        if best_move:
            self.process_move(best_move[0], best_move[1])


    def get_state(self):
        w = 0
        if self.scores[1] > self.scores[2]: w = 1
        elif self.scores[2] > self.scores[1]: w = 2
        return {
            'board':        self.board,
            'scores':       self.scores,
            'turn':         self.current_turn,
            'is_game_over': self.is_game_over,
            'winner':       w,
            'anim_log':     self.anim_log,
            'can_undo':     self._undo_snapshot is not None,
        }
    
