"""
Blackjack Game Main Entry Point
"""
import os
from app import create_app, socketio, start_display_url_thread
from config import PORT

# Ensure game records directory exists
def ensure_game_records_dir():
    """Ensure game records directory exists"""
    records_dir = "game_records"
    if not os.path.exists(records_dir):
        os.makedirs(records_dir)
        print(f"Created game records directory: {records_dir}")

# Create Flask application
def main():
    # Create game records directory
    ensure_game_records_dir()
    
    # Create Flask application
    app = create_app()
    
    # Create thread to display URL
    start_display_url_thread(app)
    
    # Start Flask application
    print(f"Starting Blackjack Game on port {PORT}...")
    socketio.run(app, debug=True, host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    main()