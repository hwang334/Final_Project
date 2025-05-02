"""
Ngrok Manager: Handle creation and management of ngrok tunnels
"""
import time
import threading
import socket
from pyngrok import ngrok, conf
from flask import current_app


def setup_ngrok(app, use_ngrok=True, auth_token=None, port=5001):
    """
    Setup ngrok tunnel
    
    Args:
        app (Flask): Flask application instance
        use_ngrok (bool, optional): Whether to enable ngrok. Default True.
        auth_token (str, optional): Ngrok authentication token. Default None.
        port (int, optional): Application port. Default 5001.
    """
    # First set ngrok as unavailable
    app.config["NGROK_AVAILABLE"] = False
    app.config["BASE_URL"] = f"http://localhost:{port}"
    
    # Create a thread to handle ngrok setup
    def ngrok_setup_thread():
        if not use_ngrok:
            return
            
        # Wait 5 seconds to let application start
        time.sleep(5)
        
        try:
            # Check if there are existing ngrok tunnels
            existing_tunnels = ngrok.get_tunnels()
            
            if existing_tunnels:
                # If tunnels exist, use the first tunnel's URL
                public_url = existing_tunnels[0].public_url
                print(f" * Using existing ngrok tunnel")
                print(f" * Public URL: {public_url}")
                print(f" * Share this link with your friends to join the game from any network")
                
                # Store public URL as application variable
                app.config["BASE_URL"] = public_url
                app.config["NGROK_AVAILABLE"] = True
                return
            
            # If no existing tunnels, setup new tunnel
            # Use PyngrokConfig object to set configuration
            if auth_token:
                ngrok_config = conf.PyngrokConfig(
                    auth_token=auth_token,
                    region="us"  # Can adjust based on your location
                )
                # Create ngrok tunnel
                public_url = ngrok.connect(port, pyngrok_config=ngrok_config).public_url
            else:
                # Use free tunnel without authentication token
                public_url = ngrok.connect(port).public_url
                
            print(f" * ngrok tunnel started")
            print(f" * Public URL: {public_url}")
            print(f" * Share this link with your friends to join the game from any network")
            
            # Store public URL as application variable
            app.config["BASE_URL"] = public_url
            app.config["NGROK_AVAILABLE"] = True
            
        except Exception as e:
            print(f" * ngrok startup failed: {e}")
            print(" * Trying to find existing tunnels...")
            
            try:
                # Try to get existing tunnels again
                existing_tunnels = ngrok.get_tunnels()
                if existing_tunnels:
                    public_url = existing_tunnels[0].public_url
                    print(f" * Found existing ngrok tunnel")
                    print(f" * Public URL: {public_url}")
                    app.config["BASE_URL"] = public_url
                    app.config["NGROK_AVAILABLE"] = True
                    return
            except:
                pass
            
            print(" * Could not find valid ngrok tunnel")
            print(" * Application will only be accessible on local network")
            
            # Get local IP as backup
            local_ip = get_local_ip()
            app.config["BASE_URL"] = f"http://{local_ip}:{port}"
    
    # Start ngrok setup thread
    ngrok_thread = threading.Thread(target=ngrok_setup_thread)
    ngrok_thread.daemon = True
    ngrok_thread.start()


def get_local_ip():
    """
    Get local IP address
    
    Returns:
        str: Local IP address
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"


def display_url(app, port):
    """
    Display application URL
    
    Args:
        app (Flask): Flask application instance
        port (int): Application port
    """
    # Wait 10 seconds for ngrok setup to complete
    time.sleep(10)
    print("\n===== Application Started =====")
    print(f" * Local URL: http://localhost:{port}")
    print(f" * LAN URL: {app.config.get('BASE_URL', 'http://localhost:'+str(port))}")
    if app.config.get("NGROK_AVAILABLE", False):
        print(f" * Public URL: {app.config.get('BASE_URL')}")
        print(" * You can share the public URL with friends to let them join the game from any network")
    else:
        print(" * ngrok tunnel not started, can only access within local network")