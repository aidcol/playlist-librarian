from src.config import Config, ConfigError
from src.spotify_client import SpotifyClientManager, SpotifyClientError, SpotifyException

def main():
    print("Hello from playlist-librarian!")

    try:
        config = Config()
    except ConfigError as e:
        print(e)

    client_manager = SpotifyClientManager(config.spotify_client_id,
                                          config.spotify_client_secret)
    
    if not client_manager.authenticate():
        exit(1)
    
    if not client_manager.test_connection():
        exit(1)

if __name__ == "__main__":
    main()
