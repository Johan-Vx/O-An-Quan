"""Quản lý viên đá và ô trên bàn cờ."""
import random
from PIL import Image
from constants import *


class Stone:
    """Một viên đá riêng biệt."""
    def __init__(self, stone_id, stone_type, image_path):
        self.id = stone_id
        self.type = stone_type
        self.image_path = image_path
        self.image = None
        self.x = 0
        self.y = 0
        self.canvas_id = None
        
    def load_image(self, size=STONE_SIZE):
        """Load và resize ảnh."""
        try:
            img = Image.open(self.image_path).convert("RGBA")
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            print(f"Lỗi load ảnh {self.image_path}: {e}")
            img = Image.new("RGBA", (size, size), (100, 100, 100, 255))
            return img
    
    def __repr__(self):
        return f"Stone(id={self.id}, type={self.type}, pos=({self.x},{self.y}))"


class Cell:
    """Một ô trên bàn cờ."""
    
    def __init__(self, cell_id, cell_type, center_x, center_y):
        self.id = cell_id
        self.type = cell_type
        self.center = (center_x, center_y)
        self.stones = []
        self.radius = CELL_RADIUS
        
    def add_stone(self, stone, randomize=True):
        """Thêm đá vào ô."""
        if randomize:
            max_attempts = 20
            best_pos = None
            best_distance = 0
            
            for _ in range(max_attempts):
                offset_x = random.randint(-self.radius + 10, self.radius - 10)
                offset_y = random.randint(-self.radius + 10, self.radius - 10)
                test_x = self.center[0] + offset_x
                test_y = self.center[1] + offset_y
                
                min_distance = float('inf')
                for other_stone in self.stones:
                    dist = ((test_x - other_stone.x)**2 + (test_y - other_stone.y)**2)**0.5
                    min_distance = min(min_distance, dist)
                
                if min_distance > best_distance:
                    best_distance = min_distance
                    best_pos = (test_x, test_y)
            
            if best_pos:
                stone.x, stone.y = best_pos
            else:
                stone.x = self.center[0]
                stone.y = self.center[1]
        else:
            stone.x = self.center[0]
            stone.y = self.center[1]
        
        self.stones.append(stone)
        
    def remove_all_stones(self):
        """Bốc hết đá trong ô."""
        stones = self.stones[:]
        self.stones = []
        return stones
    
    def count(self):
        """Đếm số đá trong ô."""
        return len(self.stones)
    
    def is_empty(self):
        """Kiểm tra ô có rỗng không."""
        return len(self.stones) == 0
    
    def __repr__(self):
        return f"Cell(id={self.id}, type={self.type}, stones={len(self.stones)})"


class GameBoard:
    """Quản lý toàn bộ bàn cờ và đá."""
    
    def __init__(self):
        self.cells = {}
        self.player1_captured = []
        self.player2_captured = []
        self.next_stone_id = 0
        
        for cell_id, pos in CELL_POSITIONS.items():
            cell_type = "quan" if cell_id in QUAN_CELLS else "dan"
            self.cells[cell_id] = Cell(cell_id, cell_type, pos[0], pos[1])
    
    def init_stones(self, board_state=None):
        """Khởi tạo đá theo state."""
        if board_state is None:
            board_state = INITIAL_BOARD_STATE
        
        for cell_id, count in enumerate(board_state):
            cell = self.cells[cell_id]
            
            for _ in range(count):
                stone = self._create_stone(cell_id)
                cell.add_stone(stone, randomize=True)
    
    def _create_stone(self, cell_id):
        """Tạo một viên đá mới."""
        stone_id = self.next_stone_id
        self.next_stone_id += 1
        
        if cell_id in QUAN_CELLS:
            stone_type = "Quan"
            image_path = IMAGE_QUAN
        else:
            image_path = random.choice(DAN_IMAGES)
            stone_type = image_path.split("/")[-1].replace(".png", "")
        
        return Stone(stone_id, stone_type, image_path)
    
    def get_board_state(self):
        """Trả về state hiện tại."""
        return [self.cells[i].count() for i in range(12)]
    
    def pick_stones(self, cell_id):
        """Bốc hết đá từ ô."""
        return self.cells[cell_id].remove_all_stones()
    
    def drop_stone(self, cell_id, stone):
        """Thả một viên đá vào ô."""
        self.cells[cell_id].add_stone(stone, randomize=True)
    
    def capture_stones(self, player, stones):
        """Ăn đá - thêm vào vùng điểm."""
        if player == 1:
            self.player1_captured.extend(stones)
        else:
            self.player2_captured.extend(stones)
    
    def get_captured_count(self, player):
        """Đếm số đá ăn được."""
        if player == 1:
            return len(self.player1_captured)
        else:
            return len(self.player2_captured)
    
    def calculate_score(self, player):
        """Tính điểm của player."""
        captured = self.player1_captured if player == 1 else self.player2_captured
        score = 0
        for stone in captured:
            if stone.type == "Quan":
                score += 10
            else:
                score += 1
        return score
    
    def __repr__(self):
        state = self.get_board_state()
        return f"GameBoard(state={state}, P1_cap={len(self.player1_captured)}, P2_cap={len(self.player2_captured)})"