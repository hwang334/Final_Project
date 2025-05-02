"""
Routes Module: Define all HTTP routes
"""
import uuid
from flask import render_template, request, jsonify

from models import game_rooms, ai_player_manager, game_record_manager
from models.game_room import GameRoom
from app import socketio

def register_routes(app):
    """
    Register all routes to Flask application
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.route('/')
    def index():
        """Home page route"""
        # Pass ngrok URL to template
        ngrok_url = app.config.get("BASE_URL", "")
        return render_template('index.html', ngrok_url=ngrok_url, config=app.config)
    
    @app.route('/room/<room_id>')
    def room(room_id):
        """Room page route"""
        if room_id not in game_rooms:
            return "Room does not exist", 404
        return render_template('room.html', room_id=room_id)
    
    @app.route('/api/create-room', methods=['POST'])
    def create_room():
        """Create new game room API"""
        data = request.get_json()
        room_name = data.get('room_name', f"Room {len(game_rooms) + 1}")
        
        room_id = str(uuid.uuid4())
        game_rooms[room_id] = GameRoom(room_id, room_name)
        
        return jsonify({"success": True, "room_id": room_id})
    
    @app.route('/api/rooms')
    def get_rooms():
        """Get all game rooms API"""
        rooms_list = []
        for room_id, room in game_rooms.items():
            rooms_list.append({
                "room_id": room.room_id,
                "room_name": room.room_name,
                "player_count": len(room.players),
                "max_players": room.max_players,
                "game_state": room.game_state
            })
        return jsonify(rooms_list)
    
    @app.route('/api/add-ai-player', methods=['POST'])
    def add_ai_player():
        """Add AI player to room"""
        from models import game_rooms, ai_player_manager
        
        data = request.get_json()
        room_id = data.get('room_id')
        difficulty = data.get('difficulty', 'medium')
        
        if room_id not in game_rooms:
            return jsonify({"success": False, "message": "Room does not exist"})
        
        # Check if room is full
        game_room = game_rooms[room_id]
        if len(game_room.players) >= game_room.max_players:
            return jsonify({"success": False, "message": "Room is full"})
        
        # Generate AI player ID
        ai_id = f"ai_{uuid.uuid4().hex[:8]}"
        
        # Create AI player
        ai_player = ai_player_manager.create_ai_player(ai_id, difficulty)
        
        # Add to room
        if game_room.add_player(ai_player):
            # Broadcast new player joined message
            socketio.emit('player_joined', {"player": ai_player.to_dict()}, room=room_id)
            
            # Immediately send game state update to ensure UI shows new AI player
            socketio.emit('game_update', game_room.to_dict(), room=room_id)
            
            # Add code: Let AI automatically prepare
            # Delay a bit to let client update UI
            socketio.sleep(1)
            ai_player_manager.handle_ai_turns(game_room)
            
            return jsonify({"success": True, "player_id": ai_id, "player": ai_player.to_dict()})
        else:
            return jsonify({"success": False, "message": "Failed to add AI player"})

    @app.route('/api/remove-ai-player', methods=['POST'])
    def remove_ai_player():
        """Remove AI player from room"""
        from models import game_rooms, ai_player_manager
        
        data = request.get_json()
        room_id = data.get('room_id')
        player_id = data.get('player_id')
        
        if room_id not in game_rooms:
            return jsonify({"success": False, "message": "Room does not exist"})
        
        game_room = game_rooms[room_id]
        
        # Ensure it's an AI player
        if player_id not in game_room.players or not game_room.players[player_id].is_ai:
            return jsonify({"success": False, "message": "Specified player is not AI or doesn't exist"})
        
        # Remove player from room
        if game_room.remove_player(player_id):
            # Remove from AI manager
            ai_player_manager.remove_ai_player(player_id)
            
            # Broadcast player left message
            socketio.emit('player_left', {"player_id": player_id}, room=room_id)
            
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Failed to remove AI player"})
    
    @app.route('/api/game-records/<room_id>')
    def get_game_records(room_id):
        """Get room game records API"""
        records = game_record_manager.load_room_records(room_id)
        return jsonify(records)

    @app.route('/api/player-stats/<player_name>')
    def get_player_stats(player_name):
        """Get player statistics API"""
        stats = game_record_manager.get_player_stats(player_name)
        return jsonify(stats)
    
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 error"""
        return render_template('404.html'), 404