"""
Game Room Class: Defines the room for blackjack games
"""
import random
from flask import request
from flask_socketio import emit

from models.card import Card
from models.player import Player
from config import MAX_PLAYERS_PER_ROOM

class GameRoom:
    """Game room class, manages a round of blackjack game"""
    
    def __init__(self, room_id, room_name, max_players=MAX_PLAYERS_PER_ROOM):
        """
        Initialize game room
        
        Args:
            room_id (str): Unique room identifier
            room_name (str): Room name
            max_players (int, optional): Maximum number of players
        """
        self.room_id = room_id
        self.room_name = room_name
        self.players = {}  # player_id -> Player object
        self.dealer = Player("dealer", "Dealer")
        self.max_players = max_players
        self.deck = []  # Card deck
        # Game states: waiting, betting, playing, dealer_turn, game_over
        self.game_state = "waiting"
        self.current_player_index = 0
        self.player_order = []  # Player action order
        self.message = "Waiting for players to join..."
        self.session_states = {}  # Store player session states
        self.initialize_deck()
    
    def initialize_deck(self):
        """Initialize card deck and shuffle"""
        suits = ['♥', '♦', '♣', '♠']
        values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.deck = []
        for suit in suits:
            for value in values:
                self.deck.append(Card(suit, value))
        random.shuffle(self.deck)
    
    def deal_card(self):
        """
        Deal a card from the deck
        
        Returns:
            Card: A card
        """
        if len(self.deck) <= 10:
            self.initialize_deck()
        return self.deck.pop()
    
    def calculate_score(self, hand):
        """
        Calculate the score of a hand
        
        Args:
            hand (list): A hand of cards
            
        Returns:
            int: Calculated score
        """
        score = 0
        aces = 0
        for card in hand:
            if card.value == 'A':
                aces += 1
                score += 11
            elif card.value in ['J', 'Q', 'K']:
                score += 10
            else:
                score += int(card.value)
        
        # Aces can be 1 or 11 points, if score exceeds 21 change Ace from 11 to 1
        while score > 21 and aces > 0:
            score -= 10
            aces -= 1
            
        return score
    
    def add_player(self, player):
        """
        Add a player to the room
        
        Args:
            player (Player): Player to add
            
        Returns:
            bool: Whether addition was successful
        """
        if len(self.players) >= self.max_players:
            return False
        
        self.players[player.player_id] = player
        self.player_order.append(player.player_id)
        
        # Check if this player previously existed in the session
        session_id = request.cookies.get('session_id') or request.args.get('session_id')
        if session_id:
            stored_state = self.get_player_state_from_session(session_id)
            if stored_state:
                player.state = stored_state
                
        return True
    
    def remove_player(self, player_id):
        """
        Remove a player from the room
        
        Args:
            player_id (str): ID of the player to remove
            
        Returns:
            bool: Whether removal was successful
        """
        if player_id in self.players:
            self.players.pop(player_id)
            
            # Remove from player order list
            if player_id in self.player_order:
                # Get player index in the list
                idx = self.player_order.index(player_id)
                self.player_order.remove(player_id)
                
                # If current player index is greater than removed player's index, decrement to maintain correct order
                if self.current_player_index > idx:
                    self.current_player_index -= 1
                
                # Ensure index won't exceed bounds
                if self.player_order and self.current_player_index >= len(self.player_order):
                    self.current_player_index = 0
            
            return True
        return False
    
    def get_player_state_from_session(self, session_id):
        """
        Get player state from session
        
        Args:
            session_id (str): Session ID
            
        Returns:
            str: Player state, returns None if doesn't exist
        """
        try:
            if session_id in self.session_states:
                return self.session_states[session_id]
        except:
            pass
        return None
    
    def store_player_state_to_session(self, session_id, state):
        """
        Store player state to session
        
        Args:
            session_id (str): Session ID
            state (str): Player state
        """
        self.session_states[session_id] = state
    
    def start_betting(self):
        """
        Start betting phase
        
        Returns:
            bool: Whether betting started successfully
        """
        if len(self.players) < 1:
            return False
        
        # Check if all non-spectating players are ready
        active_players = [p for p in self.players.values() if p.money > 0 and p.state != "spectating"]
        if not active_players:
            self.message = "No players with funds in the room, please wait for players with funds to join"
            return False
            
        all_ready = all(p.state == "ready" for p in active_players)
        
        if not all_ready:
            return False  # If any player is not ready, can't start betting
        
        self.game_state = "betting"
        self.message = "All players please place your bets"
        
        # Reset all player states
        for player in self.players.values():
            player.reset_for_new_round()
            # Players with enough funds enter betting state
            if player.money > 0:
                player.state = "betting"
            else:
                # Players without money enter spectator state
                player.state = "spectating"
                print(f"Player {player.name} has zero funds, entering spectator mode")
            
            # Save player current state to session
            from flask import request
            session_id = request.cookies.get('session_id') or request.args.get('session_id')
            if session_id and player.player_id == request.sid:  # Only save current player's state
                self.store_player_state_to_session(session_id, player.state)
        
        # Reset dealer state
        self.dealer.reset_for_new_round()
        
        return True
    
    def place_bet(self, player_id, bet_amount):
        """Player places a bet"""
        if self.game_state != "betting":
            print(f"Bet failed - game state is not 'betting': {self.game_state}")
            return False
        
        if player_id not in self.players:
            print(f"Bet failed - player ID does not exist: {player_id}")
            return False
        
        player = self.players[player_id]
        
        if player.state != "betting" or bet_amount > player.money:
            print(f"Bet failed - player state is not 'betting' or bet amount is too large: {player.state}, {bet_amount}, {player.money}")
            return False
        
        player.money -= bet_amount
        player.current_bet = bet_amount
        player.original_bet = bet_amount
        player.state = "ready"
        
        print(f"Player {player.name} bet successfully: {bet_amount}, remaining funds: {player.money}, new state: {player.state}")
        
        # Check if all non-spectating players with funds have placed bets
        active_players = [p for p in self.players.values() if (p.money > 0 or p.current_bet > 0) and p.state != "spectating"]
        betting_players = [p for p in active_players if p.state == "betting"]
        
        print(f"Bet check - active players: {len(active_players)}, betting players: {len(betting_players)}")
        
        # If no players are betting, all active players are ready
        if not betting_players and active_players:
            print("All players have placed bets, starting game")
            self.start_game()
        
        return True
    
    def start_game(self):
        """
        Start game after all players have bet
        
        Returns:
            bool: Whether game started successfully
        """
        self.game_state = "playing"
        
        # Deal cards to all players and dealer
        for player_id in self.player_order:
            player = self.players[player_id]
            if player.state == "ready":  # Only deal cards to ready players
                player.hand = [self.deal_card(), self.deal_card()]
                player.score = self.calculate_score(player.hand)
                
                # Check for natural blackjack
                if player.score == 21:
                    player.state = "blackjack"
                else:
                    player.state = "playing"
        
        # Deal cards to dealer
        self.dealer.hand = [self.deal_card(), self.deal_card()]
        self.dealer.score = self.calculate_score([self.dealer.hand[0]])  # Only calculate first card
        
        # Set current player
        self.current_player_index = 0
        self.set_current_player()
        
        return True
    
    def set_current_player(self):
        """
        Set current player
        
        Returns:
            bool: Whether setting was successful
        """
        if self.game_state != "playing" or len(self.player_order) == 0:
            return False
        
        # Find next player who needs to act
        for _ in range(len(self.player_order)):
            player_id = self.player_order[self.current_player_index]
            player = self.players[player_id]
            
            if player.state == "playing":
                self.message = f"{player.name}'s turn to act"
                return True
            
            # Move to next player
            self.current_player_index = (self.current_player_index + 1) % len(self.player_order)
        
        # If all players have finished acting, move to dealer's turn
        self.dealer_turn()
        return True
    
    def player_hit(self, player_id):
        """
        Player hits
        
        Args:
            player_id (str): Player ID
            
        Returns:
            bool: Whether hit was successful
        """
        if self.game_state != "playing" or player_id not in self.players:
            return False
        
        player = self.players[player_id]
        if player.state != "playing":
            return False
        
        # Confirm it's the current player's turn
        current_player_id = self.player_order[self.current_player_index]
        if player_id != current_player_id:
            return False
        
        # Player hits
        player.hand.append(self.deal_card())
        player.score = self.calculate_score(player.hand)
        
        # Check if busted, reached 21, or achieved five dragon
        if player.score > 21:
            player.state = "busted"
            self.message = f"{player.name} busted!"
            self.current_player_index = (self.current_player_index + 1) % len(self.player_order)
            self.set_current_player()
        elif player.score == 21:
            player.state = "stand"
            self.message = f"{player.name} got 21!"
            self.current_player_index = (self.current_player_index + 1) % len(self.player_order)
            self.set_current_player()
        elif len(player.hand) == 5 and player.score < 21:
            # Five Dragon rule
            player.state = "five_dragon"
            self.message = f"{player.name} got Five Dragon!"
            self.current_player_index = (self.current_player_index + 1) % len(self.player_order)
            self.set_current_player()
        
        return True
    
    def player_stand(self, player_id):
        """
        Player stands
        
        Args:
            player_id (str): Player ID
            
        Returns:
            bool: Whether stand was successful
        """
        if self.game_state != "playing" or player_id not in self.players:
            return False
        
        player = self.players[player_id]
        if player.state != "playing":
            return False
        
        # Confirm it's the current player's turn
        current_player_id = self.player_order[self.current_player_index]
        if player_id != current_player_id:
            return False
        
        player.state = "stand"
        self.message = f"{player.name} stands"
        
        # Move to next player
        self.current_player_index = (self.current_player_index + 1) % len(self.player_order)
        self.set_current_player()
        
        return True
    
    def player_double_down(self, player_id):
        """
        Player doubles down
        
        Args:
            player_id (str): Player ID
            
        Returns:
            bool: Whether double down was successful
        """
        if self.game_state != "playing" or player_id not in self.players:
            return False
        
        player = self.players[player_id]
        if player.state != "playing" or len(player.hand) != 2:
            return False
        
        # Confirm it's the current player's turn
        current_player_id = self.player_order[self.current_player_index]
        if player_id != current_player_id:
            return False
        
        # Check if player has enough money
        if player.money < player.current_bet:
            return False
        
        # Double down
        player.money -= player.current_bet
        player.current_bet *= 2
        
        # Take just one more card
        player.hand.append(self.deal_card())
        player.score = self.calculate_score(player.hand)
        
        if player.score > 21:
            player.state = "busted"
            self.message = f"{player.name} doubled down and busted!"
        else:
            player.state = "stand"
            self.message = f"{player.name} doubled down and stands"
        
        # Move to next player
        self.current_player_index = (self.current_player_index + 1) % len(self.player_order)
        self.set_current_player()
        
        return True
    
    def dealer_turn(self):
        """
        Dealer's turn
        
        Returns:
            bool: Whether dealer's turn completed successfully
        """
        self.game_state = "dealer_turn"
        self.message = "Dealer's turn"
        
        # Calculate dealer's actual score
        self.dealer.score = self.calculate_score(self.dealer.hand)
        
        # Dealer hits until 17 or higher (standard rule)
        while self.dealer.score < 17:
            # Check if dealer can achieve five dragon
            if len(self.dealer.hand) == 4 and self.dealer.score <= 21:
                # Try to achieve five dragon
                next_card = self.deck[-1]  # Peek at next card
                test_score = self.dealer.score
                if next_card.value == 'A':
                    test_score += 1  # A most conservatively worth 1 point
                elif next_card.value in ['J', 'Q', 'K']:
                    test_score += 10
                else:
                    test_score += int(next_card.value)
                
                # If next card would cause dealer to bust, don't take it
                if test_score > 21:
                    break
            
            self.dealer.hand.append(self.deal_card())
            self.dealer.score = self.calculate_score(self.dealer.hand)
        
        # Settle the game
        self.determine_winners()
        
        return True
    
    def determine_winners(self):
        """
        Settle the game, determine each player's win/loss
        
        Returns:
            bool: Whether settlement was successful
        """
        self.game_state = "game_over"
        
        dealer_score = self.dealer.score
        dealer_busted = dealer_score > 21
        dealer_five_dragon = len(self.dealer.hand) == 5 and dealer_score <= 21
        dealer_blackjack = dealer_score == 21 and len(self.dealer.hand) == 2
        
        for player_id, player in self.players.items():
            # If player didn't participate in this round or is spectating
            if player.state == "waiting" or player.state == "spectating":
                continue
                
            # If player has already busted, no further calculation needed
            if player.state == "busted":
                player.money += 0  # Already deducted when betting
                continue
            
            player_score = player.score
            player_five_dragon = player.state == "five_dragon"
            player_blackjack = player.state == "blackjack"
            
            # Handle five dragon cases
            if player_five_dragon and dealer_five_dragon:
                # Compare points
                if player_score > dealer_score:
                    player.money += player.current_bet * 3  # Return original bet + 2x
                    self.message = f"{player.name} wins with Five Dragon!"
                elif dealer_score > player_score:
                    # Already deducted money
                    self.message = f"{player.name}'s Five Dragon lost, dealer's Five Dragon has higher points"
                else:
                    player.money += player.current_bet  # Tie returns original bet
                    self.message = f"{player.name} ties with dealer's Five Dragon"
            elif player_five_dragon:
                player.money += player.current_bet * 3  # Five Dragon high payout
                self.message = f"{player.name} wins with Five Dragon!"
            elif dealer_five_dragon:
                # Already deducted money
                self.message = f"{player.name} lost to dealer's Five Dragon"
            # Handle blackjack cases
            elif player_blackjack and dealer_blackjack:
                player.money += player.current_bet  # Tie returns original bet
                self.message = f"{player.name} and dealer both have Blackjack, it's a tie"
            elif player_blackjack:
                player.money += int(player.current_bet * 2.5)  # Blackjack 1.5x payout
                self.message = f"{player.name} wins with Blackjack!"
            elif dealer_blackjack:
                # Already deducted money
                self.message = f"{player.name} lost to dealer's Blackjack"
            # Regular settlement
            elif dealer_busted:
                player.money += player.current_bet * 2  # Return original bet + win
                self.message = f"Dealer busted, {player.name} wins!"
            elif player_score > dealer_score:
                player.money += player.current_bet * 2  # Return original bet + win
                self.message = f"{player.name}'s score is higher than dealer's, {player.name} wins!"
            elif dealer_score > player_score:
                # Already deducted money
                self.message = f"{player.name}'s score is lower than dealer's, {player.name} lost"
            else:
                player.money += player.current_bet  # Tie returns original bet
                self.message = f"{player.name} ties with the dealer"
            
            # Do not automatically set players with zero funds to spectating
            # Allow them to continue in the current round
        
        from models import game_record_manager
        game_record_manager.add_game_record(self.room_id, self)

        return True
    
    def prepare_new_round(self):
        """
        Prepare for a new round
        
        Returns:
            bool: Whether preparation was successful
        """
        # Reset game state to waiting
        self.game_state = "waiting"
        self.message = "Ready to start a new round, please get ready"
        
        # Keep players' money and reset other game-related states
        for player in self.players.values():
            player.hand = []
            player.score = 0
            player.current_bet = 0
            player.original_bet = 0
            
            # Players with zero funds enter spectator mode, others enter waiting state
            if player.money <= 0:
                player.state = "spectating"
            else:
                player.state = "waiting"
        
        # Reset dealer
        self.dealer.hand = []
        self.dealer.score = 0
        
        # Reshuffle deck
        self.initialize_deck()
        
        return True
    
    def to_dict(self, include_hidden=False):
        """
        Convert game room to dictionary for JSON serialization
        
        Args:
            include_hidden (bool, optional): Whether to include hidden information, like dealer's second card
            
        Returns:
            dict: Dictionary containing room information
        """
        players_dict = {}
        for player_id, player in self.players.items():
            players_dict[player_id] = player.to_dict()
        
        # Handle dealer information, hide second card if game not over
        dealer_dict = self.dealer.to_dict()
        if not include_hidden and self.game_state in ["playing", "betting", "waiting"]:
            # Hide dealer's second card
            if len(dealer_dict["hand"]) > 1:
                dealer_dict["hand"][1] = {"suit": "?", "value": "?"}
                dealer_dict["score"] = self.calculate_score([self.dealer.hand[0]])
        
        return {
            "room_id": self.room_id,
            "room_name": self.room_name,
            "players": players_dict,
            "dealer": dealer_dict,
            "game_state": self.game_state,
            "message": self.message,
            "current_player_index": self.current_player_index,
            "player_order": self.player_order
        }
        
    def check_player_left(self, left_player_id):
        """
        Check game state after a player leaves
        
        Args:
            left_player_id (str): ID of the player who left
                
        Returns:
            bool: Whether handling was successful
        """
        # Check current game state
        if self.game_state == "playing":
            # Check if the player who left is the current player
            current_player_index = self.current_player_index
            if current_player_index < len(self.player_order):
                current_player_id = self.player_order[current_player_index]
                if current_player_id == left_player_id:
                    # Current player left, move to next player
                    if left_player_id in self.player_order:
                        self.player_order.remove(left_player_id)
                    # If list is empty after removal, end the game
                    if not self.player_order:
                        self.game_state = "game_over"
                        self.message = "All players left, game over"
                    else:
                        # Adjust index to ensure it won't exceed bounds
                        self.current_player_index = self.current_player_index % len(self.player_order)
                        self.set_current_player()
                elif left_player_id in self.player_order:
                    # Not current player, but in action queue
                    self.player_order.remove(left_player_id)
                    # If current index is greater than removed player's index, decrement
                    idx = self.player_order.index(left_player_id) if left_player_id in self.player_order else -1
                    if idx >= 0 and self.current_player_index > idx:
                        self.current_player_index -= 1
        elif self.game_state == "betting":
            # In betting phase, check if all players have bet
            active_players = [p for p in self.players.values() if p.money > 0 and p.state != "spectating"]
            betting_players = [p for p in active_players if p.state == "betting"]
            
            # If no players are betting, all active players are ready
            if not betting_players and active_players:
                self.start_game()
        
        # Check if there are enough players to continue the game
        active_players = [p for p in self.players.values() if p.state not in ["spectating", "waiting"] and p.money > 0]
        if len(active_players) < 1 and self.game_state not in ["waiting", "game_over"]:
            # Not enough active players, end current game
            self.game_state = "waiting"
            self.message = "Not enough players, please wait for new players to join and prepare"
            
            # Reset all player states
            for player in self.players.values():
                player.hand = []
                player.score = 0
                player.current_bet = 0
                player.original_bet = 0
                if player.money > 0:
                    player.state = "waiting"
                else:
                    player.state = "spectating"
            
            # Reset dealer
            self.dealer.hand = []
            self.dealer.score = 0
        
        return True