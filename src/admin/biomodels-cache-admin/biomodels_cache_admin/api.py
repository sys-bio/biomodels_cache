"""
BioModels API client for fetching model data.
"""
import requests
from typing import Dict, List, Any, Optional
from .cache import CacheManager

class BioModelsAPI:
    """Client for interacting with the BioModels API."""
    
    def __init__(self, cache_dir: str = "cache"):
        """Initialize the API client."""
        self.base_url = "https://www.ebi.ac.uk/biomodels"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.cache_manager = CacheManager(cache_dir)
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific model.
        If the model is not in cache, it will be fetched and saved to cache.
        
        Args:
            model_id: Model ID (e.g., 'BIOMD0000000001')
            
        Returns:
            Model metadata dictionary if found, None otherwise
        """
        # Check cache first
        cached_model = self.cache_manager.get_model(model_id)
        if cached_model:
            print(f"Model {model_id} found in cache")
            return cached_model
        
        # Model not in cache, fetch from API
        url = f"{self.base_url}/{model_id}"
        print(f"Requesting model from: {url}")
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 404:
            return None
        response.raise_for_status()
        
        try:
            model = response.json()
            # Save to cache
            self.cache_manager.cache[model_id] = model
            self.cache_manager._save_cache()
            print(f"Model {model_id} saved to cache")
            return model
        except Exception as e:
            print(f"Error parsing JSON: {str(e)}")
            return None
            
    def download_model(self, model_id: str, filepath: str) -> bool:
        """
        Download a model file.
        
        Args:
            model_id: Model ID (e.g., 'BIOMD0000000001')
            filepath: Path to save the model file
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            download_url = f"{self.base_url}/models/{model_id}/download"
            print(f"Downloading model from: {download_url}")
            
            response = requests.get(download_url, headers=self.headers)
            response.raise_for_status()
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            return True
            
        except Exception as e:
            print(f"Error downloading model {model_id}: {str(e)}")
            return False

    def search_cached_models(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search through cached models by content (name, title, synopsis, etc.).
        
        Args:
            search_term: Term to search for in model content
            
        Returns:
            List of matching model metadata dictionaries
        """
        return self.cache_manager.search_models(search_term) 