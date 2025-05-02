"""
App Module: Initialize Flask application and SocketIO
"""
import threading
import time
from flask import Flask
from flask_socketio import SocketIO

from config import SECRET_KEY, WTF_CSRF_ENABLED, PERMANENT_SESSION_LIFETIME, SESSION_TYPE
from utils import setup_ngrok, display_url
from config import USE_NGROK, NGROK_AUTH_TOKEN, PORT

# Create SocketIO instance (create here to share in routes and events)
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    """
    Create and configure Flask application
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Set Flask configuration
    app.secret_key = SECRET_KEY
    app.config['WTF_CSRF_ENABLED'] = WTF_CSRF_ENABLED
    app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME
    app.config['SESSION_TYPE'] = SESSION_TYPE
    
    # Initialize SocketIO with Flask application
    socketio.init_app(app)
    
    # Setup ngrok
    setup_ngrok(app, use_ngrok=USE_NGROK, auth_token=NGROK_AUTH_TOKEN, port=PORT)
    
    # Register blueprints
    with app.app_context():
        # Import and register routes
        from app.routes import register_routes
        register_routes(app)
        
        # Import and register Socket.IO event handlers
        from app.events import register_events
        register_events(socketio)
    
    # Add scheduled task to check AI players every 3 seconds
    def check_ai_players():
        try:
            from models import game_rooms, ai_player_manager
            from app import socketio
            
            # Current time
            current_time = time.time()
            
            # Traverse all rooms
            for room_id, game_room in game_rooms.items():
                # Track room state
                if not hasattr(game_room, 'last_state_change_time'):
                    game_room.last_state_change_time = current_time
                    game_room.stuck_timer = 0
                
                # Check if game is stuck (more than 5 seconds without state change)
                time_since_last_change = current_time - game_room.last_state_change_time
                
                # Game in betting phase
                if game_room.game_state == "betting":
                    ai_players_betting = [p for p_id, p in game_room.players.items() 
                                          if p.is_ai and p.state == "betting"]
                    
                    if ai_players_betting and time_since_last_change > 5:
                        print(f"Timer detected {len(ai_players_betting)} AI players in betting state and possibly stuck ({time_since_last_change:.1f} seconds without action), forcing bet")
                        if ai_player_manager.force_ai_action(game_room):
                            # Update state change time
                            game_room.last_state_change_time = current_time
                            game_room.stuck_timer = 0
                        else:
                            # If forced action failed, increase stuck timer
                            game_room.stuck_timer += 1
                            
                            # If consecutive failures, force reset game state
                            if game_room.stuck_timer >= 3:
                                print(f"Game seriously stuck, forcing reset to waiting state")
                                game_room.game_state = "waiting"
                                for player in game_room.players.values():
                                    if player.state == "betting":
                                        player.state = "waiting"
                                game_room.message = "Game has been reset, please get ready again"
                                game_room.last_state_change_time = current_time
                                game_room.stuck_timer = 0
                                # Use socketio instance to send update
                                socketio.emit('game_update', game_room.to_dict(), room=room_id)
                
                # Game in playing phase
                elif game_room.game_state == "playing":
                    # Get current player (if any)
                    if game_room.current_player_index < len(game_room.player_order):
                        current_player_id = game_room.player_order[game_room.current_player_index]
                        current_player = game_room.players.get(current_player_id)
                        
                        # If current player is AI and state is "playing", and over 5 seconds, force action
                        if (current_player and current_player.is_ai and 
                            current_player.state == "playing" and time_since_last_change > 5):
                            print(f"Timer detected AI {current_player.name} may be stuck ({time_since_last_change:.1f} seconds without action), forcing action")
                            if ai_player_manager.force_ai_action(game_room):
                                # Update state change time
                                game_room.last_state_change_time = current_time
                                game_room.stuck_timer = 0
                            else:
                                # If forced action failed, increase stuck timer
                                game_room.stuck_timer += 1
                                
                                # If consecutive failures, force move to next player
                                if game_room.stuck_timer >= 3:
                                    print(f"AI seriously stuck, forcing move to next player")
                                    current_player.state = "stand"
                                    game_room.current_player_index = (game_room.current_player_index + 1) % len(game_room.player_order)
                                    game_room.set_current_player()
                                    game_room.last_state_change_time = current_time
                                    game_room.stuck_timer = 0
                                    
                                    # Send update
                                    socketio.emit('game_update', game_room.to_dict(), room=room_id)
                    elif time_since_last_change > 10:
                        # If game in playing state but no player can act, possibly stuck
                        print(f"Game in playing state but no valid player can act, possibly stuck, attempting to fix")
                        game_room.stuck_timer += 1
                        
                        # If stuck for 3+ checks, force enter dealer turn
                        if game_room.stuck_timer >= 3:
                            print(f"Game stuck for a long time, forcing dealer's turn")
                            game_room.dealer_turn()
                            game_room.last_state_change_time = current_time
                            game_room.stuck_timer = 0
                            
                            # Send update
                            socketio.emit('game_update', game_room.to_dict(), room=room_id)
                
                # Game in waiting phase, check if AI needs to prepare
                elif game_room.game_state == "waiting":
                    ai_players_waiting = [p for p_id, p in game_room.players.items() 
                                         if p.is_ai and p.state == "waiting" and p.money > 0]
                    
                    if ai_players_waiting and time_since_last_change > 5:
                        print(f"Timer detected {len(ai_players_waiting)} AI players need to prepare")
                        for player in ai_players_waiting:
                            player.state = "ready"
                            
                            # Broadcast player ready status
                            socketio.emit('player_status_update', {
                                "player_id": player.player_id,
                                "player_state": player.state
                            }, room=room_id)
                        
                        # Check if all players with funds are ready
                        active_players = [p for p in game_room.players.values() if p.money > 0]
                        all_ready = active_players and all(p.state == "ready" for p in active_players)
                        
                        if all_ready:  # Allow single player game
                            if game_room.start_betting():  # Only broadcast game update if start_betting is successful
                                socketio.emit('game_update', game_room.to_dict(), room=room_id)
                        
                        # Update state change time
                        game_room.last_state_change_time = current_time
                        game_room.stuck_timer = 0
                
                # Game over phase might also get stuck
                elif game_room.game_state == "game_over" and time_since_last_change > 30:
                    # If game over state lasts too long, automatically reset game
                    print(f"Game over state lasting too long, automatically resetting game")
                    if game_room.prepare_new_round():
                        socketio.emit('game_update', game_room.to_dict(), room=room_id)
                        socketio.emit('notification', {"message": "A new round has automatically started"}, room=room_id)
                        game_room.last_state_change_time = current_time
                        game_room.stuck_timer = 0
        except Exception as e:
            print(f"AI check task error: {e}")
    
    # Setup scheduled task
    def schedule_check():
        try:
            check_ai_players()
        except Exception as e:
            print(f"AI check task error: {e}")
        threading.Timer(3.0, schedule_check).start()
    
    # Start scheduled task
    threading.Timer(3.0, schedule_check).start()
    
    return app

def start_display_url_thread(app):
    """Start thread to display URL"""
    url_thread = threading.Thread(target=lambda: display_url(app, PORT))
    url_thread.daemon = True
    url_thread.start()