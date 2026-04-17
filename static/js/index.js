// Kết nối tới SocketIO Server
const socket = io();
let currentRoomId = null;
let currentTurn = 1;

let currentScreen = 'menu-screen';
let screenHistory = [];

function showScreen(screenId, parentId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const target = document.getElementById(screenId);
    if (target) {
        target.classList.add('active');
        if (parentId) screenHistory.push(parentId);
        currentScreen = screenId;
    }
}

function goBack() {
    if (screenHistory.length > 0) {
        const prevScreenId = screenHistory.pop();
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        document.getElementById(prevScreenId).classList.add('active');
        currentScreen = prevScreenId;
    } else {
        showScreen('menu-screen');
    }
}

function startGame(difficulty) {
    socket.emit('create_room', { mode: 'pve', difficulty: difficulty });
}

function handleCreateRoomAction() {
    socket.emit('create_room', { mode: 'pvp' });
}

function handleJoinRoomAction() {
    const roomId = document.getElementById('join-room-input').value;
    socket.emit('join_room', { room_id: roomId });
}

// Lắng nghe sự kiện từ Server
socket.on('room_created', (data) => {
    currentRoomId = data.room_id;
    console.log("Joined Room:", currentRoomId);
    showScreen('game-screen', currentScreen);
});

socket.on('update_board', (gameState) => {
    renderBoard(gameState);
});

// YÊU CẦU 2: LOAD ẢNH QUAN VÀ DÂN VÀO CÁC ELEMENT
function renderBoard(gameState) {
    currentTurn = gameState.turn;

    // Cập nhật điểm
    document.getElementById('score-p1').innerText = gameState.scores[1];
    document.getElementById('score-p2').innerText = gameState.scores[2];

    const board = gameState.board;

    for (let i = 0; i < 12; i++) {
        const cellBtn = document.getElementById(`cell-${i}`);
        cellBtn.innerHTML = ''; // Xóa sạch HTML cũ (reset ô)

        const cellData = board[i];

        // 1. Thêm ảnh Quan nếu có
        for (let q = 0; q < cellData.quan; q++) {
            const imgQuan = document.createElement('img');
            imgQuan.src = '../static/images/quan.png'; // Đường dẫn tới ảnh thật
            imgQuan.classList.add('stone-quan'); // Dùng class để style width/height

            // Xoay ngẫu nhiên cho tự nhiên
            imgQuan.style.transform = `rotate(${Math.random() * 360}deg)`;
            cellBtn.appendChild(imgQuan);
        }

        // 2. Thêm ảnh Dân
        for (let d = 0; d < cellData.dan; d++) {
            const imgDan = document.createElement('img');
            imgDan.src = '../static/images/dan_1.png'; // Bạn có thể random dan_1, dan_2
            imgDan.classList.add('stone-dan');

            // Dịch chuyển nhẹ ngẫu nhiên để không bị đè cứng nhắc
            imgDan.style.transform = `translate(${Math.random() * 6 - 3}px, ${Math.random() * 6 - 3}px)`;
            cellBtn.appendChild(imgDan);
        }
    }
}

// Xử lý khi click vào 1 ô (Chọn hướng rải)
let selectedCell = null;
function handleCell(index) {
    // Chỉ cho phép click vào ô của mình (Giả sử client đang chơi P1 là ô 6-10)
    if (index >= 6 && index <= 10) {
        selectedCell = index;

        // Hiển thị UI chọn hướng (Trái/Phải) bằng prompt tạm thời hoặc modal UI của bạn
        const direction = confirm("Chọn OK để rải Phải, Cancel để rải Trái") ? 'right' : 'left';

        socket.emit('make_move', {
            room_id: currentRoomId,
            cell_index: selectedCell,
            direction: direction
        });
    } else {
        console.log("Không phải ô của bạn hoặc ô Quan!");
    }
}