"""
AI Player Module: Provides different difficulty levels of AI players
"""
import random
import time
from app import socketio
from models.player import Player

class AIPlayer:
    """AI Player Management Class"""
    
    # Define difficulty levels
    DIFFICULTY_LEVELS = ["easy", "medium", "hard", "expert"]
    
    # AI player name prefixes
    AI_NAME_PREFIXES = {
        "easy": "Beginner",
        "medium": "Average Player",
        "hard": "Expert",
        "expert": "Master"
    }
    
    # AI player name pool
    AI_NAMES = [
        "Alex", "Emma", "Jack", "Olivia", "James",
        "Alpha", "Beta", "Gamma", "Delta", "Epsilon",
        "Orange", "Lemon", "Apple", "Banana", "Grape",
        "Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Hangzhou"
    ]
    
    def __init__(self):
        """Initialize AI player manager"""
        # Track all AI players
        self.ai_players = {}
    
    def generate_ai_name(self, difficulty):
        """
        Generate AI player name
        
        Args:
            difficulty (str): Difficulty level
            
        Returns:
            str: AI player name
        """
        prefix = self.AI_NAME_PREFIXES.get(difficulty, "Player")
        name = random.choice(self.AI_NAMES)
        return f"{prefix}-{name}"
    
    def create_ai_player(self, player_id, difficulty="medium"):
        """
        Create AI player
        
        Args:
            player_id (str): Player ID
            difficulty (str): Difficulty level
            
        Returns:
            Player: AI player object
        """
        # Validate difficulty level
        if difficulty not in self.DIFFICULTY_LEVELS:
            difficulty = "medium"
        
        # Generate AI player name
        name = self.generate_ai_name(difficulty)
        
        # Create player object
        ai_player = Player(player_id, name, is_ai=True, ai_difficulty=difficulty)
        
        # Save to AI player list
        self.ai_players[player_id] = ai_player
        
        return ai_player
    
    def remove_ai_player(self, player_id):
        """
        Remove AI player
        
        Args:
            player_id (str): Player ID
        """
        if player_id in self.ai_players:
            del self.ai_players[player_id]
    
    def ai_waiting_decision(self, game_room, player):
        """
        AI player decision in waiting state
        
        Args:
            game_room (GameRoom): Game room object
            player (Player): AI player object
        """
        if player.state != "waiting" or game_room.game_state != "waiting":
            return
            
        # Add random delay to simulate thinking
        time.sleep(random.uniform(1.0, 3.0))
        
        # AI players always get ready
        player.state = "ready"
        
        # Broadcast player ready status
        socketio.emit('player_status_update', {
            "player_id": player.player_id,
            "player_state": player.state
        }, room=game_room.room_id)
        
        # Check if all players with funds are ready
        active_players = [p for p in game_room.players.values() if p.money > 0]
        all_ready = active_players and all(p.state == "ready" for p in active_players)
        
        if all_ready:  # Allow single player game
            if game_room.start_betting():  # Only broadcast game update if start_betting is successful
                socketio.emit('game_update', game_room.to_dict(), room=game_room.room_id)
    
    def ai_betting_decision(self, game_room, player):
        """
        AI player betting decision
        
        Args:
            game_room (GameRoom): Game room object
            player (Player): AI player object
        """
        if player.state != "betting":
            print(f"AI player {player.name} state is not 'betting', current state: {player.state}")
            return False
        
        print(f"AI player {player.name} starts betting...")
            
        # Add random delay to simulate thinking
        time.sleep(random.uniform(0.5, 2.0))
        
        # Determine bet amount based on difficulty
        bet_amount = 0
        
        if player.ai_difficulty == "easy":
            # Easy AI always bets minimum
            bet_amount = 100
        elif player.ai_difficulty == "medium":
            # Medium AI randomly bets small to medium
            bet_amount = random.randint(100, min(300, player.money))
        elif player.ai_difficulty == "hard":
            # Hard AI adjusts bet based on current funds
            bet_amount = random.randint(100, min(500, int(player.money * 0.2)))
        elif player.ai_difficulty == "expert":
            # Expert AI uses more complex betting strategy
            base_bet = int(player.money * 0.1)
            bet_amount = random.randint(max(base_bet, 100), min(600, int(player.money * 0.3)))
        
        # Ensure bet amount doesn't exceed funds
        bet_amount = min(bet_amount, player.money)
        bet_amount = max(bet_amount, 100)  # Minimum bet is 100
        
        print(f"AI player {player.name} bet amount: {bet_amount}")
        
        # Execute bet
        if bet_amount > 0:
            result = game_room.place_bet(player.player_id, bet_amount)
            print(f"AI bet result: {result}")
            
            # Directly broadcast update
            socketio.emit('game_update', game_room.to_dict(), room=game_room.room_id)
            
            return result
        
        return False
    
    def ai_make_decision(self, game_room, player_id):
        """
        AI player makes decision
        
        Args:
            game_room (GameRoom): Game room object
            player_id (str): AI player ID
        """
        # Get AI player
        if player_id not in game_room.players:
            return
            
        player = game_room.players[player_id]
        if not player.is_ai:
            return
            
        # Make different decisions based on game state
        if game_room.game_state == "betting":
            # Betting decision
            self.ai_betting_decision(game_room, player)
        elif game_room.game_state == "playing":
            # Game decision (hit/stand)
            self.ai_playing_decision(game_room, player)
    
    def ai_playing_decision(self, game_room, player):
        """
        AI player game decision
        
        Args:
            game_room (GameRoom): Game room object
            player (Player): AI player object
        """
        # Enhanced state checking and logging
        print(f"AI decision function - AI: {player.name}, state: {player.state}, game state: {game_room.game_state}")
        
        # Only keep state check, ensure player state is playing
        if player.state != "playing":
            print(f"AI player {player.name} state is not 'playing', current state: {player.state}")
            return False
            
        # Check if it's the current player's turn
        if game_room.current_player_index >= len(game_room.player_order):
            print(f"Index out of bounds: {game_room.current_player_index} / {len(game_room.player_order)}")
            return False
            
        current_player_id = game_room.player_order[game_room.current_player_index]
        if player.player_id != current_player_id:
            print(f"Not AI player {player.name}'s turn, current should be: {current_player_id}")
            return False
        
        print(f"===== AI player {player.name} starts acting, difficulty: {player.ai_difficulty} =====")
                
        # Add random delay to simulate thinking
        time.sleep(random.uniform(1.0, 3.0))
        
        # Get current hand score
        score = player.score
        
        # Get dealer's visible card score
        dealer_visible_card = game_room.dealer.hand[0]
        dealer_visible_value = self.get_card_value(dealer_visible_card)
        
        print(f"AI {player.name} current points: {score}, dealer's visible card points: {dealer_visible_value}")
        
        # Make decision based on difficulty
        decision = "stand"  # Default is stand
        
        if player.ai_difficulty == "easy":
            # Easy AI uses fixed rules
            if score < 17:
                decision = "hit"  # Hit below 17
        
        elif player.ai_difficulty == "medium":
            # Medium AI uses basic strategy with some randomness
            if score < 12:
                decision = "hit"  # Always hit below 12
            elif score < 17:
                # 12-16 points, look at dealer's card
                if dealer_visible_value >= 7:
                    decision = "hit"  # Hit when dealer has high card
                else:
                    # Add some randomness
                    decision = random.choices(["hit", "stand"], weights=[0.3, 0.7])[0]
                    
        elif player.ai_difficulty == "hard":
            # Hard AI uses more complete basic strategy
            if score < 12:
                decision = "hit"  # Always hit below 12
            elif score < 17:
                # 12-16 points, based on dealer's card
                if dealer_visible_value >= 7:
                    decision = "hit"
                else:
                    decision = "stand"
            # Always stand on 17 or higher
        
        elif player.ai_difficulty == "expert":
            # Expert AI uses complete basic strategy
            if score <= 11:
                decision = "hit"  # Always hit on 11 or lower
            elif score == 12:
                # On 12, hit if dealer has 2-3 or 7+, otherwise stand
                if dealer_visible_value in [2, 3] or dealer_visible_value >= 7:
                    decision = "hit"
                else:
                    decision = "stand"
            elif 13 <= score <= 16:
                # On 13-16, hit if dealer has 7+, otherwise stand
                if dealer_visible_value >= 7:
                    decision = "hit"
                else:
                    decision = "stand"
            # Always stand on 17 or higher
        
        # Check if can double down (only expert and hard AI consider this)
        if player.ai_difficulty in ["expert", "hard"] and len(player.hand) == 2 and player.money >= player.current_bet:
            # Consider double down on 9-11
            if score in [9, 10, 11]:
                double_down_chance = 0.8 if player.ai_difficulty == "expert" else 0.5
                if random.random() < double_down_chance:
                    decision = "double"
        
        print(f"AI {player.name} decides: {decision}")
        
        # Execute decision and return result
        result = False
        if decision == "hit":
            print(f"AI {player.name} hits")
            result = game_room.player_hit(player.player_id)
            if result:
                socketio.emit('game_update', game_room.to_dict(), room=game_room.room_id)
        elif decision == "stand":
            print(f"AI {player.name} stands")
            result = game_room.player_stand(player.player_id)
            if result:
                socketio.emit('game_update', game_room.to_dict(), room=game_room.room_id)
        elif decision == "double" and len(player.hand) == 2:
            print(f"AI {player.name} doubles down")
            result = game_room.player_double_down(player.player_id)
            if result:
                socketio.emit('game_update', game_room.to_dict(), room=game_room.room_id)
        
        print(f"AI {player.name} action result: {result}")
        return result
    
    def get_card_value(self, card):
        """
        Get card value
        
        Args:
            card (Card): Card object
            
        Returns:
            int: Card value
        """
        if card.value == 'A':
            return 11
        elif card.value in ['J', 'Q', 'K']:
            return 10
        else:
            return int(card.value)
    
    def handle_ai_turns(self, game_room):
        """
        Handle AI player turns
        
        Args:
            game_room (GameRoom): Game room object
        """
        print(f"========== Processing AI player turns ==========")
        print(f"Room: {game_room.room_id}, state: {game_room.game_state}")
        
        # Find all AI players
        ai_players = [player_id for player_id, player in game_room.players.items() if player.is_ai]
        print(f"Number of AI players in the room: {len(ai_players)}")
        
        # Handle waiting state - let AI automatically get ready
        if game_room.game_state == "waiting":
            print("Game is in waiting state, letting AI automatically get ready")
            for player_id in ai_players:
                player = game_room.players[player_id]
                print(f"AI player {player.name} state: {player.state}")
                if player.state == "waiting" and player.money > 0:
                    self.ai_waiting_decision(game_room, player)
        
        # Handle betting phase
        elif game_room.game_state == "betting":
            print("Game is in betting phase, letting AI automatically bet")
            for player_id in ai_players:
                player = game_room.players[player_id]
                print(f"AI player {player.name} state: {player.state}")
                if player.state == "betting":
                    self.ai_betting_decision(game_room, player)
        
        # Handle playing phase
        elif game_room.game_state == "playing":
            print("Game is in playing state")
            # Check current player
            if game_room.current_player_index < len(game_room.player_order):
                current_player_id = game_room.player_order[game_room.current_player_index]
                print(f"Current player ID: {current_player_id}")
                
                # Check if current player is AI
                if current_player_id in ai_players:
                    current_player = game_room.players[current_player_id]
                    print(f"Current player is AI: {current_player.name}, state: {current_player.state}")
                    
                    # Directly call AI decision method
                    if current_player.state == "playing":
                        print(f"AI player {current_player.name} is about to act...")
                        self.ai_playing_decision(game_room, current_player)
                    else:
                        print(f"AI player {current_player.name} state is not 'playing', cannot act")
                else:
                    print(f"Current player is not AI")
            else:
                print(f"current_player_index out of range: {game_room.current_player_index}, player_order length: {len(game_room.player_order)}")
        
        print(f"========== AI player turn processing complete ==========")

    def force_ai_action(self, game_room):
        """
        Force AI player action (for handling stuck situations)
        
        Args:
            game_room (GameRoom): Game room object
        
        Returns:
            bool: Whether action was successfully executed
        """
        print("====== Starting forced AI action ======")
        
        # Check if there are AI players who need to bet
        if game_room.game_state == "betting":
            ai_players_betting = [p for p_id, p in game_room.players.items() 
                                if p.is_ai and p.state == "betting"]
            
            if ai_players_betting:
                print(f"Forcing: {len(ai_players_betting)} AI players need to bet")
                for player in ai_players_betting:
                    print(f"Forcing AI {player.name} to bet")
                    
                    # Simple betting logic - bet minimum
                    bet_amount = min(100, player.money)
                    
                    # Directly modify game state
                    player.money -= bet_amount
                    player.current_bet = bet_amount
                    player.original_bet = bet_amount
                    player.state = "ready"
                    
                    print(f"Forced AI {player.name} betting complete: {bet_amount}")
                
                # Check if all players have bet
                active_players = [p for p in game_room.players.values() if p.money > 0 and p.state != "spectating"]
                betting_players = [p for p in active_players if p.state == "betting"]
                
                if not betting_players and active_players:
                    print("All AI players have been forced to bet, trying to start the game")
                    game_room.start_game()
                
                socketio.emit('game_update', game_room.to_dict(), room=game_room.room_id)
                return True
                
        # Check if there are AI players who need to act
        elif game_room.game_state == "playing":
            if game_room.current_player_index < len(game_room.player_order):
                current_player_id = game_room.player_order[game_room.current_player_index]
                current_player = game_room.players.get(current_player_id)
                
                if current_player and current_player.is_ai and current_player.state == "playing":
                    print(f"Forcing: AI {current_player.name} needs to act")
                    
                    # Simple action - just stand
                    current_player.state = "stand"
                    
                    # Move to next player
                    game_room.current_player_index = (game_room.current_player_index + 1) % len(game_room.player_order)
                    
                    # Ensure setting next player or entering dealer turn
                    if game_room.current_player_index == 0 or all(p.state != "playing" for p in game_room.players.values()):
                        # All players have completed their actions, enter dealer turn
                        game_room.dealer_turn()
                    else:
                        game_room.set_current_player()
                    
                    print(f"Forced AI {current_player.name} stand complete")
                    
                    socketio.emit('game_update', game_room.to_dict(), room=game_room.room_id)
                    return True
        
        print("====== No AI actions need to be forced ======")
        return False

# Create global AI player manager instance
ai_player_manager = AIPlayer()