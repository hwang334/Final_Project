"""
Player Class: Defines the player in blackjack game
"""

class Player:
    """Player class, represents a player in the game"""
    
    def __init__(self, player_id, name, is_ai=False, ai_difficulty=None):
        """
        Initialize a player
        
        Args:
            player_id (str): Player unique identifier
            name (str): Player name
            is_ai (bool, optional): Whether is AI player. Default False.
            ai_difficulty (str, optional): AI difficulty. Default None.
        """
        self.player_id = player_id
        self.name = name
        self.hand = []  # Player's hand
        self.score = 0  # Current score
        self.money = 1000  # Initial funds
        self.current_bet = 0  # Current bet amount
        self.original_bet = 0  # Original bet amount (for double down)
        self.is_ai = is_ai  # Whether is AI player
        self.ai_difficulty = ai_difficulty  # AI difficulty
        self.is_disconnected = False  # Whether disconnected
        # Player states: waiting, ready, betting, playing, stand, busted, blackjack, spectating
        self.state = "waiting"
    
    def to_dict(self):
        """
        Convert player to dictionary for JSON serialization
        
        Returns:
            dict: Dictionary containing player information
        """
        return {
            "player_id": self.player_id,
            "name": self.name,
            "hand": [card.to_dict() for card in self.hand],
            "score": self.score,
            "money": self.money,
            "current_bet": self.current_bet,
            "state": self.state,
            "is_ai": self.is_ai,
            "ai_difficulty": self.ai_difficulty,
            "is_disconnected": self.is_disconnected
        }
    
    def reset_for_new_round(self):
        """Reset player state, prepare for new round"""
        self.hand = []
        self.score = 0
        self.current_bet = 0
        self.original_bet = 0
        if self.money <= 0:
            self.state = "spectating"
        else:
            self.state = "waiting"