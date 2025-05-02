"""
Card Class: Define playing cards in blackjack game
"""

class Card:
    """Card class, representing a playing card"""
    
    def __init__(self, suit, value):
        """
        Initialize a card
        
        Args:
            suit (str): Suit ('♥', '♦', '♣', '♠')
            value (str): Value ('A', '2', ..., '10', 'J', 'Q', 'K')
        """
        self.suit = suit
        self.value = value
    
    def to_dict(self):
        """
        Convert card to dictionary for JSON serialization
        
        Returns:
            dict: Dictionary containing suit and value
        """
        return {"suit": self.suit, "value": self.value}
    
    def __str__(self):
        """String representation of card"""
        return f"{self.suit}{self.value}"