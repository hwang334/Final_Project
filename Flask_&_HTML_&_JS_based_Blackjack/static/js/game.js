// DOM elements
const playerMoneyEl = document.getElementById('player-money');
const currentBetEl = document.getElementById('current-bet');
const messageEl = document.getElementById('message');
const dealerCardsEl = document.getElementById('dealer-cards');
const playerCardsEl = document.getElementById('player-cards');
const dealerScoreEl = document.getElementById('dealer-score');
const playerScoreEl = document.getElementById('player-score');
const betAmountEl = document.getElementById('bet-amount');
const placeBetBtn = document.getElementById('place-bet-btn');
const startGameBtn = document.getElementById('start-game-btn');
const hitBtn = document.getElementById('hit-btn');
const standBtn = document.getElementById('stand-btn');
const doubleDownBtn = document.getElementById('double-down-btn');
const splitBtn = document.getElementById('split-btn');
const newGameBtn = document.getElementById('new-game-btn');
const dealerDifficultyEl = document.getElementById('dealer-difficulty');
const splitControlsEl = document.getElementById('split-controls');
const secondHandEl = document.getElementById('second-hand');
const secondCardsEl = document.getElementById('second-cards');
const secondScoreEl = document.getElementById('second-score');
const splitFirstHitBtn = document.getElementById('split-first-hit-btn');
const splitFirstStandBtn = document.getElementById('split-first-stand-btn');
const splitSecondHitBtn = document.getElementById('split-second-hit-btn');
const splitSecondStandBtn = document.getElementById('split-second-stand-btn');
const showStatsBtn = document.getElementById('show-stats-btn');
const statsDetailsEl = document.getElementById('stats-details');
const totalGamesEl = document.getElementById('total-games');
const winsEl = document.getElementById('wins');
const lossesEl = document.getElementById('losses');
const winRateEl = document.getElementById('win-rate');
const blackjacksEl = document.getElementById('blackjacks');
const highestBalanceEl = document.getElementById('highest-balance');
const totalWinningsEl = document.getElementById('total-winnings');

// Game state
let gameState = {
    player_hand: [],
    dealer_hand: [],
    player_score: 0,
    dealer_score: 0,
    game_state: "betting",
    player_money: 1000,
    current_bet: 0,
    message: "Welcome to Blackjack!",
    can_split: false,
    can_double: false,
    dealer_difficulty: "medium"
};

// Game statistics
let gameStats = {
    games_played: 0,
    wins: 0,
    losses: 0,
    blackjacks: 0,
    highest_balance: 1000,
    total_winnings: 0
};

// Initialize game
async function initGame() {
    try {
        // Load game history
        await loadGameHistory();
        
        // Load game state
        const response = await fetch('/api/game-state');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Set difficulty
        if (dealerDifficultyEl) {
            dealerDifficultyEl.value = data.dealer_difficulty || "medium";
        }
        
        updateGameState(data);
        
        // Show stats button event
        if (showStatsBtn) {
            showStatsBtn.addEventListener('click', function() {
                if (statsDetailsEl.style.display === 'none') {
                    statsDetailsEl.style.display = 'block';
                    showStatsBtn.textContent = 'Hide Stats';
                } else {
                    statsDetailsEl.style.display = 'none';
                    showStatsBtn.textContent = 'Show Stats';
                }
            });
        }
    } catch (error) {
        console.error('Error initializing game:', error);
    }
}

// Load game history
async function loadGameHistory() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update statistics
        gameStats.games_played = data.games_played || 0;
        gameStats.wins = data.wins || 0;
        gameStats.losses = data.losses || 0;
        gameStats.blackjacks = data.blackjacks || 0;
        gameStats.highest_balance = data.highest_balance || 1000;
        gameStats.total_winnings = data.total_winnings || 0;
        
        // Update stats display
        updateStatsDisplay();
    } catch (error) {
        console.error('Error loading game history:', error);
    }
}

// Update stats display
function updateStatsDisplay() {
    if (totalGamesEl) totalGamesEl.textContent = gameStats.games_played;
    if (winsEl) winsEl.textContent = gameStats.wins;
    if (lossesEl) lossesEl.textContent = gameStats.losses;
    if (winRateEl) {
        const winRate = gameStats.games_played > 0 
            ? ((gameStats.wins / gameStats.games_played) * 100).toFixed(1) 
            : 0;
        winRateEl.textContent = `${winRate}%`;
    }
    if (blackjacksEl) blackjacksEl.textContent = gameStats.blackjacks;
    if (highestBalanceEl) highestBalanceEl.textContent = gameStats.highest_balance;
    if (totalWinningsEl) totalWinningsEl.textContent = gameStats.total_winnings;
}

// Update game state and UI
function updateGameState(data) {
    gameState = data;
    
    // Update basic info display
    playerMoneyEl.textContent = gameState.player_money;
    currentBetEl.textContent = gameState.current_bet;
    messageEl.textContent = gameState.message;
    
    // Update player hand
    playerCardsEl.innerHTML = '';
    gameState.player_hand.forEach(card => {
        playerCardsEl.appendChild(createCardElement(card, false));
    });
    
    // Determine if game is in a state where dealer card should be hidden
    const isPlayerActiveTurn = gameState.game_state === 'player_turn' || 
                              gameState.game_state === 'split_first_hand' || 
                              gameState.game_state === 'split_second_hand';
    
    // Calculate actual dealer total
    let actualDealerScore = 0;
    if (gameState.dealer_hand && gameState.dealer_hand.length > 0) {
        actualDealerScore = calculateHandValue(gameState.dealer_hand);
    }
    
    // Update dealer hand display
    dealerCardsEl.innerHTML = '';
    gameState.dealer_hand.forEach((card, index) => {
        // Only hide second card during player's active turn
        const hidden = index === 1 && isPlayerActiveTurn;
        dealerCardsEl.appendChild(createCardElement(card, hidden));
    });
    
    // Update player score
    playerScoreEl.textContent = `(${gameState.player_score})`;
    
    // Update dealer score display
    if (isPlayerActiveTurn) {
        // Only show first card score during player's turn
        const firstCardValue = getCardValue(gameState.dealer_hand[0]);
        dealerScoreEl.textContent = `(${firstCardValue})`;
    } else {
        // Show actual total in other states
        dealerScoreEl.textContent = `(${actualDealerScore})`;
    }
    
    // Handle split case
    if ('second_hand' in gameState) {
        // Show second hand area
        if (secondHandEl) {
            secondHandEl.style.display = 'block';
            secondCardsEl.innerHTML = '';
            gameState.second_hand.forEach(card => {
                secondCardsEl.appendChild(createCardElement(card, false));
            });
            secondScoreEl.textContent = `(${gameState.second_hand_score})`;
        }
        
        // Show/hide split controls area
        if (splitControlsEl) {
            splitControlsEl.style.display = 'block';
            
            if (gameState.game_state === 'split_first_hand') {
                document.querySelector('.first-hand-controls').style.display = 'flex';
                document.querySelector('.second-hand-controls').style.display = 'none';
            } else if (gameState.game_state === 'split_second_hand') {
                document.querySelector('.first-hand-controls').style.display = 'none';
                document.querySelector('.second-hand-controls').style.display = 'flex';
            } else {
                splitControlsEl.style.display = 'none';
            }
        }
    } else {
        // Hide second hand area
        if (secondHandEl) {
            secondHandEl.style.display = 'none';
        }
        
        // Hide split controls area
        if (splitControlsEl) {
            splitControlsEl.style.display = 'none';
        }
    }
    
    // Update button states
    updateButtons();
}

// Helper function: Calculate a hand's total points
function calculateHandValue(hand) {
    let score = 0;
    let aces = 0;
    
    hand.forEach(card => {
        if (card.value === 'A') {
            aces += 1;
            score += 11;
        } else if (card.value === 'J' || card.value === 'Q' || card.value === 'K') {
            score += 10;
        } else {
            score += parseInt(card.value);
        }
    });
    
    // Handle Ace's 1 or 11 points issue
    while (score > 21 && aces > 0) {
        score -= 10;
        aces -= 1;
    }
    
    return score;
}

// Create card element
function createCardElement(card, hidden) {
    const cardEl = document.createElement('div');
    cardEl.className = 'card';
    
    if (hidden) {
        cardEl.classList.add('card-hidden');
        return cardEl;
    }
    
    // Set red/black color
    if (card.suit === '♥' || card.suit === '♦') {
        cardEl.classList.add('card-red');
    } else {
        cardEl.classList.add('card-black');
    }
    
    // Add value and suit
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

// Get card value
function getCardValue(card) {
    if (card.value === 'A') {
        return 11;
    } else if (card.value === 'J' || card.value === 'Q' || card.value === 'K') {
        return 10;
    } else {
        return parseInt(card.value);
    }
}

// Update button states
function updateButtons() {
    // Basic buttons
    placeBetBtn.disabled = gameState.game_state !== 'betting';
    startGameBtn.disabled = gameState.game_state !== 'betting' || gameState.current_bet <= 0;
    
    // Hit and stand buttons
    const isPlayerTurn = gameState.game_state === 'player_turn';
    hitBtn.disabled = !isPlayerTurn;
    standBtn.disabled = !isPlayerTurn;
    
    // Double down and split buttons
    doubleDownBtn.disabled = !isPlayerTurn || !gameState.can_double;
    splitBtn.disabled = !isPlayerTurn || !gameState.can_split;
}

// Place bet
async function placeBet() {
    try {
        console.log("Starting bet process");
        const betAmount = parseInt(betAmountEl.value);
        console.log("Bet amount:", betAmount);
        
        if (isNaN(betAmount) || betAmount <= 0) {
            alert('Please enter a valid bet amount!');
            return;
        }
        
        if (betAmount > gameState.player_money) {
            alert('Bet amount cannot exceed your balance!');
            return;
        }
        
        // Get difficulty setting
        const difficulty = dealerDifficultyEl ? dealerDifficultyEl.value : "medium";
        
        console.log("Preparing to send bet request");
        const response = await fetch('/api/place-bet', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                amount: betAmount,
                difficulty: difficulty
            })
        });
        
        console.log("Bet request response status:", response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Bet response data:', data);
        updateGameState(data);
    } catch (error) {
        console.error('Bet error:', error);
        alert('Bet operation failed, see console for details.');
    }
}

// Start game
async function startGame() {
    try {
        console.log("Starting game");
        const response = await fetch('/api/start-game', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("Game start response:", data);
        updateGameState(data);
    } catch (error) {
        console.error('Start game error:', error);
        alert('Start game failed, see console for details.');
    }
}

// Hit
async function hit() {
    try {
        const response = await fetch('/api/hit', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        updateGameState(data);
        
        // Update stats after game ends
        if (data.game_state === 'game_over') {
            await loadGameHistory();
        }
    } catch (error) {
        console.error('Hit error:', error);
        alert('Hit operation failed, see console for details.');
    }
}

// Stand
async function stand() {
    try {
        const response = await fetch('/api/stand', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        updateGameState(data);
        
        // Update stats after game ends
        if (data.game_state === 'game_over') {
            await loadGameHistory();
        }
    } catch (error) {
        console.error('Stand error:', error);
        alert('Stand operation failed, see console for details.');
    }
}

// Double down
async function doubleDown() {
    try {
        console.log("Executing double down");
        const response = await fetch('/api/double-down', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("Double down response:", data);
        updateGameState(data);
        
        // Update stats after game ends
        if (data.game_state === 'game_over') {
            await loadGameHistory();
        }
    } catch (error) {
        console.error('Double down error:', error);
        alert('Double down operation failed, see console for details.');
    }
}

// Split
async function split() {
    try {
        console.log("Executing split");
        const response = await fetch('/api/split', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("Split response:", data);
        updateGameState(data);
    } catch (error) {
        console.error('Split error:', error);
        alert('Split operation failed, see console for details.');
    }
}

// Split first hand hit
async function splitFirstHit() {
    try {
        const response = await fetch('/api/split-first-hit', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        updateGameState(data);
    } catch (error) {
        console.error('Split first hand hit error:', error);
        alert('Operation failed, see console for details.');
    }
}

// Split first hand stand
async function splitFirstStand() {
    try {
        const response = await fetch('/api/split-first-stand', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        updateGameState(data);
    } catch (error) {
        console.error('Split first hand stand error:', error);
        alert('Operation failed, see console for details.');
    }
}

// Split second hand hit
async function splitSecondHit() {
    try {
        const response = await fetch('/api/split-second-hit', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        updateGameState(data);
        
        // Update stats after game ends
        if (data.game_state === 'game_over') {
            await loadGameHistory();
        }
    } catch (error) {
        console.error('Split second hand hit error:', error);
        alert('Operation failed, see console for details.');
    }
}

// Split second hand stand
async function splitSecondStand() {
    try {
        const response = await fetch('/api/split-second-stand', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        updateGameState(data);
        
        // Update stats after game ends
        if (data.game_state === 'game_over') {
            await loadGameHistory();
        }
    } catch (error) {
        console.error('Split second hand stand error:', error);
        alert('Operation failed, see console for details.');
    }
}

// Reset game
async function resetGame() {
    try {
        const response = await fetch('/api/reset', {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        updateGameState(data);
    } catch (error) {
        console.error('Reset game error:', error);
        alert('Reset game failed, see console for details.');
    }
}

// Event listeners
placeBetBtn.addEventListener('click', placeBet);
startGameBtn.addEventListener('click', startGame);
hitBtn.addEventListener('click', hit);
standBtn.addEventListener('click', stand);
doubleDownBtn.addEventListener('click', doubleDown);
splitBtn.addEventListener('click', split);
newGameBtn.addEventListener('click', resetGame);

// Split operation button listeners
if (splitFirstHitBtn) splitFirstHitBtn.addEventListener('click', splitFirstHit);
if (splitFirstStandBtn) splitFirstStandBtn.addEventListener('click', splitFirstStand);
if (splitSecondHitBtn) splitSecondHitBtn.addEventListener('click', splitSecondHit);
if (splitSecondStandBtn) splitSecondStandBtn.addEventListener('click', splitSecondStand);

// Difficulty change event
if (dealerDifficultyEl) {
    dealerDifficultyEl.addEventListener('change', function() {
        console.log(`Difficulty changed to: ${this.value}`);
    });
}

// Initialize game
document.addEventListener('DOMContentLoaded', initGame);

// Add a test function that can be called from console to test API connection
window.testAPI = async function() {
    try {
        const response = await fetch('/api/test');
        const data = await response.json();
        console.log("API test result:", data);
        return data;
    } catch (error) {
        console.error("API test failed:", error);
    }
};