#!/usr/bin/env python3
"""
Music Extraction and Search
Identifies songs mentioned in journal entries and links them on iTunes/Apple Music
"""

import re
import requests
from typing import List, Dict, Optional
from urllib.parse import quote


def extract_song_mentions(text: str) -> List[Dict[str, str]]:
    """
    Extract potential song and artist mentions from journal text.
    
    Looks for patterns like:
    - "Song Title" by Artist
    - listened to "Song"
    - Song: "Title"
    - listening to Artist - Song
    
    Args:
        text: Journal entry text
        
    Returns:
        List of dicts with 'song' and 'artist' keys
    """
    mentions = []
    
    # Pattern 1: "Song Title" by Artist Name
    pattern1 = r'"([^"]+)"\s+by\s+([^,.\n]+)'
    matches1 = re.findall(pattern1, text, re.IGNORECASE)
    for song, artist in matches1:
        mentions.append({
            'song': song.strip(),
            'artist': artist.strip(),
            'pattern': 'quoted_by'
        })
    
    # Pattern 2: listened to "Song Title"
    pattern2 = r'listened?\s+to\s+"([^"]+)"'
    matches2 = re.findall(pattern2, text, re.IGNORECASE)
    for song in matches2:
        mentions.append({
            'song': song.strip(),
            'artist': '',
            'pattern': 'listened_to'
        })
    
    # Pattern 3: Song: "Title" or song called "Title"
    pattern3 = r'song\s+(?:called\s+|:)?"([^"]+)"'
    matches3 = re.findall(pattern3, text, re.IGNORECASE)
    for song in matches3:
        mentions.append({
            'song': song.strip(),
            'artist': '',
            'pattern': 'song_colon'
        })
    
    # Pattern 4: Artist - Song Title (common in playlists)
    pattern4 = r'([A-Z][A-Za-z\s&]+)\s+-\s+([A-Z][^,.\n]+)'
    matches4 = re.findall(pattern4, text)
    for artist, song in matches4:
        # Filter out non-music patterns (e.g., dates, locations)
        if len(artist.split()) <= 4 and len(song.split()) <= 8:
            mentions.append({
                'song': song.strip(),
                'artist': artist.strip(),
                'pattern': 'dash_format'
            })
    
    # Pattern 5: Listening to Artist
    pattern5 = r'listening\s+to\s+([A-Z][A-Za-z\s&]+?)(?:\s+today|\s+now|\s+all|,|\.|$)'
    matches5 = re.findall(pattern5, text, re.IGNORECASE)
    for artist in matches5:
        if len(artist.split()) <= 4:
            mentions.append({
                'song': '',
                'artist': artist.strip(),
                'pattern': 'listening_artist'
            })
    
    return mentions


def search_itunes(query: str, limit: int = 5) -> List[Dict]:
    """
    Search iTunes/Apple Music for a song or artist.
    
    Args:
        query: Search query (song and/or artist)
        limit: Maximum number of results
        
    Returns:
        List of song results with metadata
    """
    base_url = "https://itunes.apple.com/search"
    
    params = {
        'term': query,
        'media': 'music',
        'entity': 'song',
        'limit': limit
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get('results', []):
            results.append({
                'song_name': item.get('trackName', ''),
                'artist_name': item.get('artistName', ''),
                'album_name': item.get('collectionName', ''),
                'artwork_url': item.get('artworkUrl100', '').replace('100x100', '300x300'),
                'preview_url': item.get('previewUrl', ''),
                'itunes_url': item.get('trackViewUrl', ''),
                'release_date': item.get('releaseDate', ''),
                'genre': item.get('primaryGenreName', ''),
                'duration_ms': item.get('trackTimeMillis', 0)
            })
        
        return results
    
    except requests.RequestException as e:
        print(f"iTunes search error: {e}")
        return []


def search_song_on_itunes(song: str, artist: str = '') -> Optional[Dict]:
    """
    Search for a specific song on iTunes, returning the best match.
    
    Args:
        song: Song title
        artist: Artist name (optional but improves accuracy)
        
    Returns:
        Dict with song metadata, or None if not found
    """
    # Build search query
    if artist and song:
        query = f"{song} {artist}"
    elif song:
        query = song
    elif artist:
        query = artist
    else:
        return None
    
    results = search_itunes(query, limit=1)
    
    if results:
        return results[0]
    
    return None


def extract_and_search_music(journal_entries: List[Dict[str, str]]) -> Dict[str, List[Dict]]:
    """
    Extract song mentions from journal entries and search for them on iTunes.
    
    Args:
        journal_entries: List of dicts with 'date' and 'text' keys
        
    Returns:
        Dict mapping song keys to lists of {metadata, dates mentioned}
    """
    all_mentions = []
    
    # Extract mentions from each entry
    for entry in journal_entries:
        mentions = extract_song_mentions(entry['text'])
        for mention in mentions:
            mention['date'] = entry['date']
            all_mentions.append(mention)
    
    # Group by song/artist combo
    song_map = {}
    for mention in all_mentions:
        key = f"{mention['song']}|{mention['artist']}".lower()
        
        if key not in song_map:
            song_map[key] = {
                'song': mention['song'],
                'artist': mention['artist'],
                'dates': [],
                'count': 0,
                'metadata': None
            }
        
        song_map[key]['dates'].append(mention['date'])
        song_map[key]['count'] += 1
    
    # Search iTunes for each unique song
    for key, data in song_map.items():
        if data['song'] or data['artist']:
            metadata = search_song_on_itunes(data['song'], data['artist'])
            if metadata:
                song_map[key]['metadata'] = metadata
    
    # Filter out songs we couldn't find on iTunes
    found_songs = {k: v for k, v in song_map.items() if v['metadata'] is not None}
    
    return found_songs


def format_duration(milliseconds: int) -> str:
    """Convert milliseconds to MM:SS format"""
    if not milliseconds:
        return "Unknown"
    
    seconds = milliseconds // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    
    return f"{minutes}:{seconds:02d}"


if __name__ == "__main__":
    # Test the extraction
    test_text = """
    Today I listened to "Everlong" by Foo Fighters on repeat. It reminded me of college.
    Also been listening to Radiohead a lot lately. The song: "Karma Police" hits different now.
    """
    
    mentions = extract_song_mentions(test_text)
    print("Extracted mentions:")
    for m in mentions:
        print(f"  - {m}")
    
    # Test iTunes search
    print("\nSearching iTunes:")
    result = search_song_on_itunes("Everlong", "Foo Fighters")
    if result:
        print(f"  Found: {result['song_name']} by {result['artist_name']}")
        print(f"  Link: {result['itunes_url']}")
