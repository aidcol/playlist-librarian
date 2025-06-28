import re


class SpotifyURLError(Exception):
    """Exception raised when Spotify URL parsing fails."""
    pass


def extract_playlist_id(playlist_url_or_id: str) -> str:
    """Extract Spotify playlist ID from various URL formats.
    
    Supports the following formats:
    - https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
    - https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=...
    - spotify:playlist:37i9dQZF1DXcBWIGoYBM5M
    - Raw playlist ID: 37i9dQZF1DXcBWIGoYBM5M
    
    Args:
        playlist_url_or_id: Spotify playlist URL or ID in various formats
        
    Returns:
        str: The extracted playlist ID
        
    Raises:
        SpotifyURLError: If the URL format is not recognized or invalid
    """
    if not playlist_url_or_id or not isinstance(playlist_url_or_id, str):
        raise SpotifyURLError("playlist_url_or_id must be a non-empty string")
    
    # Clean the input
    url_or_id = playlist_url_or_id.strip()
    
    # Pattern for Spotify playlist ID (22 characters, alphanumeric)
    playlist_id_pattern = r'^[a-zA-Z0-9]{22}$'
    
    # Check if it's already a raw playlist ID
    if re.match(playlist_id_pattern, url_or_id):
        return url_or_id
    
    # Pattern for HTTPS URL format
    # https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
    # https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=...
    https_pattern = r'https://open\.spotify\.com/playlist/([a-zA-Z0-9]{22})'
    https_match = re.search(https_pattern, url_or_id)
    if https_match:
        return https_match.group(1)
    
    # Pattern for Spotify URI format
    # spotify:playlist:37i9dQZF1DXcBWIGoYBM5M
    uri_pattern = r'spotify:playlist:([a-zA-Z0-9]{22})'
    uri_match = re.search(uri_pattern, url_or_id)
    if uri_match:
        return uri_match.group(1)
    
    # If no pattern matches, raise an error
    raise SpotifyURLError(
        f"Invalid Spotify playlist URL or ID format: '{playlist_url_or_id}'. "
        f"Supported formats: HTTPS URL, Spotify URI, or raw playlist ID."
    )