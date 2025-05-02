"""
Game Record Class: For saving and managing game records
"""
import os
import json
import time
from datetime import datetime

class GameRecord:
    """Game Record Management Class"""
    
    def __init__(self, data_dir="game_records"):
        """
        Initialize game record manager
        
        Args:
            data_dir (str): Directory to save records
        """
        self.data_dir = data_dir
        self.ensure_data_dir()
        
        # Cache all room records
        self.room_records = {}
    
    def ensure_data_dir(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_room_record_file(self, room_id):
        """Get room record file path"""
        return os.path.join(self.data_dir, f"room_{room_id}.json")
    
    def load_room_records(self, room_id):
        """
        Load room records
        
        Args:
            room_id (str): Room ID
            
        Returns:
            list: Room records list
        """
        if room_id in self.room_records:
            return self.room_records[room_id]
            
        record_file = self.get_room_record_file(room_id)
        if os.path.exists(record_file):
            try:
                with open(record_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                self.room_records[room_id] = records
                return records
            except Exception as e:
                print(f"Error loading room records: {e}")
                return []
        return []
    
    def save_room_records(self, room_id, records):
        """
        Save room records
        
        Args:
            room_id (str): Room ID
            records (list): Room records list
        """
        self.room_records[room_id] = records
        record_file = self.get_room_record_file(room_id)
        try:
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving room records: {e}")
    
    def add_game_record(self, room_id, game_room):
        """
        Add a game record
        
        Args:
            room_id (str): Room ID
            game_room (GameRoom): Game room object
        """
        # Load existing records
        records = self.load_room_records(room_id)
        
        # Create new record
        timestamp = time.time()
        date_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        # Check if dealer busted
        dealer_busted = game_room.dealer.score > 21
        dealer_blackjack = len(game_room.dealer.hand) == 2 and game_room.dealer.score == 21

        # Get player information
        players_info = {}
        for player_id, player in game_room.players.items():
            if player.state != "spectating":  # Only record participating players
                # Calculate win/loss correctly
                initial_money = player.money + player.current_bet  # Money before betting
                
                # Calculate win/loss based on player state
                if player.state == "busted":
                    # Busted, lose bet amount
                    win_loss = -player.current_bet
                elif player.state == "blackjack" and len(player.hand) == 2:
                    if dealer_blackjack:
                        # Dealer and player both have Blackjack, tie
                        win_loss = 0
                elif dealer_blackjack:
                    # Dealer has Blackjack but player doesn't, player loses
                    win_loss = -player.current_bet
                elif player.state == "blackjack" and game_room.dealer.state != "blackjack":
                    # Player has Blackjack and dealer doesn't, win 1.5x bet
                    win_loss = int(player.current_bet * 1.5)
                elif player.state == "five_dragon":
                    # Five Dragon, win 2x bet
                    win_loss = player.current_bet * 2
                elif game_room.dealer.state == "busted" and player.state != "busted":
                    # Dealer busted and player didn't, player wins
                    win_loss = player.current_bet
                elif player.score > game_room.dealer.score and player.state != "busted":
                    # Player score higher than dealer and player didn't bust, win
                    win_loss = player.current_bet
                elif player.score < game_room.dealer.score and game_room.dealer.state != "busted":
                    # Player score lower than dealer and dealer didn't bust, player wins
                    win_loss = player.current_bet
                else:
                    # Tie, return original bet
                    win_loss = 0
                
                players_info[player_id] = {
                    "name": player.name,
                    "initial_money": initial_money,
                    "final_money": player.money,
                    "bet": player.current_bet,
                    "win_loss": win_loss,
                    "state": player.state,
                    "score": player.score,
                    "is_ai": player.is_ai,
                    "ai_difficulty": player.ai_difficulty
                }
        
        # Create record object
        record = {
            "id": f"{room_id}_{timestamp}",
            "room_id": room_id,
            "room_name": game_room.room_name,
            "timestamp": timestamp,
            "date_time": date_time,
            "players": players_info,
            "dealer_score": game_room.dealer.score,
            "dealer_cards": [{"suit": card.suit, "value": card.value} for card in game_room.dealer.hand],
            "game_result": game_room.message
        }
        
        # Add to records list
        records.append(record)
        
        # Save records
        self.save_room_records(room_id, records)
        
        return record
    
    def get_player_stats(self, player_name):
        """
        Get player statistics
        
        Args:
            player_name (str): Player name
            
        Returns:
            dict: Player statistics
        """
        # Initialize statistics
        stats = {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "total_profit": 0,
            "blackjacks": 0,
            "busts": 0,
            "win_rate": 0
        }
        
        # Traverse all room records
        for room_id in os.listdir(self.data_dir):
            if room_id.startswith("room_") and room_id.endswith(".json"):
                room_records = self.load_room_records(room_id.replace("room_", "").replace(".json", ""))
                
                # Traverse all records in room
                for record in room_records:
                    # Find player in record
                    for player_id, player_info in record.get("players", {}).items():
                        if player_info.get("name") == player_name:
                            stats["games_played"] += 1
                            
                            win_loss = player_info.get("win_loss", 0)
                            if win_loss > 0:
                                stats["wins"] += 1
                            elif win_loss < 0:
                                stats["losses"] += 1
                                
                            stats["total_profit"] += win_loss
                            
                            if player_info.get("state") == "blackjack":
                                stats["blackjacks"] += 1
                            
                            if player_info.get("state") == "busted":
                                stats["busts"] += 1
        
        # Calculate win rate
        if stats["games_played"] > 0:
            stats["win_rate"] = (stats["wins"] / stats["games_played"]) * 100
            
        return stats

# Create global game record manager instance
game_record_manager = GameRecord()