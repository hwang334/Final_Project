# Blackjack Game

A multiplayer real-time Blackjack game implementation based on Flask and Socket.IO, supporting AI players, game records, and online gameplay.

![Blackjack Game Screenshot](screenshot_path_here)

## Table of Contents

- [Features](#features)
- [Game Rules](#game-rules)
- [Technical Architecture](#technical-architecture)
- [Project Structure](#project-structure)
- [Component Details](#component-details)
- [Installation & Configuration](#installation--configuration)
- [Development Guide](#development-guide)
- [Gameplay](#gameplay)
- [AI Player System](#ai-player-system)
- [Network Implementation](#network-implementation)
- [Troubleshooting](#troubleshooting)
- [Known Issues](#known-issues)
- [Future Plans](#future-plans)
- [License](#license)

## Features

- **Multiplayer Real-time Gameplay**
  - Supports up to 5 players in a single room
  - Real-time communication based on Socket.IO
  - Player order management for orderly gameplay

- **AI Players**
  - 4 different difficulty levels of AI opponents
  - Probability and strategy-based AI decision system
  - Automatic AI actions simulating human player behavior

- **Complete Game Rules**
  - Standard Blackjack rules implementation
  - Blackjack special payout (1.5x)
  - Five-card Charlie rule (5 cards under 21 points gets 2x payout)
  - Double Down feature

- **Game Record System**
  - Detailed records of each game result
  - Player statistics (win rate, profit/loss, blackjack count, etc.)
  - JSON file-based persistent storage

- **Online Gameplay**
  - Internal network penetration based on ngrok
  - Automatic generation of public network links for easy sharing
  - Support for gameplay across different network environments

- **User Experience**
  - Responsive design for desktop and mobile devices
  - Reconnection support, remembering player state
  - Player session management, allowing rejoining games

- **System Stability**
  - Game state detection, automatic recovery of stuck games
  - AI action timeout handling, ensuring smooth gameplay
  - Error handling and logging

## Game Rules

### Basic Rules

- **Objective**: Get your hand as close to 21 points as possible without exceeding 21
- **Card Values**:
  - Number cards (2-10): Face value
  - Face cards (J, Q, K): 10 points
  - Ace: 1 or 11 points (automatically optimized)
- **Game Flow**:
  1. Player betting phase
  2. Deal (two cards to each player, one face-up and one face-down to the dealer)
  3. Player turns (hit or stand)
  4. Dealer turn (automatic actions according to rules)
  5. Settlement
- **Bust**: Hand value exceeds 21, automatic loss
- **Dealer Rules**: Dealer must hit until hand value is 17 or higher

### Special Rules

- **Blackjack**
  - Definition: First two cards are Ace + 10/J/Q/K, totaling 21 points
  - Payout: Wins 1.5x bet
  - Priority: Tie if both player and dealer have Blackjack

- **Double Down**
  - Condition: Only available with the first two cards
  - Action: Double the bet and receive exactly one more card
  - Requirement: Player must have sufficient funds

- **Five-card Charlie**
  - Definition: Having 5 cards without exceeding 21 points
  - Payout: Wins 2x bet
  - Priority: Higher than regular win, lower than Blackjack

### Settlement Rules

- **Player Wins**:
  - Player has not busted and has higher points than dealer: Wins 1x bet
  - Player has not busted and dealer busts: Wins 1x bet
  - Player gets Blackjack: Wins 1.5x bet
  - Player gets Five-card Charlie: Wins 2x bet

- **Tie**:
  - Player and dealer have the same points: Bet returned
  - Both player and dealer have Blackjack: Bet returned

- **Player Loses**:
  - Player busts: Loses bet
  - Player has lower points than dealer and dealer hasn't busted: Loses bet

## Technical Architecture

### Backend Technologies

- **Python Flask**: Web application framework for handling HTTP requests and responses
- **Flask-SocketIO**: Implementation of WebSocket communication for real-time game updates
- **Thread Management**: Scheduled tasks and asynchronous processing to monitor game states
- **Object-Oriented Design**: Classes and objects to represent game entities (cards, players, rooms)
- **JSON Persistence**: Saving game records and player data
- **ngrok Integration**: Providing external network access support

### Frontend Technologies

- **Socket.IO Client**: Real-time communication
- **Vue.js**: Reactive frontend framework
- **HTML5/CSS3**: Page structure and styling
- **JavaScript**: Client-side logic
- **LocalStorage**: Storing player information and session data
- **Responsive Design**: Adapting to different device screen sizes

### System Architecture

- **Client-Server Model**: Real-time communication based on WebSocket
- **Event-Driven Architecture**: Using events to handle game flow
- **Scheduled Task System**: Monitoring and handling game states
- **Session Management**: Handling player connections and reconnections
- **Configuration System**: Managing service parameters through configuration files

## Project Structure

```
blackjack/
│
├── config.py                  # Global configuration file
├── main.py                    # Entry point, initializes and starts the application
│
├── app/                       # Flask application core
│   ├── __init__.py            # Initializes Flask app and SocketIO, sets up scheduled tasks
│   ├── routes.py              # Handles HTTP routes and API requests
│   └── events.py              # Handles Socket.IO events and real-time communication
│
├── models/                    # Game models and data structures
│   ├── __init__.py            # Initializes model module, creates global objects
│   ├── card.py                # Card class, represents playing cards
│   ├── player.py              # Player class, manages player state and behavior
│   ├── game_room.py           # Game room class, handles game logic and rules
│   ├── game_record.py         # Game record management, saves and loads game history
│   ├── ai_player.py           # AI player management, implements AI decision logic
│   └── game_observer.py       # Game state observer, monitors and handles abnormal states
│
├── utils/                     # Utility tools and helper functions
│   ├── __init__.py            # Initializes utility module
│   └── ngrok_manager.py       # Manages ngrok tunnels, provides external network access
│
├── static/                    # Static resource files
│   ├── css/
│   │   └── style.css          # Global stylesheet
│   ├── js/
│   │   ├── lobby.js           # Game lobby client script
│   │   ├── room.js            # Game room client script
│   │   └── game.js            # Game logic client script
│   └── img/                   # Image resources directory
│
├── templates/                 # HTML templates
│   ├── index.html             # Game lobby page
│   ├── room.html              # Game room page
│   └── 404.html               # 404 error page
│
└── game_records/              # Game records storage directory (auto-created)
```

## Component Details

### Backend Components

#### `main.py`
Entry point, responsible for initializing and starting the application. Creates the game records directory, initializes the Flask application, and starts the web server.

#### `config.py`
Configuration file containing all application settings:
- Flask application configuration (SECRET_KEY, WTF_CSRF_ENABLED, SESSION_TYPE)
- ngrok configuration (USE_NGROK, NGROK_AUTH_TOKEN, PORT)
- Game parameters (maximum number of players)

#### `app/__init__.py`
Initializes the Flask application and SocketIO, sets up middleware and scheduled tasks:
- Creates SocketIO instance
- Sets Flask configuration
- Registers routes and event handlers
- Creates scheduled task to monitor AI players
- Handles stuck game states

#### `app/routes.py`
Handles HTTP routes and API requests:
- Home and room page routes
- Create room API
- Get room list API
- Add/remove AI player API
- Game records and statistics API

#### `app/events.py`
Handles Socket.IO events and real-time communication:
- Connect and disconnect events
- Join/leave room events
- Player ready events
- Betting events
- Game operation events (hit/stand/double down)
- Game state update events
- AI player action handling

#### `models/card.py`
Card class representing a playing card:
- Suit and value attributes
- Serialization method (to_dict)

#### `models/player.py`
Player class managing player state and behavior:
- Player attributes (ID, name, hand, score, money, bet, etc.)
- Player states (waiting, ready, betting, playing, stand, busted, etc.)
- AI player attributes (is_ai, ai_difficulty)
- Initialization and reset methods

#### `models/game_room.py`
Game room class handling game logic and rules:
- Room attributes (ID, name, player list, dealer, deck, etc.)
- Game states (waiting, betting, playing, dealer_turn, game_over)
- Player management (add/remove player)
- Deck management (shuffle, deal)
- Game flow control (start betting, start game, player actions, dealer turn)
- Game settlement logic
- Session state management

#### `models/game_record.py`
Game record management for saving and loading game history:
- JSON-based persistence
- Game record saving and loading
- Player statistics calculation
- Record formatting and management

#### `models/ai_player.py`
AI player management implementing AI decision logic:
- Different difficulty AI strategies
- AI betting decisions
- AI game decisions (hit/stand/double down)
- AI action handling and timeout handling
- Forced action handling (for stuck AI)

#### `models/game_observer.py`
Game state observer, monitoring and handling abnormal states:
- Monitoring game room states
- Detecting stuck games
- Forcibly resolving stuck states
- Recovering abnormal game states

#### `utils/ngrok_manager.py`
Managing ngrok tunnels, providing external network access:
- Setting up and starting ngrok tunnels
- Getting and displaying public URLs
- Handling tunnel connection errors
- Providing local network IP as backup

### Frontend Components

#### `templates/index.html`
Game lobby page:
- Create room form
- Room list display
- ngrok link sharing
- Game rules explanation

#### `templates/room.html`
Game room page, implementing a responsive interface using Vue.js:
- Room status display
- Player list and status
- Dealer and player card display
- Game controls (ready, bet, game operations)
- AI player controls
- Game record display
- Player statistics

#### `templates/404.html`
Custom 404 error page.

#### `static/js/lobby.js`
Game lobby client script:
- Getting and displaying room list
- Creating new rooms
- Joining existing rooms
- Player name management
- Automatic room list refresh

#### `static/js/room.js`
Game room client script handling Socket.IO communication:
- Establishing Socket.IO connection
- Joining/leaving rooms
- Player ready and game state updates
- Displaying cards and game information
- Handling player actions and results
- Displaying notifications and error messages
- Disconnection reconnection handling

#### `static/js/game.js`
Game logic client script (single player version):
- Game state management
- Card display and calculation
- Game flow control
- Statistics display
- API testing functionality

#### `static/css/style.css`
Global stylesheet defining game interface styles:
- Basic styles and layout
- Button and form styles
- Card styles and animations
- Player and room styles
- Game control interface
- Responsive design rules

## Installation & Configuration

### Requirements

- **Python**: 3.7 or higher
- **Flask**: 2.0.0 or higher
- **Flask-SocketIO**: 5.0.0 or higher
- **Python Dependencies**:
  - pyngrok (for external network access)
  - eventlet or gevent (SocketIO dependency)
  - python-socketio
  - python-engineio

### Detailed Installation Steps

1. **Clone the Repository**:
```bash
git clone https://github.com/your-username/blackjack.git
cd blackjack
```

2. **Create a Virtual Environment** (recommended):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure ngrok** (optional, for external network access):
   - Register for an [ngrok](https://ngrok.com/) account
   - Get an authentication token
   - Set `NGROK_AUTH_TOKEN` in `config.py`

5. **Custom Configuration**:
   Edit the `config.py` file to adjust:
   ```python
   # Port setting
   PORT = 5001  # Change to desired port
   
   # ngrok configuration
   USE_NGROK = True  # Set to False to disable ngrok
   NGROK_AUTH_TOKEN = "your_ngrok_auth_token"
   
   # Game configuration
   MAX_PLAYERS_PER_ROOM = 5  # Maximum players per room
   ```

6. **Start the Game Server**:
```bash
python main.py
```

7. **Access the Game**:
   - Local access: http://localhost:5001 (or your configured port)
   - If ngrok is enabled, the terminal will display the public access link

### Docker Deployment (Optional)

1. **Build Docker Image**:
```bash
docker build -t blackjack-game .
```

2. **Run Container**:
```bash
docker run -p 5001:5001 blackjack-game
```

## Development Guide

### Project Architecture

This project uses an MVC architecture design:
- **Model**: Classes in the `models/` directory represent game entities and business logic
- **View**: `templates/` and `static/` directories provide the user interface
- **Controller**: `app/routes.py` and `app/events.py` handle requests and events

### Coding Style

- Follow PEP 8 Python coding standards
- Use type annotations to enhance code readability
- Write detailed docstrings
- Use meaningful variable and function names

### Adding New Features

1. **Adding New Game Rules**:
   - Modify the `determine_winners` method in `models/game_room.py`
   - Update the frontend UI to display new rules

2. **Enhancing AI Behavior**:
   - Modify the decision logic in `models/ai_player.py`
   - Add new AI difficulty levels or strategies

3. **Adding New API Endpoints**:
   - Add new routes in `app/routes.py`
   - Update frontend code to use the new API

4. **Improving User Interface**:
   - Modify HTML templates in `templates/`
   - Update styles in `static/css/style.css`

### Common Development Tasks

- **Modifying Betting Limits**:
  Modify betting amount logic in `models/ai_player.py` and `room.html`

- **Adjusting Game Rules**:
  Modify methods like `player_hit`, `player_stand`, `dealer_turn` in `models/game_room.py`

- **Adding New Player Operations**:
  1. Add new methods in `models/game_room.py`
  2. Add new event handlers in `app/events.py`
  3. Add corresponding buttons and event listeners in the frontend

- **Customizing Card Styles**:
  Modify `.card` related styles in `static/css/style.css`

## Gameplay

### Basic Operation Flow

1. **Enter Game Lobby**:
   - Enter your name
   - Create a new room or join an existing one

2. **In the Game Room**:
   - Click the "Ready" button to prepare for the game
   - Add AI players to increase the number of players
   - View game rules and player information

3. **Game Start**:
   - When all players are ready, enter the betting phase
   - Set the bet amount and click the "Bet" button
   - After all players bet, the game automatically deals cards

4. **Player Actions**:
   - Choose "Hit", "Stand", or "Double Down" based on your hand
   - Take turns acting, with the current player highlighted
   - If a player's hand exceeds 21 points, they automatically bust and lose

5. **Dealer Action**:
   - After all players complete their actions, the dealer automatically acts
   - The dealer hits according to rules until reaching 17 points or higher

6. **Settlement Phase**:
   - Displays final results and profit/loss for all players
   - Updates player funds and statistics
   - Click "Next Round" to start a new round

### Special Operations

- **Double Down**: After receiving the first two cards, double your bet and receive exactly one more card
- **Spectator Mode**: Players with 0 funds enter spectator status and can watch other players
- **AI Player Management**: Add or remove AI players of different difficulties
- **View Game Records**: Check game history records at the bottom of the room page
- **View Personal Statistics**: Display win rate, profit/loss, and other personal statistics

## AI Player System

### AI Difficulty Levels

1. **Easy**:
   - Uses the most basic strategy: stands on 17+ points, otherwise hits
   - Always places minimum bets
   - Does not consider dealer's upcard
   - Does not use double down

2. **Medium**:
   - Basic strategy: considers dealer's upcard
   - Randomly places small to medium bets
   - Simple risk assessment
   - Occasionally uses double down

3. **Hard**:
   - Uses a more refined basic strategy
   - Adjusts betting based on current funds
   - Considers dealer's upcard and current points
   - Uses double down when conditions are appropriate

4. **Expert**:
   - Uses complete basic strategy chart
   - Complex betting strategy based on fund percentage
   - Precise risk and return calculations
   - Optimized use of double down

### AI Decision Logic

AI player decision logic is implemented in `models/ai_player.py`:

1. **Waiting Decision (ai_waiting_decision)**:
   - AI always gets ready after a random time delay
   - Checks if all players are ready, if so starts the game

2. **Betting Decision (ai_betting_decision)**:
   - Chooses bet amount based on difficulty
   - Considers current financial situation
   - Adds random delay to simulate thinking process

3. **Game Decision (ai_playing_decision)**:
   - Analyzes current hand and dealer's upcard
   - Chooses different strategies based on difficulty
   - Executes hit, stand, or double down operations
   - Adds random delay to simulate thinking process

4. **Handling Stuck AI (force_ai_action)**:
   - Detects if AI action is stuck
   - Forces appropriate operation
   - Ensures game flow is not blocked

### AI Strategy Implementation

Here are some specific AI strategies implemented:

```python
# Expert level AI decision logic example
if player.ai_difficulty == "expert":
    # Basic strategy table implementation
    if score <= 11:
        decision = "hit"  # Always hit on 11 or less
    elif score == 12:
        # On 12, hit if dealer shows 2-3 or 7+, otherwise stand
        if dealer_visible_value in [2, 3] or dealer_visible_value >= 7:
            decision = "hit"
        else:
            decision = "stand"
    elif 13 <= score <= 16:
        # On 13-16, hit if dealer shows 7+, otherwise stand
        if dealer_visible_value >= 7:
            decision = "hit"
        else:
            decision = "stand"
    # Always stand on 17+
```

## Network Implementation

### Socket.IO Communication Architecture

This project uses Socket.IO to implement real-time communication, including:

1. **Server-side Socket.IO**:
   - Initialized in `app/__init__.py`
   - Event handlers registered in `app/events.py`

2. **Client-side Socket.IO**:
   - Implemented in `room.html` and `room.js`
   - Handles real-time game state updates and player operations

### Event Types

Main Socket.IO events used in the game:

1. **Connection Events**:
   - `connect`: Client connects to server
   - `disconnect`: Client disconnects

2. **Room Events**:
   - `join_room`: Player joins room
   - `leave_room`: Player leaves room
   - `player_joined`: New player join notification
   - `player_left`: Player leave notification

3. **Game State Events**:
   - `room_data`: Complete room data
   - `game_update`: Game state update
   - `player_status_update`: Player status update

4. **Player Operation Events**:
   - `player_ready`: Player ready
   - `place_bet`: Player bet
   - `hit`: Player hit
   - `stand`: Player stand
   - `double_down`: Player double down
   - `next_round`: Start next round

### ngrok External Network Connection

The game uses ngrok to provide external network connection functionality:

1. **ngrok Configuration**:
   - Set `USE_NGROK` and `NGROK_AUTH_TOKEN` in `config.py`
   - Manage ngrok tunnels via `utils/ngrok_manager.py`

2. **Tunnel Creation Process**:
   - Check if there are existing tunnels
   - Create new tunnel using specified port
   - Get and display public URL

3. **Public URL Sharing**:
   - Display public URL on homepage
   - Provide copy button for easy sharing with friends

4. **Notes**:
   - Free version of ngrok has connection count and bandwidth limitations
   - Tunnel URL changes each time the server restarts
   - Using paid version provides fixed domain and higher connection limits
   - If connection issues occur, try using local network direct connection

### Disconnection Reconnection Mechanism

The game implements a comprehensive disconnection reconnection mechanism:

1. **Session Management**:
   - Use `localStorage` to store session ID
   - Save session to player ID mapping in `player_sessions` dictionary

2. **Reconnection Process**:
   - Client tries to reconnect after disconnection
   - Uses stored session ID to restore player identity
   - Updates player references in the room
   - Synchronizes game state

3. **State Recovery**:
   - Rejoins the same room
   - Restores player hand, funds, and state
   - Continues previous game process

```javascript
// Frontend reconnection implementation example
socket.on('reconnect', (attemptNumber) => {
    console.log('Reconnection successful, attempt number:', attemptNumber);
    
    // Rejoin room
    socket.emit('join_room', {
        room_id: roomId,
        player_name: playerName,
        session_id: localStorage.getItem('session_id')
    });
});
```

## Troubleshooting

### Common Issues

1. **Game Freezes**
   - **Cause**: AI player action stuck or state transition exception
   - **Solution**: 
     - Wait for automatic repair (scheduled tasks will detect and fix)
     - Refresh page to reconnect
     - Restart server

2. **AI Players Not Acting**
   - **Cause**: AI decision logic error or state mismatch
   - **Solution**:
     - Check console output for errors
     - Add or remove AI players to trigger state update
     - Ensure game state is correct (check `game_state`)

3. **Incorrect Profit/Loss in Game Records**
   - **Cause**: Settlement calculation logic error
   - **Solution**:
     - Verify profit/loss calculation logic in `game_record.py`
     - Recalculate difference between player initial and final funds

4. **Network Connection Issues**
   - **Cause**: ngrok tunnel failure or connection problems
   - **Solution**:
     - Check ngrok status and authentication token
     - Use local network connection instead
     - Restart server and ngrok tunnel

5. **Player Fails to Join Room**
   - **Cause**: Room is full or doesn't exist
   - **Solution**:
     - Verify room ID is correct
     - Check if room is full (reached maximum player count)
     - Create new room to try

6. **Cannot Continue After Zero Funds**
   - **Cause**: Logic error in handling zero-fund players
   - **Solution**:
     - Ensure setting to spectator state rather than removing player
     - Check zero-fund player handling in `game_room.py`

### Debugging Guide

1. **Console Logs**
   - Server console outputs detailed game state and error information
   - Frontend console shows client events and errors

2. **API Testing**
   - Use browser console to call test functions:
   ```javascript
   window.testAPI()
   ```

3. **Manually Trigger Events**
   - Use console to manually trigger Socket.IO events:
   ```javascript
   socket.emit('player_ready', { room_id: roomId })
   ```

4. **Modify Game State**
   - In development mode, directly modify DOM elements to adjust interface
   - Modify session data in localStorage using browser plugins

## Known Issues

1. **All-in Funds Handling**
   - When a player bets all funds and loses, they should be set to spectator state rather than removed
   - Need to fix related logic in `game_room.py`

2. **AI Action Stuck**
   - AI players may get stuck in certain situations
   - Scheduled task system should forcibly resolve this issue
   - Ensure `force_ai_action` function is correctly implemented

3. **Profit/Loss Calculation in Game Records**
   - When dealer busts and player wins, profit/loss record may show negative
   - Blackjack profit/loss calculation may be incorrect
   - Need to improve calculation logic in `game_record.py`

4. **Socket.IO Request Context Issue**
   - Using `emit` function in background threads may cause errors
   - Should use `socketio.emit` directly instead of relying on request context

5. **Race Condition with Multiple Players Acting Simultaneously**
   - When multiple players act in quick succession, may cause state errors
   - Need to improve state management and event handling logic

## Future Plans

### Game Feature Enhancements

1. **New Game Rules**
   - Implement split feature
   - Add insurance option
   - Support surrender option

2. **Player System**
   - Player accounts and login system
   - Leaderboard functionality
   - Player achievement system

3. **Game Experience**
   - Card animation effects
   - Sound effects and background music
   - Customizable interface themes

### Technical Improvements

1. **Data Storage**
   - Use database instead of file storage
   - Support player accounts and point system
   - Game data analysis and reporting

2. **Server Architecture**
   - Optimize multi-room support
   - Horizontal scaling to support more players
   - Deploy to cloud service platforms

3. **Security**
   - Add anti-cheating mechanisms
   - Enhance session security
   - Input validation and security filtering

### Implementation Roadmap

1. **Short-term Plans**
   - Fix known issues and bugs
   - Improve AI player behavior
   - Optimize mobile experience

2. **Medium-term Plans**
   - Add split and insurance features
   - Implement more statistics and history records
   - Add chat functionality

3. **Long-term Plans**
   - Player accounts and point system
   - Implement multiple card game variants
   - Add tournament mode

## Contribution Guidelines

Contributions to this project are welcome! Please follow these steps:

1. **Fork the project repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**:
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **Push to the branch**:
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Submit a Pull Request**

### Contribution Standards

- Follow existing code style and naming conventions
- Add detailed comments and documentation
- Ensure tests pass and no new issues are introduced
- Update README.md to reflect your changes


## Acknowledgements

- Thanks to all contributors for their hard work and support
- Flask and Socket.IO communities for excellent frameworks
- Various open source libraries and tools making this project possible
- Reference card game designs and rules

