import random
import time
from enum import Enum

class Suit(Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        
    def __str__(self):
        if self.value == 1:
            rank = "Ace"
        elif self.value == 11:
            rank = "Jack"
        elif self.value == 12:
            rank = "Queen"
        elif self.value == 13:
            rank = "King"
        else:
            rank = str(self.value)
            
        return f"{rank} of {self.suit.value}"
    
    def get_card_value(self):
        if self.value == 1:
            return 11  # Ace is 11 by default, will be handled as 1 when needed
        elif self.value > 10:
            return 10  # Face cards are worth 10
        else:
            return self.value

class Deck:
    def __init__(self):
        self.cards = []
        self.create_deck()
        
    def create_deck(self):
        for suit in Suit:
            for value in range(1, 14):  # 1 = Ace, 11 = Jack, 12 = Queen, 13 = King
                self.cards.append(Card(suit, value))
        
    def shuffle(self):
        random.shuffle(self.cards)
        
    def deal_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            print("Deck is empty. Creating and shuffling a new deck.")
            self.create_deck()
            self.shuffle()
            return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
        
    def add_card(self, card):
        self.cards.append(card)
        
    def get_value(self):
        value = 0
        aces = 0
        
        for card in self.cards:
            card_value = card.get_card_value()
            if card_value == 11:
                aces += 1
            value += card_value
        
        # Handle aces if the total value exceeds 21
        while value > 21 and aces > 0:
            value -= 10  # Convert an ace from 11 to 1
            aces -= 1
            
        return value
    
    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21
    
    def clear(self):
        self.cards = []
        
    def __str__(self):
        return ", ".join(str(card) for card in self.cards)

class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.hand = Hand()
        self.chips = chips
        
    def place_bet(self, amount):
        if amount > self.chips:
            print(f"Cannot bet {amount}. You only have {self.chips} chips.")
            return 0
        else:
            self.chips -= amount
            return amount
    
    def add_chips(self, amount):
        self.chips += amount
        
    def __str__(self):
        return f"{self.name} ({self.chips} chips)"

class Dealer:
    def __init__(self):
        self.name = "Dealer"
        self.hand = Hand()
    
    def show_partial_hand(self):
        if len(self.hand.cards) > 0:
            return f"Dealer shows: {self.hand.cards[0]} and [Hidden Card]"
        else:
            return "Dealer has no cards"

class Blackjack:
    def __init__(self):
        self.deck = Deck()
        self.player = Player("Player")
        self.dealer = Dealer()
        self.bet = 0
        
    def setup_game(self):
        self.deck.shuffle()
        self.player.hand.clear()
        self.dealer.hand.clear()
        
        # Deal initial cards
        self.player.hand.add_card(self.deck.deal_card())
        self.dealer.hand.add_card(self.deck.deal_card())
        self.player.hand.add_card(self.deck.deal_card())
        self.dealer.hand.add_card(self.deck.deal_card())
        
    def play_game(self):
        print("\n===== NEW GAME =====")
        print(f"You have {self.player.chips} chips.")
        
        # Get player's bet
        while True:
            try:
                bet_amount = int(input("Place your bet: "))
                if bet_amount <= 0:
                    print("Bet must be greater than zero.")
                    continue
                self.bet = self.player.place_bet(bet_amount)
                if self.bet > 0:
                    break
            except ValueError:
                print("Please enter a valid number.")
        
        self.setup_game()
        
        # Show initial hands
        print(f"\nYour hand: {self.player.hand} (Value: {self.player.hand.get_value()})")
        print(self.dealer.show_partial_hand())
        
        # Check for blackjack
        if self.player.hand.is_blackjack():
            print("Blackjack! You win 3:2 on your bet!")
            self.player.add_chips(int(self.bet * 2.5))
            return
        
        # Player's turn
        while True:
            choice = input("\nDo you want to (H)it or (S)tand? ").upper()
            
            if choice == 'H':
                self.player.hand.add_card(self.deck.deal_card())
                print(f"Your hand: {self.player.hand} (Value: {self.player.hand.get_value()})")
                
                if self.player.hand.get_value() > 21:
                    print("Bust! You lose.")
                    return
            elif choice == 'S':
                break
            else:
                print("Invalid choice. Please enter 'H' or 'S'.")
        
        # Dealer's turn
        print(f"\nDealer's hand: {self.dealer.hand} (Value: {self.dealer.hand.get_value()})")
        
        while self.dealer.hand.get_value() < 17:
            time.sleep(1)  # Pause for effect
            self.dealer.hand.add_card(self.deck.deal_card())
            print(f"Dealer hits: {self.dealer.hand.cards[-1]}")
            print(f"Dealer's hand: {self.dealer.hand} (Value: {self.dealer.hand.get_value()})")
            
            if self.dealer.hand.get_value() > 21:
                print("Dealer busts! You win!")
                self.player.add_chips(self.bet * 2)
                return
        
        # Determine winner
        player_value = self.player.hand.get_value()
        dealer_value = self.dealer.hand.get_value()
        
        print(f"\nYour hand value: {player_value}")
        print(f"Dealer's hand value: {dealer_value}")
        
        if player_value > dealer_value:
            print("You win!")
            self.player.add_chips(self.bet * 2)
        elif player_value < dealer_value:
            print("Dealer wins!")
        else:
            print("Push! It's a tie.")
            self.player.add_chips(self.bet)  # Return the bet amount

def main():
    print("Welcome to Blackjack!")
    game = Blackjack()
    
    while True:
        game.play_game()
        
        if game.player.chips <= 0:
            print("You're out of chips! Game over.")
            break
            
        play_again = input("\nDo you want to play again? (Y/N): ").upper()
        if play_again != 'Y':
            print(f"Thanks for playing! You leave with {game.player.chips} chips.")
            break

if __name__ == "__main__":
    main()


