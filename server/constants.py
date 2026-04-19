"""Constants và cấu hình cho game Ô Ăn Quan."""

WINDOW_WIDTH = 1366
WINDOW_HEIGHT = 768
WINDOW_TITLE = "Ô Ăn Quan"

IMAGE_PATH = "Images/"
IMAGE_MENU = IMAGE_PATH + "menu.png"
IMAGE_CHOOSE = IMAGE_PATH + "choose.png"
IMAGE_INGAME_BG = IMAGE_PATH + "ingame_bg.png"
IMAGE_QUAN = IMAGE_PATH + "Quan.png"
IMAGE_DAN_1 = IMAGE_PATH + "Dan_1.png"
IMAGE_DAN_2 = IMAGE_PATH + "Dan_2.png"
IMAGE_DAN_3 = IMAGE_PATH + "Dan_3.png"
IMAGE_DAN_4 = IMAGE_PATH + "Dan_4.png"
IMAGE_DAN_5 = IMAGE_PATH + "Dan_5.png"
IMAGE_H0 = IMAGE_PATH + "h0.png"
IMAGE_H1 = IMAGE_PATH + "h1.png"
IMAGE_H2 = IMAGE_PATH + "h2.png"
IMAGE_H3 = IMAGE_PATH + "h3.png"
IMAGE_LEFT = IMAGE_PATH + "left.png"
IMAGE_RIGHT = IMAGE_PATH + "right.png"
IMAGE_PLAYER1_WIN = IMAGE_PATH + "player1_win.png"
IMAGE_PLAYER2_WIN = IMAGE_PATH + "player2_win.png"

DAN_IMAGES = [IMAGE_DAN_1, IMAGE_DAN_2, IMAGE_DAN_3, IMAGE_DAN_4, IMAGE_DAN_5]

CELL_POSITIONS = {
    0: (427, 325),
    1: (552, 325), 
    2: (677, 325),
    3: (802, 325), 
    4: (927, 325), 
    5: (1056, 395),
    6: (927, 465),
    7: (802, 465),
    8: (677, 465), 
    9: (552, 465), 
    10: (427, 465), 
    11: (298, 395),
}

CELL_RADIUS = 35

SCORE_AREA_P1 = {
    "x1": 115,
    "y1": 545,
    "x2": 305,
    "y2": 725,
    "center": (210, 635)
}

SCORE_AREA_P2 = {
    "x1": 1090,
    "y1": 60,
    "x2": 1275,
    "y2": 225,
    "center": (1130, 140)
}

STONE_SIZE = 28
STONE_SIZE_CAPTURED = 22
QUAN_SIZE = 50

MENU_BUTTON_PVP = {
    "x": 339,
    "y": 335,
    "width":301,
    "height": 136
}

MENU_BUTTON_PVE = {
    "x": 685,
    "y":335,
    "width": 301,
    "height":136
}

MENU_BUTTON_EXIT = {
    "x": 1032,
    "y": 316,
    "width": 300,
    "height": 92
}

CHOOSE_BUTTON_EASY = {
    "x": 354,
    "y": 332,
    "width": 258,
    "height": 80
}

CHOOSE_BUTTON_MEDIUM = {
    "x": 682,
    "y": 332,
    "width": 260,
    "height": 80
}

CHOOSE_BUTTON_HARD = {
    "x": 683,
    "y": 625,
    "width": 460,
    "height": 80
}

CHOOSE_BUTTON_BACK = {
    "x": 90,
    "y": 82,
    "width": 60,
    "height": 60
}

INGAME_BUTTON_UNDO = {
    "x": 197,
    "y": 52,
    "width": 50,
    "height": 50
}

INGAME_BUTTON_EXIT = {
    "x": 62,
    "y": 56,
    "width": 85,
    "height": 85
}

COLOR_BUTTON_HOVER = "#FFD700"
COLOR_TRANSPARENT = (0, 0, 0, 0)

ANIMATION_SPEED = 0.3
HAND_OFFSET_Y = 0

INITIAL_BOARD_STATE = [5, 5, 5, 5, 5, 1, 5, 5, 5, 5, 5, 1]

PLAYER1_CELLS = [6, 7, 8, 9, 10]
PLAYER2_CELLS = [0, 1, 2, 3, 4]
QUAN_CELLS = [5, 11]