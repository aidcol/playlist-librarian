import logging
from typing import Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException


class SpotifyClientError(Exception):
    """Exception raised for Spotify client errors."""
    pass


class SpotifyClientManager:
    """Spotify client wrapper that handles authentication.

    Uses spotipy with Client Credentials authentication flow for
    server-to-server communication. Handles authentication errors gracefully
    and provides connection testing.
    """

    def __init__(self, client_id: str, client_secret: str):
        """Initialize the Spotify client manager.

        Args:
            client_id: Spotify application client ID
            client_secret: Spotify application client secret

        Raises:
            SpotifyClientError: If credentials are invalid or missing
        """
        if not client_id or not isinstance(client_id, str):
            raise SpotifyClientError("client_id must be a non-empty string")
        if not client_secret or not isinstance(client_secret, str):
            raise SpotifyClientError("client_secret must be a non-empty string")

        self._client_id = client_id
        self._client_secret = client_secret
        self._spotify_client: Optional[spotipy.Spotify] = None

        # Set up logging
        self.logger = logging.getLogger(__name__)

    def authenticate(self) -> bool:
        """Authenticate with Spotify using Client Credentials flow.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Create client credentials manager
            auth_manager = SpotifyClientCredentials(
                client_id=self._client_id,
                client_secret=self._client_secret
            )

            # Create Spotify client with authentication
            self._spotify_client = spotipy.Spotify(auth_manager=auth_manager)

            self.logger.info("Successfully authenticated with Spotify")
            return True
        except SpotifyException as e:
            self.logger.error(f"Spotify authentication failed: {e}")
            self._spotify_client = None
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during authentication: {e}")
            self._spotify_client = None
            return False

    def get_client(self) -> spotipy.Spotify:
        """Get the authenticated Spotify client.

        Returns:
            spotipy.Spotify: The authenticated Spotify client

        Raises:
            SpotifyClientError: If not authenticated or client is not available
        """
        if self._spotify_client is None:
            raise SpotifyClientError(
                "Spotify client is not authenticated. Call authenticate() first."
            )
        return self._spotify_client

    def test_connection(self) -> bool:
        """Test the connection to Spotify API.

        Makes a simple API call to verify the connection is working.

        Returns:
            bool: True if connection test successful, False otherwise

        Raises:
            SpotifyClientError: If not authenticated
        """
        if self._spotify_client is None:
            raise SpotifyClientError(
                "Spotify client is not authenticated. Call authenticate() first."
            )

        try:
            # Make a simple API call to test connection
            self._spotify_client.search(q="test", type="track", limit=1)
            self.logger.info("Spotify connection test successful")
            return True
        except SpotifyException as e:
            self.logger.error(f"Spotify connection test failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during connection test: {e}")
            return False
