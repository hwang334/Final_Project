"""
Events Module: Handle all Socket.IO events
"""
import uuid
import time
from flask import request, after_this_request
from flask_socketio import emit, join_room, leave_room

from models import game_rooms, player_sessions, ai_player_manager

def handle_game_update_after_emit(game_room):
    """Handle operations after game update event is sent"""
    from app import socketio
    
    # Delay a bit to let client update UI
    socketio.sleep(1)
    
    print(f"Processing game update event - room state: {game_room.game_state}")
    
    # Handle AI decisions in different game states
    if game_room.game_state == "betting":
        # Handle AI players in betting phase
        ai_players_betting = [p for p_id, p in game_room.players.items() 
                             if p.is_ai and p.state == "betting"]
        
        print(f"Betting phase - AI players that need to bet: {len(ai_players_betting)}")
        
        for ai_player in ai_players_betting:
            print(f"AI player {ai_player.name} starts betting...")
            # Directly call betting decision and ensure broadcast update
            result = ai_player_manager.ai_betting_decision(game_room, ai_player)
            
            # No matter the result, send update
            socketio.emit('game_update', game_room.to_dict(), room=game_room.room_id)
            socketio.sleep(0.5)  # Short delay, avoid continuous operations
    
    elif game_room.game_state == "playing":
        # Handle AI players in game phase
        if game_room.current_player_index < len(game_room.player_order):
            current_player_id = game_room.player_order[game_room.current_player_index]
            current_player = game_room.players.get(current_player_id)
            
            # Check if current player is AI that needs to act
            if current_player and current_player.is_ai and current_player.state == "playing":
                print(f"Current acting player is AI: {current_player.name}")
                
                # Record current time for detecting stuck
                start_time = time.time()
                
                # Ensure current player is AI that needs to act
                result = ai_player_manager.ai_playing_decision(game_room, current_player)
                
                # No matter the result, send update
                socketio.emit('game_update', game_room.to_dict(), room=game_room.room_id)
                
                # Check if execution was successful, force action if failed
                if not result and current_player.state == "playing":
                    print(f"AI {current_player.name} action failed, forcing action")
                    if ai_player_manager.force_ai_action(game_room):
                        socketio.emit('game_update', game_room.to_dict(), room=game_room.room_id)
                
                # Wait for AI player to complete action
                socketio.sleep(0.5)
                
                # Check if timeout, consider stuck after 3 seconds
                if time.time() - start_time > 3:
                    print(f"AI action taking too long, possibly stuck, forcing action")
                    if ai_player_manager.force_ai_action(game_room):
                        socketio.emit('game_update', game_room.to_dict(), room=game_room.room_id)
                
                # Check if game state changed (if AI changed state, may need to handle next AI player)
                if game_room.game_state == "playing":
                    # Recursively call again, handle next possible AI player
                    socketio.sleep(0.5)  # Short delay
                    handle_game_update_after_emit(game_room)
            else:
                print(f"Current player is not AI or doesn't need to act")
    
    # Other game state handling...
    elif game_room.game_state == "waiting":
        # Handle AI players in waiting state
        ai_player_manager.handle_ai_turns(game_room)

def register_events(socketio):
    """
    Register all Socket.IO event handlers
    
    Args:
        socketio (SocketIO): SocketIO instance
    """
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection event"""
        print(f"Client connected: {request.sid}")
        # Check if previously connected player (can use cookie or sessionID)
        session_id = request.cookies.get('session_id')
        if not session_id:
            # Try to get from query parameters
            session_id = request.args.get('session_id')
            
        if session_id in player_sessions:
            # Restore previous player ID
            old_player_id = player_sessions[session_id]
            # Update to new socket ID
            player_sessions[session_id] = request.sid
            
            # Traverse all rooms, update player ID
            for room in game_rooms.values():
                if old_player_id in room.players:
                    player = room.players[old_player_id]
                    # Delete old ID
                    room.players.pop(old_player_id)
                    # Use new ID
                    player.player_id = request.sid
                    room.players[request.sid] = player
                    
                    # Update player order
                    if old_player_id in room.player_order:
                        idx = room.player_order.index(old_player_id)
                        room.player_order[idx] = request.sid

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection event"""
        player_id = request.sid
        print(f"Client disconnected: {player_id}")
        
        # Get session ID
        session_id = request.cookies.get('session_id') or request.args.get('session_id')
        
        # Find player's rooms
        for room_id, game_room in list(game_rooms.items()):
            if player_id in game_room.players:
                player = game_room.players[player_id]
                
                # Mark player as disconnected
                player.is_disconnected = True
                
                # If game is in progress and it's the player's turn, automatically stand
                if game_room.game_state == "playing" and game_room.current_player_index < len(game_room.player_order):
                    current_player_id = game_room.player_order[game_room.current_player_index]
                    if current_player_id == player_id and player.state == "playing":
                        # Automatically stand
                        game_room.player_stand(player_id)
                
                # Broadcast player status update
                emit('player_status_update', {
                    "player_id": player_id,
                    "player_state": "disconnected"
                }, room=room_id)
                
                # Broadcast updated game state
                emit('game_update', game_room.to_dict(), room=room_id)
                
                # Handle AI players
                socketio.sleep(1)
                handle_game_update_after_emit(game_room)
                
                # If room is empty, delete room
                # Note: We don't immediately remove disconnected human players to give them a chance to reconnect
                remaining_players = [p for p_id, p in game_room.players.items() 
                                   if p_id != player_id or p.is_ai]
                
                if not remaining_players:
                    del game_rooms[room_id]
                    print(f"Deleted empty room: {room_id}")
                    # Can add additional cleanup logic here, like clearing related session data
                    if hasattr(game_room, 'session_states'):
                        game_room.session_states.clear()
                
                break
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """Handle player joining room event"""
        room_id = data.get('room_id')
        player_name = data.get('player_name', f"Player{request.sid[:4]}")
        
        if room_id not in game_rooms:
            emit('error', {"message": "Room does not exist"})
            return
        
        # Create or get session ID
        session_id = request.cookies.get('session_id')
        if not session_id:
            # Try to get from query parameters
            session_id = request.args.get('session_id')
            
        if not session_id:
            session_id = str(uuid.uuid4())
            # Set cookie in response
            @after_this_request
            def set_cookie(response):
                response.set_cookie('session_id', session_id)
                return response
            
            # Tell client to store session ID
            emit('set_session_id', {"session_id": session_id})
        
        # Record session ID to player ID mapping
        player_sessions[session_id] = request.sid
        
        # Check if player already in room
        player_exists = False
        for player_id, player in game_rooms[room_id].players.items():
            if player.name == player_name:
                player_exists = True
                # If player exists but ID different, it's same player with different connection
                if player_id != request.sid:
                    # Update player ID
                    player.player_id = request.sid
                    game_rooms[room_id].players[request.sid] = player
                    game_rooms[room_id].players.pop(player_id)
                    
                    # Update player order
                    if player_id in game_rooms[room_id].player_order:
                        idx = game_rooms[room_id].player_order.index(player_id)
                        game_rooms[room_id].player_order[idx] = request.sid
                
                # Reset disconnected state
                player.is_disconnected = False
                break
        
        # If player doesn't exist, create new player
        if not player_exists:
            # Create new player
            from models.player import Player
            player_id = request.sid
            player = Player(player_id, player_name)
            
            # Add player to room
            game_room = game_rooms[room_id]
            if not game_room.add_player(player):
                emit('error', {"message": "Room is full"})
                return
        
        # Join Socket.IO room
        join_room(room_id)
        
        # Broadcast new player joined message (only when new player)
        if not player_exists:
            emit('player_joined', {"player": game_rooms[room_id].players[request.sid].to_dict()}, room=room_id)
        
        # Send complete room info to new player
        emit('room_data', game_rooms[room_id].to_dict())
        
        # Add code: Handle AI players
        # Delay a bit to let client update UI
        socketio.sleep(1)
        ai_player_manager.handle_ai_turns(game_rooms[room_id])
    
    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Handle player leaving room event"""
        room_id = data.get('room_id')
        
        if room_id not in game_rooms:
            return
        
        player_id = request.sid
        game_room = game_rooms[room_id]
        
        # Remove player from room
        if game_room.remove_player(player_id):
            # Leave Socket.IO room
            leave_room(room_id)
            
            # Broadcast player left message
            emit('player_left', {"player_id": player_id}, room=room_id)
            
            # If room is empty, delete room
            if len(game_room.players) == 0:
                del game_rooms[room_id]
                print(f"Deleted empty room: {room_id}")
                return
            
            # Check if player leaving affects game
            game_room.check_player_left(player_id)
            
            # Broadcast updated game state
            emit('game_update', game_room.to_dict(), room=room_id)
            
            # Handle AI players
            socketio.sleep(1)
            handle_game_update_after_emit(game_room)
    
    @socketio.on('player_ready')
    def handle_player_ready(data):
        """Handle player ready event"""
        room_id = data.get('room_id')
        
        if room_id not in game_rooms:
            emit('error', {"message": "Room does not exist"})
            return
        
        player_id = request.sid
        game_room = game_rooms[room_id]
        
        if player_id not in game_room.players:
            emit('error', {"message": "Player is not in the room"})
            return
        
        player = game_room.players[player_id]
        
        # Allow player to get ready even with zero funds
        # If player went All-in last round, determine funds in next round
        
        # Toggle ready state
        if player.state == "waiting":
            player.state = "ready"
        elif player.state == "ready":
            player.state = "waiting"
        elif player.state == "spectating" and player.money > 0:
            # If in spectating state but has funds, can ready
            player.state = "ready"
        
        # Save player state to session
        session_id = request.cookies.get('session_id') or request.args.get('session_id')
        if session_id:
            game_room.store_player_state_to_session(session_id, player.state)
        
        # Broadcast player ready status
        emit('player_status_update', {
            "player_id": player_id,
            "player_state": player.state
        }, room=room_id)
        
        # Check if all players with funds are ready
        # Note: We now allow players to ready even with zero funds, but they'll be set to spectating in next round
        active_players = [p for p in game_room.players.values() if p.money > 0 or p.current_bet > 0]
        ready_players = [p for p in active_players if p.state == "ready"]
        
        # If all active players are ready, start betting phase
        if len(active_players) > 0 and len(ready_players) == len(active_players):
            if game_room.start_betting():  # Only broadcast game update if start_betting is successful
                emit('game_update', game_room.to_dict(), room=room_id)
                # Handle AI players
                handle_game_update_after_emit(game_room)
    
    @socketio.on('place_bet')
    def handle_place_bet(data):
        """Handle player bet event"""
        room_id = data.get('room_id')
        bet_amount = data.get('bet_amount', 0)
        
        if room_id not in game_rooms:
            emit('error', {"message": "Room does not exist"})
            return
        
        player_id = request.sid
        game_room = game_rooms[room_id]
        
        # Check if bet amount is all funds (All-in)
        player = game_room.players.get(player_id)
        if player and bet_amount == player.money:
            print(f"Player {player.name} is going All-in!")
        
        # Player bets
        if game_room.place_bet(player_id, bet_amount):
            # Broadcast game state
            emit('game_update', game_room.to_dict(), room=room_id)
            
            # Check if any AI players need to bet
            ai_players_betting = [p for p_id, p in game_room.players.items() 
                                 if p.is_ai and p.state == "betting"]
            
            if ai_players_betting:
                # Delay a bit to let client update UI
                socketio.sleep(1)
                
                # Handle all AI players that need to bet
                for ai_player in ai_players_betting:
                    ai_player_manager.ai_betting_decision(game_room, ai_player)
            else:
                # No AI players need to bet, normal processing
                handle_game_update_after_emit(game_room)
    
    @socketio.on('hit')
    def handle_hit(data):
        """Handle player hit event"""
        room_id = data.get('room_id')
        
        if room_id not in game_rooms:
            emit('error', {"message": "Room does not exist"})
            return
        
        player_id = request.sid
        game_room = game_rooms[room_id]
        
        # Player hits
        if game_room.player_hit(player_id):
            # Broadcast game state to all players in room
            emit('game_update', game_room.to_dict(), room=room_id)
            # Handle AI players
            handle_game_update_after_emit(game_room)
    
    @socketio.on('stand')
    def handle_stand(data):
        """Handle player stand event"""
        room_id = data.get('room_id')
        
        if room_id not in game_rooms:
            emit('error', {"message": "Room does not exist"})
            return
        
        player_id = request.sid
        game_room = game_rooms[room_id]
        
        # Player stands
        if game_room.player_stand(player_id):
            # Broadcast game state to all players in room
            emit('game_update', game_room.to_dict(), room=room_id)
            # Handle AI players
            handle_game_update_after_emit(game_room)
    
    @socketio.on('double_down')
    def handle_double_down(data):
        """Handle player double down event"""
        room_id = data.get('room_id')
        
        if room_id not in game_rooms:
            emit('error', {"message": "Room does not exist"})
            return
        
        player_id = request.sid
        game_room = game_rooms[room_id]
        
        # Player double down
        if game_room.player_double_down(player_id):
            # Broadcast game state to all players in room
            emit('game_update', game_room.to_dict(), room=room_id)
            # Handle AI players
            handle_game_update_after_emit(game_room)
    
    @socketio.on('next_round')
    def handle_next_round(data):
        """Handle next round event"""
        room_id = data.get('room_id')
        
        if room_id not in game_rooms:
            emit('error', {"message": "Room does not exist"})
            return
        
        game_room = game_rooms[room_id]
        
        # Confirm game is over
        if game_room.game_state != "game_over":
            emit('error', {"message": "The game is not over yet"})
            return
        
        # Prepare new round
        if game_room.prepare_new_round():
            # Broadcast game state
            emit('game_update', game_room.to_dict(), room=room_id)
            # Send additional notification
            emit('notification', {"message": "A new round is ready, please click the ready button"}, room=room_id)
            
            # Add code: Handle AI players
            # Delay a bit to let client update UI
            socketio.sleep(1)
            ai_player_manager.handle_ai_turns(game_room)
    
    @socketio.on('game_update')
    def handle_game_update(data):
        """Receive game state update event"""
        print("Received game state update event")
        # Handle AI players
        room_id = data.get('room_id')
        if room_id in game_rooms:
            handle_game_update_after_emit(game_rooms[room_id])