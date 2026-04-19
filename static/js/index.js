

const socket = io();

// ─── State ──────────────────────────────────────────────────
let currentRoomId = null;
let currentTurn = 1;
let myPlayerNumber = null;   // 1 hoặc 2
let currentMode = null;   // 'pve' | 'pvp' | 'practice'
let currentScreen = 'menu-screen';
let screenHistory = [];
let selectedCellIndex = null;

let isAnimating = false;
let updateQueue = [];
let localBoardState = null;
let localScores = { 1: 0, 2: 0 };
const P1_CELLS = [6, 7, 8, 9, 10];
const P2_CELLS = [0, 1, 2, 3, 4];

const CELL_POS_DEFAULT = {
    0: { top: 325, left: 400 }, 1: { top: 325, left: 516 },
    2: { top: 325, left: 635 }, 3: { top: 325, left: 755 },
    4: { top: 325, left: 870 },
    6: { top: 465, left: 870 }, 7: { top: 465, left: 755 },
    8: { top: 465, left: 635 }, 9: { top: 465, left: 516 },
    10: { top: 465, left: 400 }
};

const CELL_POS_P2 = {
    0: { top: 465, left: 400 }, 1: { top: 465, left: 516 },
    2: { top: 465, left: 635 }, 3: { top: 465, left: 755 },
    4: { top: 465, left: 870 },
    6: { top: 325, left: 870 }, 7: { top: 325, left: 755 },
    8: { top: 325, left: 635 }, 9: { top: 325, left: 516 },
    10: { top: 325, left: 400 }
};
const preloadedImages = {};
const imgNames = [
    'Quan.png', 'Dan_1.png', 'Dan_2.png', 'Dan_3.png',
    'Dan_4.png', 'Dan_5.png', 'h0.png', 'h1.png', 'h2.png', 'h3.png'
];
let imagesLoadedCount = 0;
imgNames.forEach(name => {
    const img = new Image();
    img.onload = () => {
        if (++imagesLoadedCount === imgNames.length && localBoardState)
            renderBoardData(localBoardState, localScores);
    };
    img.src = `/static/images/${name}`;
    preloadedImages[name] = img;
});

const stonePositions = Array.from({ length: 12 }, (_, i) => {
    const isQuan = (i === 5 || i === 11);
    const cx = isQuan ? 50 : 45, cy = isQuan ? 80 : 45;
    const rx = isQuan ? 20 : 25, ry = isQuan ? 50 : 25;
    return Array.from({ length: 150 }, () => {
        const a = Math.random() * Math.PI * 2, r = Math.sqrt(Math.random());
        return { x: cx + Math.cos(a) * rx * r, y: cy + Math.sin(a) * ry * r, angle: Math.random() * 360 };
    });
});

function showScreen(screenId, parentId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const target = document.getElementById(screenId);
    if (!target) return;
    target.classList.add('active');
    if (parentId) screenHistory.push(parentId);
    currentScreen = screenId;
}

function goBack() {
    if (screenHistory.length > 0) {
        const prevId = screenHistory.pop();
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        const prev = document.getElementById(prevId);
        if (prev) { prev.classList.add('active'); currentScreen = prevId; }
    } else {
        goToMenu();
    }
}

function goToMenu() {
    screenHistory = [];
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById('menu-screen').classList.add('active');
    currentScreen = 'menu-screen';
}

function applyPlayerView(playerNum) {
    const posMap = (playerNum === 2) ? CELL_POS_P2 : CELL_POS_DEFAULT;

    // Đặt vị trí các ô cờ (bỏ qua ô Quan 5 và 11 – cố định ở CSS)
    for (const [idx, pos] of Object.entries(posMap)) {
        const cell = document.getElementById(`cell-${idx}`);
        if (cell) {
            cell.style.top = `${pos.top}px`;
            cell.style.left = `${pos.left}px`;
        }
    }

    const gs = document.getElementById('game-screen');
    const sp1 = document.getElementById('score-p1');
    const sp2 = document.getElementById('score-p2');
    const cp1 = document.getElementById('capture-p1');
    const cp2 = document.getElementById('capture-p2');

    if (playerNum === 2) {
        // P2 view: đổi background, hoán đổi vị trí score và capture area
        gs.style.backgroundImage = "url('/static/images/ingame_bg_p2.png')";
        if (sp1) { sp1.style.top = '200px'; sp1.style.left = '710px'; }
        if (sp2) { sp2.style.top = '620px'; sp2.style.left = '710px'; }
        if (cp1) { cp1.style.top = '40px'; cp1.style.left = '970px'; }
        if (cp2) { cp2.style.top = '580px'; cp2.style.left = '30px'; }
    } else {
        // P1 view (mặc định): P1 ở dưới, P2 ở trên
        gs.style.backgroundImage = "url('/static/images/ingame_bg_p1.png')";
        if (sp1) { sp1.style.top = '620px'; sp1.style.left = '710px'; }
        if (sp2) { sp2.style.top = '200px'; sp2.style.left = '710px'; }
        if (cp1) { cp1.style.top = '580px'; cp1.style.left = '30px'; }
        if (cp2) { cp2.style.top = '40px'; cp2.style.left = '970px'; }
    }
}


function resetLocalGameState() {
    localBoardState = null;
    localScores = { 1: 0, 2: 0 };
    currentTurn = 1;
    selectedCellIndex = null;
    isAnimating = false;
    updateQueue = [];
    currentRoomId = null;

    // Xóa canvas
    for (let i = 0; i < 12; i++) {
        const c = document.getElementById(`cell-${i}`);
        if (c) c.getContext('2d').clearRect(0, 0, c.width, c.height);
    }
    ['capture-p1', 'capture-p2'].forEach(id => {
        const c = document.getElementById(id);
        if (c) c.getContext('2d').clearRect(0, 0, c.width, c.height);
    });

    // Reset text
    document.getElementById('score-p1').innerText = '0';
    document.getElementById('score-p2').innerText = '0';

    // Reset UI
    document.getElementById('arrow-left').style.display = 'none';
    document.getElementById('arrow-right').style.display = 'none';
    document.getElementById('hand-cursor').style.display = 'none';
    const rc = document.getElementById('room-code-display');
    if (rc) rc.style.display = 'none';
    const ti = document.getElementById('turn-indicator');
    if (ti) ti.style.display = 'none';
    const ws = document.getElementById('win-screen');
    if (ws) ws.style.display = 'none';
    const btnUndo = document.getElementById('btn-undo');
    if (btnUndo) btnUndo.style.visibility = 'hidden';

    applyPlayerView(1);
}


function startGame(difficulty) {
    currentMode = 'pve';
    myPlayerNumber = 1;
    resetLocalGameState();
    socket.emit('create_room', { mode: 'pve', difficulty });
}

function startPractice() {
    currentMode = 'practice';
    myPlayerNumber = 1;
    resetLocalGameState();
    socket.emit('create_room', { mode: 'practice', room_name: null });
}

function handleCreateRoomAction() {
    const roomName = document.getElementById('create-room-input').value.trim().toUpperCase();
    if (!roomName) {
        showModal('Thông báo', 'Vui lòng nhập tên phòng!', [{ text: 'OK', cls: 'btn-ok', fn: closeModal }]);
        return;
    }
    currentMode = 'pvp';
    myPlayerNumber = 1;
    resetLocalGameState();
    socket.emit('create_room', { mode: 'pvp', room_name: roomName });
}

function handleCreateRandom() {
    document.getElementById('create-room-input').value = '';
    currentMode = 'pvp';
    myPlayerNumber = 1;
    resetLocalGameState();
    socket.emit('create_room', { mode: 'pvp', room_name: null });
}


function handleJoinRoomAction() {
    const roomId = document.getElementById('join-room-input').value.trim().toUpperCase();
    if (!roomId) {
        showModal('Thông báo', 'Vui lòng nhập mã phòng!', [{ text: 'OK', cls: 'btn-ok', fn: closeModal }]);
        return;
    }
    currentMode = 'pvp';
    myPlayerNumber = 2;
    socket.emit('join_room', { room_id: roomId });
}

function handleJoinRandom() {
    currentMode = 'pvp';
    myPlayerNumber = 2;
    socket.emit('find_random_room');
}


function handleExitGame() {
    showModal(
        'BẠN CÓ CHẮC MUỐN THOÁT?',
        'Thoát giữa chừng sẽ bị xử thua!',
        [
            { text: 'Hủy', cls: 'btn-cancel', fn: closeModal },
            { text: 'Xác nhận', cls: 'btn-confirm', fn: _doExitGame }
        ]
    );
}

function _doExitGame() {
    closeModal();
    if (currentRoomId) socket.emit('leave_room_event', { room_id: currentRoomId });
    resetLocalGameState();
    goToMenu();
}

function handleExitApp() {
    showModal(
        'THOÁT ỨNG DỤNG',
        'Bạn có chắc muốn thoát?',
        [
            { text: 'Hủy', cls: 'btn-cancel', fn: closeModal },
            { text: 'Xác nhận', cls: 'btn-confirm', fn: () => { closeModal(); window.close(); } }
        ]
    );
}

function handleUndo() {
    if (!currentRoomId || isAnimating || currentMode !== 'pve') return;
    socket.emit('undo_move', { room_id: currentRoomId });
}

function showModal(title, message, buttons) {
    document.getElementById('modal-title').innerText = title;
    document.getElementById('modal-message').innerText = message;
    const container = document.getElementById('modal-buttons');
    container.innerHTML = '';
    buttons.forEach(b => {
        const btn = document.createElement('button');
        btn.className = `modal-btn ${b.cls}`;
        btn.innerText = b.text;
        btn.onclick = b.fn;
        container.appendChild(btn);
    });
    document.getElementById('exit-modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('exit-modal').style.display = 'none';
}

function showWinScreen(winner) {
    const screen = document.getElementById('win-screen');
    const img = document.getElementById('win-image');
    img.src = `/static/images/player${winner}_win.png`;
    screen.style.display = 'flex';
    setTimeout(() => {
        screen.style.display = 'none';
        resetLocalGameState();
        goToMenu();
    }, 3000);
}

socket.on('room_created', (data) => {
    currentRoomId = data.room_id;
    showScreen('game-screen', currentScreen);

    if (data.mode === 'pvp') {
        _showRoomCode(data.room_id, 'Phòng của bạn');
    }
    if (data.mode === 'pve') {
        const btnUndo = document.getElementById('btn-undo');
        if (btnUndo) btnUndo.style.visibility = 'visible';
    }
    _updateTurnIndicator();
});

socket.on('join_success', (data) => {
    const roomId = data.room_id;
    resetLocalGameState();       // reset board cũ, reset về P1 view trước
    currentRoomId = roomId;     // reset đặt null, cần set lại
    currentMode = 'pvp';
    myPlayerNumber = 2;
    applyPlayerView(2);
    showScreen('game-screen', currentScreen);
    _showRoomCode(roomId, 'Bạn đã vào phòng');
    _updateTurnIndicator();
});

socket.on('room_error', (data) => {
    showModal('Thông báo', data.message, [{ text: 'OK', cls: 'btn-ok', fn: closeModal }]);
});

socket.on('opponent_left', (data) => {
    showModal('Thông báo', data.message, [{
        text: 'OK', cls: 'btn-ok', fn: () => {
            closeModal();
            resetLocalGameState();
            goToMenu();
        }
    }]);
});

socket.on('update_board', (gameState) => {
    updateQueue.push(gameState);
    processQueue();
});

function _showRoomCode(roomId, label) {
    const rc = document.getElementById('room-code-display');
    if (!rc) return;
    rc.innerHTML = `${label}: <span class="room-code-value">${roomId}</span>`;
    rc.style.display = 'block';
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function processQueue() {
    if (isAnimating || updateQueue.length === 0) return;
    isAnimating = true;

    while (updateQueue.length > 0) {
        const gs = updateQueue.shift();

        if (!localBoardState) {
            localBoardState = JSON.parse(JSON.stringify(gs.board));
            localScores = JSON.parse(JSON.stringify(gs.scores));
            renderBoardData(localBoardState, localScores);
        } else if (gs.anim_log && gs.anim_log.length > 0) {
            await playAnimations(gs.anim_log);
        }

        localBoardState = JSON.parse(JSON.stringify(gs.board));
        localScores = JSON.parse(JSON.stringify(gs.scores));
        currentTurn = gs.turn;

        // Practice: đổi vai theo lượt
        if (currentMode === 'practice') myPlayerNumber = currentTurn;

        // Cập nhật turn indicator mọi chế độ
        _updateTurnIndicator();

        // Cập nhật nút Undo (chỉ PvE)
        if (currentMode === 'pve') {
            const btnUndo = document.getElementById('btn-undo');
            if (btnUndo) btnUndo.style.visibility = gs.can_undo ? 'visible' : 'hidden';
        }

        renderBoardData(localBoardState, localScores);

        if (gs.is_game_over) {
            const w = gs.winner;
            const scores = `P1: ${localScores[1]} – P2: ${localScores[2]}`;
            setTimeout(() => {
                if (currentMode === 'pvp') {
                    showWinScreen(w);
                } else {
                    let title;
                    if (w === 0) {
                        title = 'HÒA!';
                    } else if (currentMode === 'pve') {
                        title = w === 1 ? 'BẠN THẮNG!' : 'AI THẮNG!';
                    } else {
                        title = `PLAYER ${w} THẮNG!`;
                    }
                    showModal(title, scores, [{
                        text: 'OK', cls: 'btn-confirm', fn: () => {
                            closeModal();
                            resetLocalGameState();
                            goToMenu();
                        }
                    }]);
                }
            }, 800);
        }
    }

    isAnimating = false;
}


function _updateTurnIndicator() {
    const ti = document.getElementById('turn-indicator');
    if (!ti || !currentMode) return;

    const isMyTurn = (currentTurn === myPlayerNumber);
    let text, cls;

    if (currentMode === 'practice') {
        text = `Lượt: Player ${currentTurn}`;
        cls = `player${currentTurn}`;
    } else if (currentMode === 'pve') {
        text = isMyTurn ? 'Lượt: Bạn ▶' : '⏳ AI đang suy nghĩ...';
        cls = isMyTurn ? 'player1' : 'player2';
    } else if (currentMode === 'pvp') {
        text = isMyTurn ? 'Lượt: Bạn ▶' : '⏳ Đối thủ...';
        cls = isMyTurn ? 'player1' : 'player2';
    } else {
        return;
    }

    ti.style.display = 'block';
    ti.innerText = text;
    ti.className = `turn-indicator ${cls}`;
}

async function playAnimations(animLog) {
    const hand = document.getElementById('hand-cursor');
    hand.style.display = 'block';
    let lastIdx = -1;

    for (const action of animLog) {
        const { cell: cellIdx, type } = action;
        const cellElem = document.getElementById(`cell-${cellIdx}`);
        if (!cellElem) continue;

        if (cellIdx !== lastIdx) {
            const r = cellElem.getBoundingClientRect();
            const b = document.getElementById('game-board').getBoundingClientRect();
            hand.style.left = `${r.left - b.left + r.width / 2}px`;
            hand.style.top = `${r.top - b.top + r.height / 2}px`;
            await sleep(300);
            lastIdx = cellIdx;
        }

        if (type === 'pick') {
            hand.style.backgroundImage = "url('/static/images/h1.png')";
            localBoardState[cellIdx].dan = 0;
            await sleep(200);
        } else if (type === 'drop') {
            hand.style.backgroundImage = "url('/static/images/h0.png')";
            localBoardState[cellIdx].dan += 1;
            await sleep(150);
        } else if (type === 'slap_empty') {
            hand.style.backgroundImage = "url('/static/images/h3.png')";
            hand.style.transform = "translate(-50%, -50%) scale(1.3)";
            await sleep(150);
            hand.style.transform = "translate(-50%, -50%) scale(1)";
            await sleep(150);
        } else if (type === 'capture') {
            hand.style.backgroundImage = "url('/static/images/h1.png')";
            localBoardState[cellIdx].quan = 0;
            localBoardState[cellIdx].dan = 0;
            await sleep(300);
            hand.style.backgroundImage = "url('/static/images/h0.png')";
        }
        renderBoardData(localBoardState, localScores);
    }
    hand.style.display = 'none';
}


function renderBoardData(boardData, scoresData) {
    document.getElementById('score-p1').innerText = scoresData[1];
    document.getElementById('score-p2').innerText = scoresData[2];
    renderCaptured('capture-p1', scoresData[1]);
    renderCaptured('capture-p2', scoresData[2]);

    for (let i = 0; i < 12; i++) {
        const canvas = document.getElementById(`cell-${i}`);
        if (!canvas) continue;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const cell = boardData[i];
        let si = 0;

        for (let q = 0; q < cell.quan; q++) {
            if (preloadedImages['Quan.png']?.complete) {
                const p = stonePositions[i][si++ % 150];
                ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.angle * Math.PI / 180);
                ctx.drawImage(preloadedImages['Quan.png'], -20, -20, 40, 40); ctx.restore();
            }
        }
        for (let d = 0; d < cell.dan; d++) {
            const name = `Dan_${(si % 5) + 1}.png`;
            if (preloadedImages[name]?.complete) {
                const p = stonePositions[i][si++ % 150];
                ctx.drawImage(preloadedImages[name], p.x - 7.5, p.y - 7.5, 15, 15);
            }
        }
    }
}

function renderCaptured(canvasId, score) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    let sX = 10, sY = 10;
    const qC = Math.floor(score / 10), dC = score % 10;

    for (let i = 0; i < qC; i++) {
        if (preloadedImages['Quan.png']?.complete)
            ctx.drawImage(preloadedImages['Quan.png'], sX, sY, 40, 40);
        sX += 45;
        if (sX > canvas.width - 40) { sX = 10; sY += 45; }
    }
    sX = 10; sY = qC > 0 ? sY + 45 : 10;
    for (let i = 0; i < dC; i++) {
        const n = `Dan_${(i % 5) + 1}.png`;
        if (preloadedImages[n]?.complete)
            ctx.drawImage(preloadedImages[n], sX, sY, 20, 20);
        sX += 25;
        if (sX > canvas.width - 20) { sX = 10; sY += 25; }
    }
}


function selectCell(index) {
    if (isAnimating) return;
    if (currentTurn !== myPlayerNumber) return;

    // Chỉ được chọn ô của mình
    if (myPlayerNumber === 1 && !P1_CELLS.includes(index)) return;
    if (myPlayerNumber === 2 && !P2_CELLS.includes(index)) return;

    if (!localBoardState || localBoardState[index].dan === 0) return;

    selectedCellIndex = index;
    const rect = document.getElementById(`cell-${index}`).getBoundingClientRect();
    const boardRect = document.getElementById('game-board').getBoundingClientRect();
    const top = rect.top - boardRect.top;
    const left = rect.left - boardRect.left;

    const aL = document.getElementById('arrow-left');
    const aR = document.getElementById('arrow-right');
    aL.style.display = aR.style.display = 'block';
    aL.style.top = aR.style.top = `${top + 20}px`;
    aL.style.left = `${left - 60}px`;
    aR.style.left = `${left + 100}px`;
}


function confirmMove(direction) {
    if (selectedCellIndex === null || !currentRoomId) return;
    document.getElementById('arrow-left').style.display = 'none';
    document.getElementById('arrow-right').style.display = 'none';
    socket.emit('make_move', {
        room_id: currentRoomId,
        cell_index: selectedCellIndex,
        direction: direction,
    });
    selectedCellIndex = null;
}

document.addEventListener('click', e => {
    if (!e.target.classList.contains('cell-btn') &&
        !e.target.classList.contains('direction-arrow')) {
        document.getElementById('arrow-left').style.display = 'none';
        document.getElementById('arrow-right').style.display = 'none';
    }
});