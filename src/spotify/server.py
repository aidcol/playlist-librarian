import logging
from typing import List
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .config import Config, ConfigError
from .spotify_client import SpotifyClientManager, SpotifyClientError
from ..utils import extract_playlist_id, SpotifyURLError


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Spotify MCP Server")

# Global Spotify client manager
spotify_manager: SpotifyClientManager = None


class PlaylistRequest(BaseModel):
    playlist_url_or_id: str = Field(description="Spotify playlist URL or ID")


class TrackDetailsRequest(BaseModel):
    track_ids: List[str] = Field(description="List of Spotify track IDs")


@mcp.tool()
def fetch_playlist(request: PlaylistRequest) -> dict:
    """Fetch track URIs from a Spotify playlist"""
    logger.info(f"Fetching playlist: {request.playlist_url_or_id}")
    
    if spotify_manager is None:
        raise SpotifyClientError("Spotify client not initialized")
    
    try:
        # Extract playlist ID from URL or validate raw ID
        playlist_id = extract_playlist_id(request.playlist_url_or_id)
        logger.info(f"Extracted playlist ID: {playlist_id}")
        
    except SpotifyURLError as e:
        logger.error(f"Invalid playlist URL or ID: {e}")
        raise ValueError(str(e))
    
    try:
        # Get authenticated Spotify client
        spotify_client = spotify_manager.get_client()
        
        # Fetch playlist tracks from Spotify API
        playlist_tracks = spotify_client.playlist_tracks(playlist_id)
        
        # Extract track URIs
        track_uris = []
        for item in playlist_tracks['items']:
            if item['track'] is not None and item['track']['uri']:
                track_uris.append(item['track']['uri'])
        
        return {
            "track_uris": track_uris
        }
        
    except SpotifyClientError as e:
        logger.error(f"Spotify client error: {e}")
        raise ValueError(str(e))
    except Exception as e:
        logger.error(f"Error fetching playlist: {e}")
        raise ValueError(f"Failed to fetch playlist: {str(e)}")


@mcp.tool()
def get_track_details(request: TrackDetailsRequest) -> dict:
    """Get detailed metadata for specific tracks"""
    logger.info(f"Getting track details for {len(request.track_ids)} tracks: {request.track_ids}")
    
    if spotify_manager is None:
        raise SpotifyClientError("Spotify client not initialized")
    
    # Validate input
    if not request.track_ids:
        raise ValueError("track_ids cannot be empty")
    
    for i, track_id in enumerate(request.track_ids):
        if not track_id.strip():
            raise ValueError(f"track_ids[{i}] cannot be empty")
    
    try:
        # Get authenticated Spotify client
        spotify_client = spotify_manager.get_client()
        
        # Fetch track details from Spotify API
        tracks_data = spotify_client.tracks(request.track_ids)
        
        # Extract unique artist IDs to fetch detailed artist information
        artist_ids = set()
        for track in tracks_data['tracks']:
            if track is not None:
                for artist in track['artists']:
                    artist_ids.add(artist['id'])
        
        # Extract unique album IDs to fetch detailed album information
        album_ids = set()
        for track in tracks_data['tracks']:
            if track is not None and track['album'] and track['album']['id']:
                album_ids.add(track['album']['id'])
        
        # Fetch detailed artist information
        artists_data = {}
        if artist_ids:
            artists_response = spotify_client.artists(list(artist_ids))
            for artist in artists_response['artists']:
                if artist is not None:
                    # Extract artist image URL (largest image)
                    artist_image_url = None
                    if artist['images']:
                        artist_image_url = artist['images'][0]['url']
                    
                    artists_data[artist['id']] = {
                        "image_url": artist_image_url,
                        "genres": artist.get('genres', [])
                    }
        
        # Fetch detailed album information
        albums_data = {}
        if album_ids:
            albums_response = spotify_client.albums(list(album_ids))
            for album in albums_response['albums']:
                if album is not None:
                    albums_data[album['id']] = {
                        "label": album.get('label', ''),
                        "copyrights": album.get('copyrights', [])
                    }
        
        tracks = []
        for track in tracks_data['tracks']:
            if track is not None:
                # Extract album cover art URL (largest image)
                album_cover_url = None
                if track['album']['images']:
                    album_cover_url = track['album']['images'][0]['url']
                
                # Build artist list with detailed information
                artists = []
                for artist in track['artists']:
                    artist_details = {
                        "uri": artist['uri'],
                        "name": artist['name']
                    }
                    # Add detailed artist info if available
                    if artist['id'] in artists_data:
                        artist_details.update(artists_data[artist['id']])
                    artists.append(artist_details)
                
                # Build album details with additional information
                album_details = {
                    "uri": track['album']['uri'],
                    "name": track['album']['name'],
                    "album_type": track['album']['album_type'],
                    "cover_art_url": album_cover_url,
                    "release_date": track['album']['release_date'],
                    "release_date_precision": track['album']['release_date_precision']
                }
                # Add detailed album info if available
                if track['album']['id'] in albums_data:
                    album_details.update(albums_data[track['album']['id']])
                
                tracks.append({
                    "name": track['name'],
                    "duration_ms": track['duration_ms'],
                    "album": album_details,
                    "artists": artists
                })
        
        return {"tracks": tracks}
        
    except SpotifyClientError as e:
        logger.error(f"Spotify client error: {e}")
        raise ValueError(str(e))
    except Exception as e:
        logger.error(f"Error fetching track details: {e}")
        raise ValueError(f"Failed to fetch track details: {str(e)}")





def initialize_spotify_client():
    """Initialize the Spotify client manager."""
    global spotify_manager
    
    try:
        logger.info("Initializing Spotify client...")
        config = Config()
        
        spotify_manager = SpotifyClientManager(
            config.spotify_client_id,
            config.spotify_client_secret
        )
        
        if spotify_manager.authenticate():
            if spotify_manager.test_connection():
                logger.info("Spotify client initialized and tested successfully")
            else:
                logger.warning("Spotify client authenticated but connection test failed")
        else:
            logger.error("Failed to authenticate with Spotify")
            raise SpotifyClientError("Authentication failed")   
    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        raise
    except SpotifyClientError as e:
        logger.error(f"Spotify client error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error initializing Spotify client: {e}")
        raise


def main():
    """Main function to run the MCP server."""
    try:
        # Initialize Spotify client
        initialize_spotify_client()
        
        # Run the FastMCP server
        logger.info("Starting MCP server...")
        mcp.run()
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    main()
