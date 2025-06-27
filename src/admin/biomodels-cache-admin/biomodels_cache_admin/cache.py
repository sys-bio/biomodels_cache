"""
Cache management for BioModels data.
"""
import os
import json
import re
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime

class CacheManager:
    """Manages a local cache of BioModels data."""
    
    def __init__(self, cache_dir: str):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store cache files
        """
        if not cache_dir:
            raise ValueError("cache_dir must be provided")
            
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "biomodels_cache.json")
        self.cache: Dict[str, Dict[str, Any]] = {}
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize empty cache file if it doesn't exist
        if not os.path.exists(self.cache_file):
            self._save_cache()
        else:
            # Load existing cache if available
            try:
                with open(self.cache_file, "r") as f:
                    self.cache = json.load(f)
            except json.JSONDecodeError:
                # If file is invalid JSON, initialize empty cache
                self.cache = {}
                self._save_cache()
    
    def _save_cache(self) -> None:
        """Save the cache to disk."""
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=2)
    
    def update_cache(self, models: List[Dict[str, Any]], progress_callback: Optional[Callable[[int, int], None]] = None) -> None:
        """
        Update the cache with new model data.
        
        Args:
            models: List of model data to cache
            progress_callback: Optional callback for progress updates.
                             Signature: progress_callback(current: int, total: int) -> None
                             Example: Use tqdm.tqdm.write() or tqdm.update() for progress display
        """
        total = len(models)
        for idx, model in enumerate(models, 1):
            model_id = model["id"]
            if model_id not in self.cache:
                self.cache[model_id] = model
            if progress_callback:
                progress_callback(idx, total)
        # Save updated cache
        self._save_cache()
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a model from the cache.
        
        Args:
            model_id: Model ID (can be numeric or full ID)
            
        Returns:
            Model data if found, None otherwise
        """
        # Convert numeric ID to full ID if needed
        if model_id.isdigit():
            model_id = f"BIOMD{model_id.zfill(10)}"
            
        return self.cache.get(model_id)
    
    def search_models(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for models in the cache.
        
        Args:
            query: Search query string
            filters: Optional filters to apply. Available filters:
                - authors: List[str] - Filter by author names (case-insensitive)
                - journals: List[str] - Filter by journal names (case-insensitive)
                - dateRange: Dict[str, str] - Filter by date range with 'start' and 'end' keys (format: 'YYYY-MM-DD')
                - caseSensitive: bool - Whether to perform case-sensitive search (default: False)
                - useRegex: bool - Whether to treat query as regular expression (default: False)
            
        Returns:
            List of matching models
        """
        results = []
        
        # Extract search options from filters
        case_sensitive = filters.get("caseSensitive", False) if filters else False
        use_regex = filters.get("useRegex", False) if filters else False
        
        # Prepare search query
        if use_regex:
            try:
                search_pattern = re.compile(query, flags=0 if case_sensitive else re.IGNORECASE)
            except re.error as e:
                raise ValueError(f"Invalid regular expression: {e}")
        else:
            if not case_sensitive:
                query = query.lower()
        
        for model in self.cache.values():
            # Perform search based on configuration
            if use_regex:
                matches = (
                    search_pattern.search(model["name"]) or
                    search_pattern.search(model["title"]) or
                    search_pattern.search(model["synopsis"])
                )
            else:
                if case_sensitive:
                    matches = (
                        query in model["name"] or
                        query in model["title"] or
                        query in model["synopsis"]
                    )
                else:
                    matches = (
                        query in model["name"].lower() or
                        query in model["title"].lower() or
                        query in model["synopsis"].lower()
                    )
            
            if matches:
                # Apply filters if specified
                if filters:
                    if not self._apply_filters(model, filters):
                        continue
                        
                results.append(model)
        
        return results
    
    def _apply_filters(self, model: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Apply filters to a model."""
        # Author filter
        if "authors" in filters:
            authors = [a.lower() for a in model["authors"]]
            filter_authors = [a.lower() for a in filters["authors"]]
            if not any(a in authors for a in filter_authors):
                return False
                
        # Journal filter
        if "journals" in filters:
            model_journal = model["journal"].lower()
            filter_journals = [j.lower() for j in filters["journals"]]
            if model_journal not in filter_journals:
                return False
                
        # Date range filter
        if "dateRange" in filters:
            try:
                model_date = datetime.strptime(model["date"], "%Y-%m-%d")
                start_date = datetime.strptime(filters["dateRange"]["start"], "%Y-%m-%d")
                end_date = datetime.strptime(filters["dateRange"]["end"], "%Y-%m-%d")
                
                if not (start_date <= model_date <= end_date):
                    return False
            except ValueError as e:
                # If date parsing fails, raise ValueError
                raise ValueError(f"Invalid date format in filters: {str(e)}")
                
        return True
    
    def export_json(self, filepath: str) -> None:
        """
        Export the cache to a JSON file.
        
        Args:
            filepath: Path to save the JSON file
        """
        with open(filepath, "w") as f:
            json.dump(self.cache, f, indent=2)
    
    def import_json(self, filepath: str) -> None:
        """
        Import cache from a JSON file.
        
        Args:
            filepath: Path to the JSON file to import
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        with open(filepath, "r") as f:
            self.cache = json.load(f)
        
        # Save to cache file
        self._save_cache() 