"""
Game State Observer: Monitor game state changes, ensure AI players don't get stuck

This file should be saved as models/game_observer.py
"""
import time
import threading
from app import socketio

class GameObserver:
    """Game state observer, monitor game state and force resolve stuck AI"""
    
    def __init__(self, socketio):
        """
        Initialize game observer
        
        Args:
            socketio (SocketIO): SocketIO instance
        """
        self.socketio = socketio
        self.room_states = {}  # Store room states
        self.running = False
        self.observer_thread = None
        
    def start(self, check_interval=2.0):
        """
        Start observer
        
        Args:
            check_interval (float): Check interval time (seconds)
        """
        if self.running:
            return
            
        self.running = True
        
        def observer_loop():
            print("Game observer started")
            while self.running:
                try:
                    self.check_all_rooms()
                except Exception as e:
                    print(f"Game observer error: {e}")
                time.sleep(check_interval)
                
        self.observer_thread = threading.Thread(target=observer_loop)
        self.observer_thread.daemon = True
        self.observer_thread.start()
    
    def stop(self):
        """Stop observer"""
        self.running = False
        if self.observer_thread:
            self.observer_thread.join(timeout=1.0)
            self.observer_thread = None
    
    def check_all_rooms(self):
        """Check all room states"""
        from models import game_rooms, ai_player_manager
        
        current_time = time.time()
        
        for room_id, game_room in game_rooms.items():
            # Initialize room state record
            if room_id not in self.room_states:
                self.room_states[room_id] = {
                    'game_state': game_room.game_state,
                    'current_player_index': game_room.current_player_index,
                    'last_update_time': current_time,
                    'stuck_count': 0
                }
                continue
            
            room_state = self.room_states[room_id]
            
            # Detect if state has changed
            if (game_room.game_state != room_state['game_state'] or
                game_room.current_player_index != room_state['current_player_index']):
                # State has changed, update record
                room_state['game_state'] = game_room.game_state
                room_state['current_player_index'] = game_room.current_player_index
                room_state['last_update_time'] = current_time
                room_state['stuck_count'] = 0
                continue
            
            # Check if stuck (more than 5 seconds without state change)
            time_since_update = current_time - room_state['last_update_time']
            
            if time_since_update > 5.0:  # Consider stuck after 5 seconds without state change
                room_state['stuck_count'] += 1
                # Check what the state is when stuck
                self._handle_stuck_room(game_room, room_state, room_id)
                # Regardless of handling result, update timestamp to prevent continuous triggering
                room_state['last_update_time'] = current_time
    
    def _handle_stuck_room(self, game_room, room_state, room_id):
        """
        Handle stuck room
        
        Args:
            game_room (GameRoom): Stuck game room
            room_state (dict): Room state record
            room_id (str): Room ID
        """
        from models import ai_player_manager
        
        stuck_count = room_state['stuck_count']
        print(f"Room {room_id} stuck detection: state={game_room.game_state}, stuck count={stuck_count}")
        
        # Handle based on game state
        if game_room.game_state == "betting":
            # Handle betting phase stuck
            ai_players_betting = [p for p_id, p in game_room.players.items() 
                                 if p.is_ai and p.state == "betting"]
            
            if ai_players_betting:
                print(f"Forced handling: {len(ai_players_betting)} AI players stuck in betting phase")
                for player in ai_players_betting:
                    # Force bet
                    bet_amount = min(100, player.money)
                    player.money -= bet_amount
                    player.current_bet = bet_amount
                    player.original_bet = bet_amount
                    player.state = "ready"
                    print(f"Force AI {player.name} to bet: {bet_amount}")
                
                # Check if can start game
                active_players = [p for p in game_room.players.values() 
                                  if p.money > 0 and p.state != "spectating"]
                betting_players = [p for p in active_players if p.state == "betting"]
                
                if not betting_players and active_players:
                    print("All AI players have been forced to bet, starting game")
                    game_room.start_game()
                
                socketio.emit('game_update', game_room.to_dict(), room=room_id)
                
        elif game_room.game_state == "playing":
            # Handle playing phase stuck
            if game_room.current_player_index < len(game_room.player_order):
                current_player_id = game_room.player_order[game_room.current_player_index]
                current_player = game_room.players.get(current_player_id)
                
                if current_player and current_player.is_ai and current_player.state == "playing":
                    print(f"Forced handling: AI {current_player.name} stuck in action phase")
                    
                    # Force stand
                    if game_room.player_stand(current_player_id):
                        print(f"Force AI {current_player.name} stand successful")
                    else:
                        # If normal method fails, directly modify state
                        print(f"Normal stand failed, directly modify AI state")
                        current_player.state = "stand"
                        game_room.current_player_index = (game_room.current_player_index + 1) % len(game_room.player_order)
                        game_room.set_current_player()
                    
                    socketio.emit('game_update', game_room.to_dict(), room=room_id)