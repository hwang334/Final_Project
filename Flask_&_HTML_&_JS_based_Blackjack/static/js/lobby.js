document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const playerNameInput = document.getElementById('player-name');
    const roomNameInput = document.getElementById('room-name');
    const createRoomBtn = document.getElementById('create-room-btn');
    const refreshBtn = document.getElementById('refresh-btn');
    const roomsContainer = document.getElementById('rooms-container');
    
    // Load player name from localStorage
    const savedPlayerName = localStorage.getItem('playerName');
    if (savedPlayerName) {
        playerNameInput.value = savedPlayerName;
    }
    
    // Get room list
    async function fetchRooms() {
        try {
            const response = await fetch('/api/rooms');
            const rooms = await response.json();
            
            displayRooms(rooms);
        } catch (error) {
            console.error('Failed to get room list:', error);
            roomsContainer.innerHTML = '<div class="error">Failed to get room list, please try again</div>';
        }
    }
    
    // Display room list
    function displayRooms(rooms) {
        if (rooms.length === 0) {
            roomsContainer.innerHTML = '<div class="no-rooms">No rooms available, please create a new room</div>';
            return;
        }
        
        let html = '';
        rooms.forEach(room => {
            html += `
                <div class="room-item">
                    <div class="room-info">
                        <h3>${room.room_name}</h3>
                        <p>Players: ${room.player_count}/${room.max_players}</p>
                        <p>Status: ${getGameStateText(room.game_state)}</p>
                    </div>
                    <button class="btn primary-btn join-room-btn" data-room-id="${room.room_id}">Join</button>
                </div>
            `;
        });
        
        roomsContainer.innerHTML = html;
        
        // Add join room button events
        document.querySelectorAll('.join-room-btn').forEach(button => {
            button.addEventListener('click', () => {
                const roomId = button.getAttribute('data-room-id');
                joinRoom(roomId);
            });
        });
    }
    
    // Get game state text
    function getGameStateText(state) {
        const stateMap = {
            'waiting': 'Waiting',
            'betting': 'Betting',
            'playing': 'In Progress',
            'dealer_turn': "Dealer's Turn",
            'game_over': 'Round Over'
        };
        return stateMap[state] || state;
    }
    
    // Create room
    async function createRoom() {
        const playerName = playerNameInput.value.trim();
        if (!playerName) {
            alert('Please enter your name');
            return;
        }
        
        // Save player name to localStorage
        localStorage.setItem('playerName', playerName);
        
        const roomName = roomNameInput.value.trim() || `${playerName}'s Room`;
        
        try {
            const response = await fetch('/api/create-room', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ room_name: roomName })
            });
            
            const data = await response.json();
            
            if (data.success) {
                joinRoom(data.room_id);
            } else {
                alert('Failed to create room: ' + (data.message || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error creating room:', error);
            alert('Failed to create room, please try again');
        }
    }
    
    // Join room
    function joinRoom(roomId) {
        const playerName = playerNameInput.value.trim();
        if (!playerName) {
            alert('Please enter your name');
            return;
        }
        
        // Save player name to localStorage
        localStorage.setItem('playerName', playerName);
        
        // Redirect to room page
        window.location.href = `/room/${roomId}`;
    }
    
    // Add event listeners
    createRoomBtn.addEventListener('click', createRoom);
    refreshBtn.addEventListener('click', fetchRooms);
    
    // Initially load room list
    fetchRooms();
    
    // Auto refresh room list (every 10 seconds)
    setInterval(fetchRooms, 10000);
});