# Final_Project
Final project for Software Carpenter

# Luxury Casino Blackjack

A modular, animated Python blackjack game with multiple AI players and advanced gameplay features.

## Overview

This blackjack game is built using PyGame and features:

- Beautiful card animations and visual effects
- Multiple AI players with different strategies
- Advanced blackjack rules like splitting and "Five Card Charlie"
- Realistic chip betting system
- Modular code structure for easy customization

## File Structure

```
blackjack/
├── super_main.py   # Main entry point
├── constants.py    # Game constants and configuration
├── card.py         # Card, Deck, and Hand classes
├── player.py       # Player, Dealer, and ChipStack classes
├── gui.py          # GUI elements (buttons, chips)
├── effects.py      # Visual effects
├── game.py         # Main game logic
└── assets/         # Game assets directory
    └── cards/      # Card images
```

## Module Descriptions

### main.py

The entry point for the game. Creates and runs the main game instance.

```python
# Example usage
python super_main.py
```

### constants.py

Contains all game constants including screen dimensions, colors, card sizes, and enumerations.

### card.py

Handles all card-related functionality:
- `Card` class: Represents a single playing card with suit, value, and animation properties
- `Deck` class: Manages a collection of cards with shuffling and dealing capabilities
- `Hand` class: Represents a player's hand with methods for calculating values and checking special conditions

### player.py

Contains classes for game participants:
- `Player` class: Manages player data (human or AI), betting, and decision-making
- `Dealer` class: Specialized player class for the dealer with simplified behavior
- `ChipStack` class: Visual representation of betting chips

### gui.py

Defines interactive GUI elements:
- `Button` class: Interactive buttons with hover effects and animations
- `ChipButton` class: Specialized buttons for betting with chip appearance

### effects.py

Visual effects to enhance the gaming experience:
- `Particle` class: Creates animated particle effects for wins and other events

### game.py

The main game logic:
- `AdvancedBlackjackGame` class: Manages game state, player turns, dealing, and rendering

## Game Rules

- Standard blackjack rules apply (closest to 21 without going over wins)
- Special "Five Card Charlie" rule: Automatically win with 5 cards without busting
- Players can split pairs of matching cards
- Blackjack pays 3:2
- Dealer must hit on 16 or less and stand on 17 or more

## Controls

- Click chip buttons to place bets
- Use "Hit" button to draw another card
- Use "Stand" button to end your turn
- Use "Split" button to split pairs when available
- Use "Deal" button to start a new round
- Use "Reset Bet" button to clear your current bet

## Customization Tips

- To modify game appearance: Edit colors and dimensions in `constants.py`
- To adjust game rules: Modify game logic in `game.py`
- To change AI behavior: Update AI logic in the `Player` class in `player.py`
- To add new visual effects: Extend the `effects.py` module

## Requirements

- Python 3.6+
- PyGame library

## Installation

1. Clone the repository or download the source code
2. Install PyGame: `pip install pygame`
3. Create an `assets/cards` directory and add card images
4. Run the game: `python super_main.py`

## Card Assets

The game expects card images in the `assets/cards` directory with the following naming convention:
- Card faces: `[Value][Suit].png` (e.g., `AS.png` for Ace of Spades)
- Card back: `back.png`

Values: A (Ace), 2-10, J (Jack), Q (Queen), K (King)
Suits: H (Hearts), D (Diamonds), C (Clubs), S (Spades)
