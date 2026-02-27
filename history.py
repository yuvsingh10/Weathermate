"""Manage search history and favorite cities."""

import json
import os
from typing import List, Dict
from datetime import datetime

HISTORY_FILE = "search_history.json"
MAX_HISTORY = 10  # Maximum recent cities to remember


class SearchHistory:
    """Manage search history and favorites persistence."""
    
    def __init__(self):
        """Initialize search history from file."""
        self.history_data = self._load_history()
    
    def _load_history(self) -> Dict:
        """Load history from JSON file.
        
        Returns:
            Dictionary with 'recent' and 'favorites' keys
        """
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"recent": [], "favorites": []}
        return {"recent": [], "favorites": []}
    
    def _save_history(self) -> None:
        """Save history to JSON file."""
        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump(self.history_data, f, indent=2)
        except IOError as e:
            print(f"Failed to save history: {str(e)}")
    
    def add_recent(self, city: str) -> None:
        """Add city to recent searches.
        
        Args:
            city: City name to add
        """
        recent = self.history_data.get("recent", [])
        
        # Remove if already exists (to move to top)
        if city in recent:
            recent.remove(city)
        
        # Add to beginning
        recent.insert(0, city)
        
        # Keep only MAX_HISTORY items
        recent = recent[:MAX_HISTORY]
        self.history_data["recent"] = recent
        self._save_history()
    
    def get_recent(self) -> List[str]:
        """Get list of recent cities.
        
        Returns:
            List of recent city names (most recent first)
        """
        return self.history_data.get("recent", [])
    
    def add_favorite(self, city: str) -> None:
        """Add city to favorites.
        
        Args:
            city: City name to add to favorites
        """
        favorites = self.history_data.get("favorites", [])
        if city not in favorites:
            favorites.append(city)
            self.history_data["favorites"] = favorites
            self._save_history()
    
    def remove_favorite(self, city: str) -> None:
        """Remove city from favorites.
        
        Args:
            city: City name to remove from favorites
        """
        favorites = self.history_data.get("favorites", [])
        if city in favorites:
            favorites.remove(city)
            self.history_data["favorites"] = favorites
            self._save_history()
    
    def get_favorites(self) -> List[str]:
        """Get list of favorite cities.
        
        Returns:
            List of favorite city names
        """
        return self.history_data.get("favorites", [])
    
    def is_favorite(self, city: str) -> bool:
        """Check if city is in favorites.
        
        Args:
            city: City name to check
            
        Returns:
            True if city is a favorite, False otherwise
        """
        return city in self.history_data.get("favorites", [])
    
    def clear_history(self) -> None:
        """Clear all search history."""
        self.history_data = {"recent": [], "favorites": []}
        self._save_history()
