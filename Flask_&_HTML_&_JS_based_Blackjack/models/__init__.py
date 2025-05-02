"""
Models Module: Contains game data models
"""
from models.card import Card
from models.player import Player
from models.game_room import GameRoom
from models.game_record import game_record_manager
from models.ai_player import ai_player_manager
from models.game_observer import GameObserver

# Store all game rooms
game_rooms = {}

# Player session management, store sid to player_id mapping
player_sessions = {}

game_observer = None