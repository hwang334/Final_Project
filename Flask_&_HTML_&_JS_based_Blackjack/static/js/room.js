// 获取房间ID
const roomId = window.location.pathname.split('/').pop();
// 从localStorage获取玩家名称
const playerName = localStorage.getItem('playerName') || `玩家${Math.floor(Math.random() * 1000)}`;

// Socket.IO连接
let socket;

// DOM元素
const roomNameEl = document.getElementById('room-name');
const leaveRoomBtn = document.getElementById('leave-room-btn');
const gameMessageEl = document.getElementById('game-message');
const dealerCardsEl = document.getElementById('dealer-cards');
const dealerScoreEl = document.getElementById('dealer-score');
const playersListEl = document.getElementById('players-list');
const playerCardsEl = document.getElementById('player-cards');
const playerScoreEl = document.getElementById('player-score');
const playerMoneyEl = document.getElementById('player-money');
const currentBetEl = document.getElementById('current-bet');
const readyControlsEl = document.getElementById('ready-controls');
const readyBtn = document.getElementById('ready-btn');
const bettingControlsEl = document.getElementById('betting-controls');
const betAmountEl = document.getElementById('bet-amount');
const placeBetBtn = document.getElementById('place-bet-btn');
const actionControlsEl = document.getElementById('action-controls');
const hitBtn = document.getElementById('hit-btn');
const standBtn = document.getElementById('stand-btn');
const doubleDownBtn = document.getElementById('double-down-btn');
const endGameControlsEl = document.getElementById('end-game-controls');
const nextRoundBtn = document.getElementById('next-round-btn');

// 游戏状态
let gameState = null;
let playerId = null;
let currentPlayer = null;

// 初始化
function init() {
    // 建立Socket连接
    connectSocket();
    
    // 加入房间
    setTimeout(() => {
        socket.emit('join_room', {
            room_id: roomId,
            player_name: playerName
        });
    }, 1000);
    
    // 监听Socket事件
    setupSocketListeners();
    
    // 添加事件监听
    setupEventListeners();
}

// 建立Socket连接
function connectSocket() {
    // 尝试从localStorage获取会话ID
    const storedSessionId = localStorage.getItem('session_id');
    
    // 创建Socket连接，支持移动设备
    if (storedSessionId) {
        socket = io({
            query: {
                session_id: storedSessionId
            },
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionAttempts: 5
        });
    } else {
        socket = io({
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionAttempts: 5
        });
    }
}

// 设置Socket事件监听
function setupSocketListeners() {
    // 连接成功
    socket.on('connect', () => {
        console.log('连接到服务器');
        playerId = socket.id;
    });
    
    // 连接错误
    socket.on('connect_error', (error) => {
        console.error('连接错误:', error);
        gameMessageEl.textContent = '连接错误，请刷新页面重试';
        gameMessageEl.className = 'game-message error';
    });
    
    // 断开连接
    socket.on('disconnect', (reason) => {
        console.log('断开连接:', reason);
        if (reason === 'io server disconnect') {
            // 服务器断开连接，尝试重新连接
            socket.connect();
        }
        gameMessageEl.textContent = '与服务器断开连接，尝试重新连接...';
        gameMessageEl.className = 'game-message error';
    });
    
    // 重新连接
    socket.on('reconnect', (attemptNumber) => {
        console.log('重新连接成功，尝试次数:', attemptNumber);
        gameMessageEl.textContent = '重新连接成功';
        gameMessageEl.className = 'game-message';
        
        // 重新加入房间
        socket.emit('join_room', {
            room_id: roomId,
            player_name: playerName
        });
    });
    
    // 会话ID设置
    socket.on('set_session_id', (data) => {
        localStorage.setItem('session_id', data.session_id);
        console.log('存储会话ID:', data.session_id);
    });
    
    // 接收房间数据
    socket.on('room_data', (data) => {
        console.log('接收到房间数据:', data);
        updateRoomData(data);
    });
    
    // 游戏状态更新
    socket.on('game_update', (data) => {
        console.log('游戏状态更新:', data);
        updateRoomData(data);
    });
    
    // 新玩家加入
    socket.on('player_joined', (data) => {
        console.log('新玩家加入:', data);
        // 显示通知
        showNotification(`${data.player.name} 加入了游戏`);
    });
    
    // 玩家离开
    socket.on('player_left', (data) => {
        console.log('玩家离开:', data);
        // 显示通知
        if (gameState && gameState.players && gameState.players[data.player_id]) {
            showNotification(`${gameState.players[data.player_id].name} 离开了游戏`);
        } else {
            showNotification('有玩家离开了游戏');
        }
    });
    
    // 监听玩家状态更新事件
    socket.on('player_status_update', (data) => {
        console.log('玩家状态更新:', data);
        
        // 如果是当前玩家
        if (data.player_id === socket.id) {
            if (currentPlayer) {
                currentPlayer.state = data.player_state;
            }
            
            // 更新UI
            updateGameControls();
        }
        
        // 更新玩家列表中的状态
        updatePlayerStatus(data.player_id, data.player_state);
    });
    
    // 错误消息
    socket.on('error', (data) => {
        console.error('错误:', data);
        alert(data.message);
    });
}

// 设置事件监听
function setupEventListeners() {
    // 离开房间按钮
    leaveRoomBtn.addEventListener('click', () => {
        leaveRoom();
    });
    
    // 准备按钮
    readyBtn.addEventListener('click', () => {
        socket.emit('player_ready', {
            room_id: roomId
        });
        
        // 禁用准备按钮，防止重复点击
        readyBtn.disabled = true;
        readyBtn.textContent = '已准备';
    });
    
    // 下注按钮
    placeBetBtn.addEventListener('click', () => {
        const betAmount = parseInt(betAmountEl.value);
        if (isNaN(betAmount) || betAmount <= 0) {
            alert('请输入有效的下注金额');
            return;
        }
        
        socket.emit('place_bet', {
            room_id: roomId,
            bet_amount: betAmount
        });
    });
    
    // 要牌按钮
    hitBtn.addEventListener('click', () => {
        socket.emit('hit', {
            room_id: roomId
        });
    });
    
    // 停牌按钮
    standBtn.addEventListener('click', () => {
        socket.emit('stand', {
            room_id: roomId
        });
    });
    
    // 双倍下注按钮
    doubleDownBtn.addEventListener('click', () => {
        socket.emit('double_down', {
            room_id: roomId
        });
    });
    
    // 下一轮按钮
    nextRoundBtn.addEventListener('click', () => {
        socket.emit('next_round', {
            room_id: roomId
        });
    });
}

// 更新房间数据
function updateRoomData(data) {
    gameState = data;
    
    // 更新房间名称
    roomNameEl.textContent = data.room_name;
    
    // 更新游戏消息
    gameMessageEl.textContent = data.message;
    
    // 更新庄家牌
    updateDealerCards(data.dealer);
    
    // 更新玩家列表
    updatePlayersList(data.players);
    
    // 更新当前玩家
    updateCurrentPlayer();
    
    // 更新游戏控制
    updateGameControls();
}

// 更新庄家牌
function updateDealerCards(dealer) {
    dealerCardsEl.innerHTML = '';
    
    // 显示庄家牌
    dealer.hand.forEach(card => {
        const cardEl = createCardElement(card);
        dealerCardsEl.appendChild(cardEl);
    });
    
    // 更新庄家分数
    dealerScoreEl.textContent = `(${dealer.score})`;
}

// 更新玩家列表
function updatePlayersList(players) {
    playersListEl.innerHTML = '';
    
    // 玩家顺序
    const playerOrder = gameState.player_order || Object.keys(players);
    
    // 显示其他玩家
    playerOrder.forEach(playerId => {
        if (playerId === socket.id) return; // 跳过当前玩家
        
        const player = players[playerId];
        
        const playerEl = document.createElement('div');
        playerEl.className = 'player-item';
        playerEl.setAttribute('data-player-id', playerId);
        
        // 高亮当前行动玩家
        if (gameState.game_state === 'playing' && 
            gameState.player_order[gameState.current_player_index] === playerId) {
            playerEl.classList.add('current-turn');
        }
        
        // 设置玩家状态样式
        let statusClass = 'status-waiting';
        let statusText = '等待中';
        
        if (player.state === 'ready') {
            statusClass = 'status-ready';
            statusText = '已准备';
        } else if (player.state === 'betting') {
            statusClass = 'status-betting';
            statusText = '下注中';
        } else if (player.state === 'playing') {
            statusClass = 'status-playing';
            statusText = '游戏中';
        } else if (player.state === 'stand') {
            statusClass = 'status-stand';
            statusText = '停牌';
        } else if (player.state === 'busted') {
            statusClass = 'status-busted';
            statusText = '爆牌';
        } else if (player.state === 'blackjack') {
            statusClass = 'status-blackjack';
            statusText = 'BlackJack';
        } else if (player.state === 'five_dragon') {
            statusClass = 'status-five-dragon';
            statusText = '五小龙';
        }
        
        playerEl.innerHTML = `
            <div class="player-name">${player.name}</div>
            <div class="player-status ${statusClass}">${statusText}</div>
            <div class="player-money">¥${player.money}</div>
            <div class="player-bet">下注: ¥${player.current_bet}</div>
            <div class="player-cards-container">
                <div class="player-score">${player.score > 0 ? `(${player.score})` : ''}</div>
                <div class="player-cards" id="player-cards-${playerId}"></div>
            </div>
        `;
        
        playersListEl.appendChild(playerEl);
        
        // 显示玩家牌
        const playerCardsContainer = document.getElementById(`player-cards-${playerId}`);
        if (playerCardsContainer) {
            player.hand.forEach(card => {
                const cardEl = createCardElement(card);
                cardEl.classList.add('card-small'); // 其他玩家的牌显示小一点
                playerCardsContainer.appendChild(cardEl);
            });
        }
    });
}

// 更新当前玩家
function updateCurrentPlayer() {
    if (!gameState || !gameState.players) return;
    
    // 获取当前玩家
    currentPlayer = gameState.players[socket.id];
    if (!currentPlayer) return;
    
    // 更新当前玩家信息
    playerMoneyEl.textContent = currentPlayer.money;
    currentBetEl.textContent = currentPlayer.current_bet;
    
    // 更新玩家牌
    playerCardsEl.innerHTML = '';
    currentPlayer.hand.forEach(card => {
        const cardEl = createCardElement(card);
        playerCardsEl.appendChild(cardEl);
    });
    
    // 更新玩家分数
    playerScoreEl.textContent = `(${currentPlayer.score})`;
}

// 更新游戏控制
function updateGameControls() {
    if (!gameState || !currentPlayer) return;
    
    // 显示/隐藏准备按钮
    if (gameState.game_state === 'waiting' && currentPlayer.state === 'waiting') {
        readyControlsEl.style.display = 'block';
        readyBtn.disabled = false;
        readyBtn.textContent = '准备';
        bettingControlsEl.style.display = 'none';
        actionControlsEl.style.display = 'none';
        endGameControlsEl.style.display = 'none';
    }
    // 已准备状态
    else if (gameState.game_state === 'waiting' && currentPlayer.state === 'ready') {
        readyControlsEl.style.display = 'block';
        readyBtn.disabled = true;
        readyBtn.textContent = '已准备';
        bettingControlsEl.style.display = 'none';
        actionControlsEl.style.display = 'none';
        endGameControlsEl.style.display = 'none';
    }

    // 观众状态
    else if (currentPlayer.state === 'spectating') {
        readyControlsEl.style.display = 'none';
        bettingControlsEl.style.display = 'none';
        actionControlsEl.style.display = 'none';
        
        // 可以显示一个观众提示
        gameMessageEl.textContent = "您正在观战模式中观看游戏";
    }

    // 控制下注界面
    else if (gameState.game_state === 'betting' && currentPlayer.state === 'betting') {
        readyControlsEl.style.display = 'none';
        bettingControlsEl.style.display = 'block';
        actionControlsEl.style.display = 'none';
        endGameControlsEl.style.display = 'none';
    }
    // 控制游戏操作界面
    else if (gameState.game_state === 'playing' && currentPlayer.state === 'playing' && 
            gameState.player_order[gameState.current_player_index] === socket.id) {
        readyControlsEl.style.display = 'none';
        bettingControlsEl.style.display = 'none';
        actionControlsEl.style.display = 'block';
        endGameControlsEl.style.display = 'none';
        
        // 控制双倍下注按钮
        doubleDownBtn.disabled = currentPlayer.hand.length !== 2 || currentPlayer.money < currentPlayer.current_bet;
    }
    // 控制游戏结束界面
    else if (gameState.game_state === 'game_over') {
        readyControlsEl.style.display = 'none';
        bettingControlsEl.style.display = 'none';
        actionControlsEl.style.display = 'none';
        endGameControlsEl.style.display = 'block';
    }
    // 其他情况隐藏所有控制
    else {
        readyControlsEl.style.display = 'none';
        bettingControlsEl.style.display = 'none';
        actionControlsEl.style.display = 'none';
        endGameControlsEl.style.display = 'none';
    }
}

// 更新玩家状态
function updatePlayerStatus(playerId, state) {
    const playerEl = document.querySelector(`.player-item[data-player-id="${playerId}"]`);
    if (!playerEl) return;

    if (state === 'spectating') {
        statusClass = 'status-spectating';
        statusText = '观战中';
    }
    
    // 更新状态显示
    const statusEl = playerEl.querySelector('.player-status');
    if (statusEl) {
        // 移除所有状态类
        statusEl.classList.remove('status-waiting', 'status-ready', 'status-betting', 'status-playing', 'status-stand', 'status-busted', 'status-blackjack', 'status-five-dragon');
        
        // 添加新状态类
        let statusClass = 'status-waiting';
        let statusText = '等待中';
        
        if (state === 'ready') {
            statusClass = 'status-ready';
            statusText = '已准备';
        } else if (state === 'betting') {
            statusClass = 'status-betting';
            statusText = '下注中';
        } else if (state === 'playing') {
            statusClass = 'status-playing';
            statusText = '游戏中';
        } else if (state === 'stand') {
            statusClass = 'status-stand';
            statusText = '停牌';
        } else if (state === 'busted') {
            statusClass = 'status-busted';
            statusText = '爆牌';
        } else if (state === 'blackjack') {
            statusClass = 'status-blackjack';
            statusText = 'BlackJack';
        } else if (state === 'five_dragon') {
            statusClass = 'status-five-dragon';
            statusText = '五小龙';
        }
        
        statusEl.className = `player-status ${statusClass}`;
        statusEl.textContent = statusText;
    }
}

// 创建卡牌元素
function createCardElement(card) {
    const cardEl = document.createElement('div');
    cardEl.className = 'card';
    
    // 处理隐藏牌
    if (card.suit === '?' || card.value === '?') {
        cardEl.classList.add('card-hidden');
        return cardEl;
    }
    
    // 设置红黑色
    if (card.suit === '♥' || card.suit === '♦') {
        cardEl.classList.add('card-red');
    } else {
        cardEl.classList.add('card-black');
    }
    
    // 添加牌值和花色
    const valueEl = document.createElement('div');
    valueEl.className = 'card-value';
    valueEl.textContent = card.value;
    
    const suitEl = document.createElement('div');
    suitEl.className = 'card-suit';
    suitEl.textContent = card.suit;
    
    cardEl.appendChild(valueEl);
    cardEl.appendChild(suitEl);
    
    return cardEl;
}

// 显示通知
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // 2秒后移除通知
    setTimeout(() => {
        notification.classList.add('fadeout');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 500);
    }, 2000);
}

// 离开房间
function leaveRoom() {
    socket.emit('leave_room', {
        room_id: roomId
    });
    
    // 重定向到主页
    window.location.href = '/';
}

// 页面卸载前通知服务器
window.addEventListener('beforeunload', () => {
    socket.emit('leave_room', {
        room_id: roomId
    });
});

// 初始化
document.addEventListener('DOMContentLoaded', init);