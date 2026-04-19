"""Minimax AI cho game Ô Ăn Quan với 3 cấp độ."""
import copy
import time
from constants import *


class OAnQuanAI:
    """AI sử dụng Minimax/Alpha-Beta algorithm."""
    
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.depth, self.use_alpha_beta = self._get_config(difficulty)
        self.max_player = 2
        self.min_player = 1
        self.log = {
            'total_moves': 0,
            'total_time': 0,
            'avg_time': 0,
            'nodes_evaluated': 0,
            'pruning_count': 0
        }
    
    def _get_config(self, difficulty):
        """Lấy config theo độ khó."""
        configs = {
            'easy': (2, False),
            'medium': (4, True),
            'hard': (5, True)
        }
        return configs.get(difficulty, (4, True))
    
    def get_best_move(self, game_board):
        """Tìm nước đi tốt nhất cho AI."""
        start_time = time.time()
        self.log['nodes_evaluated'] = 0
        self.log['pruning_count'] = 0
        
        best_score = float('-inf')
        best_move = None
        
        possible_moves = self._get_possible_moves(game_board, 2)
        
        if not possible_moves:
            return None
        
        print(f"AI đang tính toán {len(possible_moves)} nước đi...")
        
        # BƯỚC 1: Kiểm tra nước đi thắng ngay (winning move) - ưu tiên cao nhất
        winning_move = self._find_winning_move(game_board, possible_moves)
        if winning_move:
            elapsed_time = time.time() - start_time
            self.log['total_moves'] += 1
            self.log['total_time'] += elapsed_time
            self.log['avg_time'] = self.log['total_time'] / self.log['total_moves']
            print(f"AI chọn: Ô {winning_move[0]}, Hướng {winning_move[1]} (WINNING MOVE!)")
            print(f"Thời gian: {elapsed_time:.3f}s | Nodes: {self.log['nodes_evaluated']} | Pruning: {self.log['pruning_count']}")
            return winning_move
        
        # BƯỚC 2: Sử dụng minimax để tìm nước đi tốt nhất
        for cell_id, direction in possible_moves:
            board_copy = self._copy_board(game_board)
            self._simulate_move(board_copy, cell_id, direction, 2)
            
            # Kiểm tra nếu move này dẫn đến thắng ngay
            if self._is_terminal(board_copy):
                # Kiểm tra ai thắng
                score2 = board_copy.calculate_score(2)
                score1 = board_copy.calculate_score(1)
                if score2 > score1:
                    # AI thắng - đây là nước đi tốt nhất
                    elapsed_time = time.time() - start_time
                    self.log['total_moves'] += 1
                    self.log['total_time'] += elapsed_time
                    self.log['avg_time'] = self.log['total_time'] / self.log['total_moves']
                    print(f"AI chọn: Ô {cell_id}, Hướng {direction} (WINNING MOVE!)")
                    print(f"Thời gian: {elapsed_time:.3f}s | Nodes: {self.log['nodes_evaluated']} | Pruning: {self.log['pruning_count']}")
                    return (cell_id, direction)
            
            if self.use_alpha_beta:
                score = self._minimax_alpha_beta(
                    board_copy,
                    self.depth - 1,
                    float('-inf'),
                    float('inf'),
                    False
                )
            else:
                score = self._minimax(
                    board_copy,
                    self.depth - 1,
                    False
                )
            
            if score > best_score:
                best_score = score
                best_move = (cell_id, direction)
        
        elapsed_time = time.time() - start_time
        self.log['total_moves'] += 1
        self.log['total_time'] += elapsed_time
        self.log['avg_time'] = self.log['total_time'] / self.log['total_moves']
        
        print(f"AI chọn: Ô {best_move[0]}, Hướng {best_move[1]} (Score: {best_score:.2f})")
        print(f"Thời gian: {elapsed_time:.3f}s | Nodes: {self.log['nodes_evaluated']} | Pruning: {self.log['pruning_count']}")
        print(f"Trung bình: {self.log['avg_time']:.3f}s/nước")
        
        return best_move
    
    def _get_possible_moves(self, game_board, player):
        """Lấy tất cả nước đi có thể của player."""
        moves = []
        
        if player == 1:
            cells = PLAYER1_CELLS
        else:
            cells = PLAYER2_CELLS
        
        for cell_id in cells:
            if not game_board.cells[cell_id].is_empty():
                moves.append((cell_id, 'left'))
                moves.append((cell_id, 'right'))
        
        return moves
    
    def _find_winning_move(self, board, possible_moves):
        """Tìm nước đi có thể ăn quan để thắng ngay."""
        for cell_id, direction in possible_moves:
            board_copy = self._copy_board(board)
            self._simulate_move(board_copy, cell_id, direction, 2)
            
            # Kiểm tra nếu game kết thúc sau nước đi này
            if self._is_terminal(board_copy):
                score2 = board_copy.calculate_score(2)
                score1 = board_copy.calculate_score(1)
                # Nếu AI thắng, đây là nước đi thắng
                if score2 > score1:
                    return (cell_id, direction)
        
        return None
    
    def _minimax(self, board, depth, is_maximizing):
        """Minimax algorithm."""
        self.log['nodes_evaluated'] += 1
        
        # Kiểm tra điều kiện thắng trước khi đánh giá
        if self._is_terminal(board):
            score2 = board.calculate_score(2)
            score1 = board.calculate_score(1)
            if score2 > score1:
                return 10000  # AI thắng - điểm rất cao
            elif score1 > score2:
                return -10000  # AI thua - điểm rất thấp
            else:
                return 0  # Hòa
        
        if depth == 0:
            return self._evaluate(board, self.difficulty)
        
        player = 2 if is_maximizing else 1
        possible_moves = self._get_possible_moves(board, player)
        
        if not possible_moves:
            return self._evaluate(board, self.difficulty)
        
        if is_maximizing:
            max_score = float('-inf')
            for move_cell, move_dir in possible_moves:
                board_copy = self._copy_board(board)
                self._simulate_move(board_copy, move_cell, move_dir, player)
                score = self._minimax(board_copy, depth - 1, False)
                max_score = max(max_score, score)
            return max_score
        else:
            min_score = float('inf')
            for move_cell, move_dir in possible_moves:
                board_copy = self._copy_board(board)
                self._simulate_move(board_copy, move_cell, move_dir, player)
                score = self._minimax(board_copy, depth - 1, True)
                min_score = min(min_score, score)
            return min_score
    
    def _minimax_alpha_beta(self, board, depth, alpha, beta, is_maximizing):
        """Minimax với Alpha-Beta Pruning."""
        self.log['nodes_evaluated'] += 1
        
        # Kiểm tra điều kiện thắng trước khi đánh giá
        if self._is_terminal(board):
            score2 = board.calculate_score(2)
            score1 = board.calculate_score(1)
            if score2 > score1:
                return 10000  # AI thắng - điểm rất cao
            elif score1 > score2:
                return -10000  # AI thua - điểm rất thấp
            else:
                return 0  # Hòa
        
        if depth == 0:
            return self._evaluate(board, self.difficulty)
        
        player = 2 if is_maximizing else 1
        possible_moves = self._get_possible_moves(board, player)
        
        if not possible_moves:
            return self._evaluate(board, self.difficulty)
        
        if is_maximizing:
            max_score = float('-inf')
            for move_cell, move_dir in possible_moves:
                board_copy = self._copy_board(board)
                self._simulate_move(board_copy, move_cell, move_dir, player)
                score = self._minimax_alpha_beta(
                    board_copy, depth - 1, alpha, beta, False
                )
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                
                if beta <= alpha:
                    self.log['pruning_count'] += 1
                    break
            
            return max_score
        else:
            min_score = float('inf')
            for move_cell, move_dir in possible_moves:
                board_copy = self._copy_board(board)
                self._simulate_move(board_copy, move_cell, move_dir, player)
                score = self._minimax_alpha_beta(
                    board_copy, depth - 1, alpha, beta, True
                )
                min_score = min(min_score, score)
                beta = min(beta, score)
                
                if beta <= alpha:
                    self.log['pruning_count'] += 1
                    break
            
            return min_score
    
    def _simulate_move(self, board, cell_id, direction, player):
        """Simulate một nước đi."""
        stones = board.pick_stones(cell_id)
        if not stones:
            return
        
        if player == 1:
            offset = 1 if direction == 'left' else -1
        else:
            offset = -1 if direction == 'left' else 1
        
        current_cell = cell_id
        for stone in stones:
            current_cell = (current_cell + offset) % 12
            board.drop_stone(current_cell, stone)
        
        next_cell = (current_cell + offset) % 12
        
        if board.cells[next_cell].is_empty():
            capture_cell = (next_cell + offset) % 12
            if not board.cells[capture_cell].is_empty():
                if capture_cell in QUAN_CELLS:
                    has_quan = any(s.type == "Quan" for s in board.cells[capture_cell].stones)
                    if has_quan:
                        num_dan = sum(1 for s in board.cells[capture_cell].stones if s.type != "Quan")
                        if num_dan < 5:
                            return
                
                captured = board.pick_stones(capture_cell)
                board.capture_stones(player, captured)
                
                next_empty = (capture_cell + offset) % 12
                if board.cells[next_empty].is_empty():
                    next_capture = (next_empty + offset) % 12
                    if not board.cells[next_capture].is_empty():
                        if next_capture in QUAN_CELLS:
                            has_quan = any(s.type == "Quan" for s in board.cells[next_capture].stones)
                            if has_quan:
                                num_dan = sum(1 for s in board.cells[next_capture].stones if s.type != "Quan")
                                if num_dan >= 5:
                                    captured2 = board.pick_stones(next_capture)
                                    board.capture_stones(player, captured2)
        
        elif next_cell in QUAN_CELLS:
            return
        else:
            # Tiếp tục rải từ next_cell (không phải current_cell)
            self._simulate_move(board, next_cell, direction, player)
    
    def _evaluate(self, board, difficulty):
        """Đánh giá điểm số theo độ khó."""
        if difficulty == 'easy':
            return self._evaluate_simple(board)
        elif difficulty == 'medium':
            return self._evaluate_advanced(board)
        else:
            return self._evaluate_complex(board)
    
    def _evaluate_simple(self, board):
        """Heuristic đơn giản: Chênh lệch điểm."""
        score2 = board.calculate_score(2)
        score1 = board.calculate_score(1)
        return score2 - score1
    
    def _evaluate_advanced(self, board):
        """Heuristic nâng cao: Điểm + Vị trí + Quan + Mobility + Capture."""
        score2 = board.calculate_score(2)
        score1 = board.calculate_score(1)
        base_score = score2 - score1
        
        # Bonus nếu quan còn trên bàn cờ (quan của AI có giá trị hơn)
        quan_bonus = 0
        if not board.cells[5].is_empty():
            has_quan_5 = any(s.type == "Quan" for s in board.cells[5].stones)
            if has_quan_5:
                num_dan_5 = sum(1 for s in board.cells[5].stones if s.type != "Quan")
                quan_bonus += 5 + num_dan_5 * 0.3  # Quan của P2 quan trọng hơn
        if not board.cells[11].is_empty():
            has_quan_11 = any(s.type == "Quan" for s in board.cells[11].stones)
            if has_quan_11:
                num_dan_11 = sum(1 for s in board.cells[11].stones if s.type != "Quan")
                quan_bonus -= 5 + num_dan_11 * 0.3  # Quan của P1 (AI cần phòng thủ)
        
        # Bonus số đá trên bàn cờ
        p2_stones = sum(board.cells[i].count() for i in PLAYER2_CELLS)
        p1_stones = sum(board.cells[i].count() for i in PLAYER1_CELLS)
        position_bonus = (p2_stones - p1_stones) * 0.15
        
        # Mobility: Số nước đi có thể (AI có nhiều lựa chọn hơn = tốt hơn)
        p2_moves = len(self._get_possible_moves(board, 2))
        p1_moves = len(self._get_possible_moves(board, 1))
        mobility_bonus = (p2_moves - p1_moves) * 0.5
        
        # Capture potential: Đánh giá khả năng ăn đá
        capture_potential = self._evaluate_capture_potential(board, 2)
        
        return base_score + quan_bonus + position_bonus + mobility_bonus + capture_potential
    
    def _evaluate_complex(self, board):
        """Heuristic phức tạp: Tất cả + Chiến thuật + Defense + Aggressive."""
        score2 = board.calculate_score(2)
        score1 = board.calculate_score(1)
        base_score = score2 - score1
        
        # KIỂM TRA CƠ HỘI ĂN QUAN ĐỂ THẮNG - Ưu tiên cao nhất
        # Kiểm tra xem AI có thể ăn quan của đối thủ (cell 11) không
        capture_quan_bonus = 0
        if not board.cells[11].is_empty():
            has_quan_11 = any(s.type == "Quan" for s in board.cells[11].stones)
            if has_quan_11:
                num_dan_11 = sum(1 for s in board.cells[11].stones if s.type != "Quan")
                # Nếu có thể ăn quan (>= 5 dân), bonus rất lớn
                if num_dan_11 >= 5:
                    # Kiểm tra xem có nước đi nào có thể ăn quan này không
                    possible_moves_p2 = self._get_possible_moves(board, 2)
                    for cell_id, direction in possible_moves_p2:
                        board_test = self._copy_board(board)
                        self._simulate_move(board_test, cell_id, direction, 2)
                        # Nếu sau nước đi này, quan 11 bị ăn
                        if board_test.cells[11].is_empty():
                            capture_quan_bonus = 500  # Bonus cực lớn để ưu tiên
                            break
        
        # Đánh giá quan chi tiết hơn
        quan_bonus = 0
        if not board.cells[5].is_empty():
            has_quan_5 = any(s.type == "Quan" for s in board.cells[5].stones)
            if has_quan_5:
                num_dan_5 = sum(1 for s in board.cells[5].stones if s.type != "Quan")
                quan_bonus += 8 + num_dan_5 * 0.6  # Quan của P2 rất quan trọng
        if not board.cells[11].is_empty():
            has_quan_11 = any(s.type == "Quan" for s in board.cells[11].stones)
            if has_quan_11:
                num_dan_11 = sum(1 for s in board.cells[11].stones if s.type != "Quan")
                # Nếu quan của đối thủ có thể bị ăn, giảm bonus phòng thủ
                if num_dan_11 >= 5:
                    quan_bonus -= 10  # Phạt nếu để quan đối thủ dễ bị ăn
                else:
                    quan_bonus += 5 + num_dan_11 * 0.4  # Quan của P1 cần phòng thủ
        
        # Bonus vị trí (trọng số cao hơn)
        p2_stones = sum(board.cells[i].count() for i in PLAYER2_CELLS)
        p1_stones = sum(board.cells[i].count() for i in PLAYER1_CELLS)
        position_bonus = (p2_stones - p1_stones) * 0.2
        
        # Mobility với trọng số cao
        p2_moves = len(self._get_possible_moves(board, 2))
        p1_moves = len(self._get_possible_moves(board, 1))
        mobility_bonus = (p2_moves - p1_moves) * 0.8
        
        # Capture potential chi tiết
        capture_potential = self._evaluate_capture_potential(board, 2) * 1.5
        
        # Chiến thuật: Tạo cơ hội ăn quan
        strategy_bonus = 0
        for quan_cell in [5, 11]:
            if not board.cells[quan_cell].is_empty():
                has_quan = any(s.type == "Quan" for s in board.cells[quan_cell].stones)
                if has_quan:
                    num_dan = sum(1 for s in board.cells[quan_cell].stones if s.type != "Quan")
                    # Kiểm tra cả 2 hướng có thể tấn công
                    for offset in [-1, 1]:
                        prev_cell = (quan_cell + offset) % 12
                        if board.cells[prev_cell].is_empty():
                            # Có thể rải từ ô trước đó và kết thúc ở ô trống, sau đó ăn quan
                            if num_dan >= 5:
                                if quan_cell == 5:  # Quan của P2 - cần bảo vệ
                                    strategy_bonus -= 20  # Phạt nếu quan của mình bị đe dọa
                                else:  # Quan của P1 - cần tấn công
                                    strategy_bonus += 25  # Bonus lớn nếu có thể ăn quan đối thủ
        
        # Phân tích mối đe dọa (threat analysis) - cải thiện logic
        threat_penalty = 0
        # Đe dọa từ P1 đến các ô của P2
        for cell_id in PLAYER1_CELLS:
            if board.cells[cell_id].count() > 0:
                num_stones = board.cells[cell_id].count()
                # Kiểm tra cả 2 hướng
                for direction in ['left', 'right']:
                    if direction == 'left':
                        offset = 1  # P1 left = +1
                    else:
                        offset = -1  # P1 right = -1
                    
                    # Simulate: rải đá từ cell_id
                    current = cell_id
                    for _ in range(num_stones):
                        current = (current + offset) % 12
                    
                    next_cell = (current + offset) % 12
                    # Nếu kết thúc ở ô trống trong vùng của P2
                    if next_cell in PLAYER2_CELLS and board.cells[next_cell].is_empty():
                        capture_cell = (next_cell + offset) % 12
                        if capture_cell in PLAYER2_CELLS and not board.cells[capture_cell].is_empty():
                            capture_count = board.cells[capture_cell].count()
                            # Kiểm tra nếu có quan
                            has_quan = any(s.type == "Quan" for s in board.cells[capture_cell].stones)
                            if has_quan:
                                threat_penalty -= capture_count * 3  # Phạt rất nặng nếu mất quan
                            else:
                                threat_penalty -= capture_count * 1.5  # Phạt nếu mất dân
        
        # Defense bonus: Bảo vệ các ô quan trọng
        defense_bonus = 0
        for cell_id in PLAYER2_CELLS:
            if board.cells[cell_id].count() > 0:
                # Kiểm tra xem ô này có dễ bị tấn công không
                vulnerable = False
                for offset in [1, -1]:
                    prev_cell = (cell_id - offset) % 12
                    if prev_cell in PLAYER1_CELLS and board.cells[prev_cell].is_empty():
                        vulnerable = True
                        break
                if not vulnerable:
                    defense_bonus += board.cells[cell_id].count() * 0.2
        
        # Aggressive play: Khuyến khích tấn công quan của đối thủ khi có cơ hội
        aggressive_bonus = 0
        # Luôn khuyến khích tấn công quan đối thủ nếu có cơ hội
        if not board.cells[11].is_empty():
            has_quan_11 = any(s.type == "Quan" for s in board.cells[11].stones)
            if has_quan_11:
                num_dan_11 = sum(1 for s in board.cells[11].stones if s.type != "Quan")
                if num_dan_11 >= 5:
                    # Kiểm tra xem có nước đi nào có thể ăn quan này không
                    possible_moves_p2 = self._get_possible_moves(board, 2)
                    can_capture_quan = False
                    for cell_id, direction in possible_moves_p2:
                        board_test = self._copy_board(board)
                        self._simulate_move(board_test, cell_id, direction, 2)
                        if board_test.cells[11].is_empty():
                            can_capture_quan = True
                            break
                    
                    if can_capture_quan:
                        aggressive_bonus += 100  # Bonus cực lớn nếu có thể ăn quan ngay
                    else:
                        aggressive_bonus += 30  # Bonus lớn để tấn công quan đối thủ
                else:
                    aggressive_bonus += 5  # Vẫn có giá trị nhưng ít hơn
        
        return base_score + capture_quan_bonus + quan_bonus + position_bonus + mobility_bonus + \
               capture_potential + strategy_bonus + threat_penalty + defense_bonus + aggressive_bonus
    
        
    def _evaluate_capture_potential(self, board, player):
        """Đánh giá khả năng ăn đá trong nước đi tiếp theo."""
        potential = 0
        
        if player == 1:
            cells = PLAYER1_CELLS
            offset_left = 1
            offset_right = -1
        else:
            cells = PLAYER2_CELLS
            offset_left = -1
            offset_right = 1
        
        for cell_id in cells:
            if board.cells[cell_id].is_empty():
                continue
            
            num_stones = board.cells[cell_id].count()
            
            # Kiểm tra cả 2 hướng
            for offset in [offset_left, offset_right]:
                # Simulate rải đá
                current_cell = cell_id
                for _ in range(num_stones):
                    current_cell = (current_cell + offset) % 12
                
                next_cell = (current_cell + offset) % 12
                
                # Kiểm tra có thể ăn không
                if board.cells[next_cell].is_empty():
                    capture_cell = (next_cell + offset) % 12
                    if not board.cells[capture_cell].is_empty():
                        if capture_cell in QUAN_CELLS:
                            has_quan = any(s.type == "Quan" for s in board.cells[capture_cell].stones)
                            if has_quan:
                                num_dan = sum(1 for s in board.cells[capture_cell].stones if s.type != "Quan")
                                if num_dan >= 5:
                                    potential += 15  # Ăn quan = rất cao
                                else:
                                    continue  # Không đủ điều kiện
                            else:
                                potential += board.cells[capture_cell].count() * 2
                        else:
                            # Đếm số đá có thể ăn
                            capture_count = board.cells[capture_cell].count()
                            has_quan = any(s.type == "Quan" for s in board.cells[capture_cell].stones)
                            if has_quan:
                                potential += capture_count * 3  # Có quan
                            else:
                                potential += capture_count * 1.5  # Chỉ dân
                            
                            # Kiểm tra ăn liên tiếp
                            next_empty = (capture_cell + offset) % 12
                            if board.cells[next_empty].is_empty():
                                next_capture = (next_empty + offset) % 12
                                if not board.cells[next_capture].is_empty():
                                    potential += board.cells[next_capture].count() * 1.2
        
        return potential
    
    def _is_terminal(self, board):
        """Kiểm tra game kết thúc."""
        return board.cells[5].is_empty() and board.cells[11].is_empty()
    
    def _copy_board(self, board):
        """Copy board state để simulate."""
        from stone import GameBoard, Stone
        new_board = GameBoard()
        
        for cell_id in range(12):
            new_board.cells[cell_id].stones = []
            for stone in board.cells[cell_id].stones:
                new_stone = Stone(stone.id, stone.type, stone.image_path)
                new_stone.x = stone.x
                new_stone.y = stone.y
                new_board.cells[cell_id].stones.append(new_stone)
        
        new_board.player1_captured = [
            Stone(s.id, s.type, s.image_path) for s in board.player1_captured
        ]
        new_board.player2_captured = [
            Stone(s.id, s.type, s.image_path) for s in board.player2_captured
        ]
        
        return new_board
    
    def get_log_stats(self):
        """Lấy thống kê log."""
        return self.log.copy()

