from src.config import Config, ConfigError

def main():
    print("Hello from playlist-librarian!")

    try:
        config = Config()
        print(f'{config.spotify_client_id=}')
        print(f'{config.spotify_client_secret=}')
    except ConfigError as e:
        print(e)


if __name__ == "__main__":
    main()
