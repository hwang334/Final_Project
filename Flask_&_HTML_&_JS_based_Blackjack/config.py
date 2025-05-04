"""
Configuration File: Store application global configuration items
"""
import datetime

# Flask application configuration
SECRET_KEY = "blackjack_secret_key"
WTF_CSRF_ENABLED = False
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=365)
SESSION_TYPE = 'filesystem'

# ngrok configuration
USE_NGROK = True  # Set to False to disable ngrok
NGROK_AUTH_TOKEN = "2wMtLtJ7pnsTamBplMoATDyUOPA_6W4Qhim6RBMow9hyZGLSr"
PORT = 5001  # Use port 5001 to avoid conflict with AirPlay

# Game configuration
MAX_PLAYERS_PER_ROOM = 5