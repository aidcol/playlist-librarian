import os
from typing import Optional
from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when configuration is invalid or missing required values."""
    pass


class Config:
    """Configuration manager for the Spotify MCP server.

    Loads environment variables from .env file and validates required Spotify
    credentials. Provides clean access to configuration values with proper
    error handling.
    """

    def __init__(self, dotenv_path: Optional[str] = None):
        """Initialize configuration.

        Args:
            dotenv_path: Optional path to .env file. If not provided, will look
                for .env in current directory.
        """
        # Load environment variables from .env file
        if dotenv_path:
            load_dotenv(dotenv_path)
        else:
            load_dotenv()

        # Load and validate Spotify credentials
        self._load_spotify_credentials()

    def _load_spotify_credentials(self) -> None:
        """Load and validate Spotify credentials from environment variables."""
        missing_vars = []

        # Load SPOTIFY_CLIENT_ID
        client_id = os.getenv('SPOTIFY_CLIENT_ID', '').strip()
        if not client_id:
            missing_vars.append('SPOTIFY_CLIENT_ID')

        # Load SPOTIFY_CLIENT_SECRET
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '').strip()
        if not client_secret:
            missing_vars.append('SPOTIFY_CLIENT_SECRET')

        # Raise error if any required variables are missing
        if missing_vars:
            missing_vars_str = ', '.join(missing_vars)
            raise ConfigError(
                f"Missing required environment variables: {missing_vars_str}. "
                f"Please set these variables in your environment or .env file."
            )

        # Store validated credentials
        self._spotify_client_id = client_id
        self._spotify_client_secret = client_secret

    @property
    def spotify_client_id(self) -> str:
        """Get the Spotify client ID."""
        return self._spotify_client_id

    @property
    def spotify_client_secret(self) -> str:
        """Get the Spotify client secret."""
        return self._spotify_client_secret
