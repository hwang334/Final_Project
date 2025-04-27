import pygame
import random
import sys
from enum import Enum

# Initialize pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

# Card dimensions
CARD_WIDTH = 100
CARD_HEIGHT = 140

class Suit(Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.face_up = True
        
    def __str__(self):
        if self.value == 1:
            rank = "A"
        elif self.value == 11:
            rank = "J"
        elif self.value == 12:
            rank = "Q"
        elif self.value == 13:
            rank = "K"
        else:
            rank = str(self.value)
            
        suit_symbol = ""
        if self.suit == Suit.HEARTS:
            suit_symbol = "♥"
        elif self.suit == Suit.DIAMONDS:
            suit_symbol = "♦"
        elif self.suit == Suit.CLUBS:
            suit_symbol = "♣"
        elif self.suit == Suit.SPADES:
            suit_symbol = "♠"
            
        return f"{rank}{suit_symbol}"
    
    def get_card_value(self):
        if self.value == 1:
            return 11  # Ace is 11 by default, will be handled as 1 when needed
        elif self.value > 10:
            return 10  # Face cards are worth 10
        else:
            return self.value
    
    def draw(self, screen, x, y):
        # Draw card outline
        pygame.draw.rect(screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
        pygame.draw.rect(screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
        
        if self.face_up:
            # Draw card suit and value
            font = pygame.font.Font(None, 36)
            
            # Get the card text and color
            card_text = self.__str__()
            text_color = BLACK
            if self.suit == Suit.HEARTS or self.suit == Suit.DIAMONDS:
                text_color = RED
            
            # Draw text in top left and bottom right
            text = font.render(card_text, True, text_color)
            screen.blit(text, (x + 10, y + 10))
            screen.blit(pygame.transform.rotate(text, 180), (x + CARD_WIDTH - 40, y + CARD_HEIGHT - 40))
            
            # Draw a larger symbol in the middle
            font_big = pygame.font.Font(None, 60)
            if self.suit == Suit.HEARTS:
                symbol = font_big.render("♥", True, text_color)
            elif self.suit == Suit.DIAMONDS:
                symbol = font_big.render("♦", True, text_color)
            elif self.suit == Suit.CLUBS:
                symbol = font_big.render("♣", True, text_color)
            else:  # SPADES
                symbol = font_big.render("♠", True, text_color)
            
            symbol_rect = symbol.get_rect(center=(x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2))
            screen.blit(symbol, symbol_rect)
        else:
            # Draw card back
            pygame.draw.rect(screen, BLUE, (x + 5, y + 5, CARD_WIDTH - 10, CARD_HEIGHT - 10))
            pygame.draw.rect(screen, BLUE, (x + 15, y + 15, CARD_WIDTH - 30, CARD_HEIGHT - 30), 2)

class Deck:
    def __init__(self):
        self.cards = []
        self.create_deck()
        
    def create_deck(self):
        self.cards = []
        for suit in Suit:
            for value in range(1, 14):  # 1 = Ace, 11 = Jack, 12 = Queen, 13 = King
                self.cards.append(Card(suit, value))
        
    def shuffle(self):
        random.shuffle(self.cards)
        
    def deal_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
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
    
    def draw(self, screen, x, y, is_dealer=False, hide_first_card=False):
        for i, card in enumerate(self.cards):
            # Hide dealer's first card if necessary
            if is_dealer and i == 0 and hide_first_card:
                card.face_up = False
            else:
                card.face_up = True
                
            card.draw(screen, x + i * 30, y)

class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.hand = Hand()
        self.chips = chips
        
    def place_bet(self, amount):
        if amount > self.chips:
            return 0
        else:
            self.chips -= amount
            return amount
    
    def add_chips(self, amount):
        self.chips += amount

class Dealer:
    def __init__(self):
        self.name = "Dealer"
        self.hand = Hand()

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False

class ChipButton:
    def __init__(self, x, y, radius, value, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.value = value
        self.color = color
        self.is_hovered = False
        
    def draw(self, screen):
        color = (min(self.color[0] + 30, 255), min(self.color[1] + 30, 255), min(self.color[2] + 30, 255)) if self.is_hovered else self.color
        pygame.draw.circle(screen, color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius, 2)
        
        font = pygame.font.Font(None, 30)
        text = font.render(str(self.value), True, BLACK)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)
        
    def check_hover(self, mouse_pos):
        distance = ((mouse_pos[0] - self.x) ** 2 + (mouse_pos[1] - self.y) ** 2) ** 0.5
        self.is_hovered = distance <= self.radius
        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False

class BlackjackGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Blackjack")
        self.clock = pygame.time.Clock()
        
        self.deck = Deck()
        self.player = Player("Player")
        self.dealer = Dealer()
        
        self.current_bet = 0
        self.game_state = "betting"  # betting, player_turn, dealer_turn, game_over
        self.message = ""
        
        self.hit_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 100, 120, 60, "Hit", GREEN, (100, 200, 100))
        self.stand_button = Button(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT - 100, 120, 60, "Stand", RED, (200, 100, 100))
        self.deal_button = Button(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT - 180, 120, 60, "Deal", BLUE, (100, 100, 200))
        
        # Chip buttons for betting
        self.chip_buttons = [
            ChipButton(SCREEN_WIDTH // 4 - 150, SCREEN_HEIGHT - 100, 30, 5, (200, 200, 200)),
            ChipButton(SCREEN_WIDTH // 4 - 75, SCREEN_HEIGHT - 100, 30, 25, (0, 200, 0)),
            ChipButton(SCREEN_WIDTH // 4, SCREEN_HEIGHT - 100, 30, 50, (200, 0, 0)),
            ChipButton(SCREEN_WIDTH // 4 + 75, SCREEN_HEIGHT - 100, 30, 100, (0, 0, 200))
        ]
        
        # Start new game and shuffle deck
        self.start_new_game()
    
    def start_new_game(self):
        self.deck.create_deck()
        self.deck.shuffle()
        self.player.hand.clear()
        self.dealer.hand.clear()
        self.current_bet = 0
        self.game_state = "betting"
        self.message = "Place your bet!"
    
    def deal_initial_cards(self):
        # Deal two cards to player and dealer
        self.player.hand.add_card(self.deck.deal_card())
        self.dealer.hand.add_card(self.deck.deal_card())
        self.player.hand.add_card(self.deck.deal_card())
        self.dealer.hand.add_card(self.deck.deal_card())
        
        # Check for blackjack
        if self.player.hand.is_blackjack():
            if self.dealer.hand.is_blackjack():
                self.message = "Both have Blackjack! Push!"
                self.player.add_chips(self.current_bet)  # Return bet
                self.game_state = "game_over"
            else:
                self.message = "Blackjack! You win 3:2!"
                self.player.add_chips(int(self.current_bet * 2.5))  # Pay 3:2
                self.game_state = "game_over"
        elif self.dealer.hand.is_blackjack():
            self.message = "Dealer has Blackjack! You lose."
            self.game_state = "game_over"
        else:
            self.game_state = "player_turn"
            self.message = "Your turn. Hit or Stand?"
    
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        for button in [self.hit_button, self.stand_button, self.deal_button]:
            button.check_hover(mouse_pos)
        
        for chip in self.chip_buttons:
            chip.check_hover(mouse_pos)
        
        # Handle button clicks based on game state
        if self.game_state == "betting":
            # Chip buttons for betting
            for chip in self.chip_buttons:
                if chip.is_clicked(event):
                    if self.player.chips >= chip.value:
                        self.current_bet += chip.value
                        self.player.chips -= chip.value
                    
            # Deal button to start the game
            if self.deal_button.is_clicked(event) and self.current_bet > 0:
                self.deal_initial_cards()
                
        elif self.game_state == "player_turn":
            # Hit button
            if self.hit_button.is_clicked(event):
                self.player.hand.add_card(self.deck.deal_card())
                
                if self.player.hand.get_value() > 21:
                    self.message = "Bust! You lose."
                    self.game_state = "game_over"
            
            # Stand button
            elif self.stand_button.is_clicked(event):
                self.game_state = "dealer_turn"
        
        elif self.game_state == "game_over":
            # Deal button to start a new game
            if self.deal_button.is_clicked(event):
                self.start_new_game()
        
        return True
    
    def handle_dealer_turn(self):
        if self.game_state == "dealer_turn":
            # Dealer draws until 17 or higher
            if self.dealer.hand.get_value() < 17:
                self.dealer.hand.add_card(self.deck.deal_card())
                # Add a small delay for visual effect
                pygame.time.delay(500)
            else:
                self.determine_winner()
                self.game_state = "game_over"
    
    def determine_winner(self):
        player_value = self.player.hand.get_value()
        dealer_value = self.dealer.hand.get_value()
        
        if dealer_value > 21:
            self.message = "Dealer busts! You win!"
            self.player.add_chips(self.current_bet * 2)  # Return bet + winnings
        elif player_value > dealer_value:
            self.message = "You win!"
            self.player.add_chips(self.current_bet * 2)  # Return bet + winnings
        elif player_value < dealer_value:
            self.message = "Dealer wins!"
        else:
            self.message = "Push! It's a tie."
            self.player.add_chips(self.current_bet)  # Return bet
    
    def draw(self):
        # Draw background
        self.screen.fill(GREEN)
        
        # Draw title
        font_large = pygame.font.Font(None, 60)
        title = font_large.render("Blackjack", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Draw message
        font = pygame.font.Font(None, 36)
        message_text = font.render(self.message, True, WHITE)
        self.screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, 80))
        
        # Draw player's chips and bet
        chips_text = font.render(f"Chips: {self.player.chips}", True, WHITE)
        self.screen.blit(chips_text, (50, SCREEN_HEIGHT - 50))
        
        bet_text = font.render(f"Bet: {self.current_bet}", True, WHITE)
        self.screen.blit(bet_text, (50, SCREEN_HEIGHT - 90))
        
        # Draw hands
        # Dealer's hand
        dealer_text = font.render("Dealer", True, WHITE)
        self.screen.blit(dealer_text, (50, 150))
        
        hide_first_card = self.game_state == "player_turn"
        self.dealer.hand.draw(self.screen, 50, 190, True, hide_first_card)
        
        if not hide_first_card:
            dealer_value = font.render(f"Value: {self.dealer.hand.get_value()}", True, WHITE)
            self.screen.blit(dealer_value, (300, 150))
        
        # Player's hand
        player_text = font.render("Player", True, WHITE)
        self.screen.blit(player_text, (50, 400))
        
        self.player.hand.draw(self.screen, 50, 440)
        
        player_value = font.render(f"Value: {self.player.hand.get_value()}", True, WHITE)
        self.screen.blit(player_value, (300, 400))
        
        # Draw buttons based on game state
        if self.game_state == "betting":
            # Draw chip buttons
            for chip in self.chip_buttons:
                chip.draw(self.screen)
                
            # Draw deal button if there's a bet
            if self.current_bet > 0:
                self.deal_button.draw(self.screen)
                
        elif self.game_state == "player_turn":
            self.hit_button.draw(self.screen)
            self.stand_button.draw(self.screen)
            
        elif self.game_state == "game_over":
            self.deal_button.draw(self.screen)
            
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                running = self.handle_event(event)
                if not running:
                    break
            
            # Handle dealer's turn if in that state
            self.handle_dealer_turn()
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(60)

def main():
    game = BlackjackGame()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
