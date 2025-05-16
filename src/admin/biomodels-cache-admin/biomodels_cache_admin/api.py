"""
BioModels API client for fetching model data.
"""
import requests
from typing import Dict, List, Any, Optional

class BioModelsAPI:
    """Client for interacting with the BioModels API."""
    
    def __init__(self):
        """Initialize the API client."""
        self.base_url = "https://www.ebi.ac.uk/biomodels"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Get all models from BioModels.
        
        Returns:
            List of model metadata dictionaries
        """
        # Use the v1 API endpoint for models
        url = f"{self.base_url}/models"
        print(f"Requesting models from: {url}")
        
        response = requests.get(url, headers=self.headers)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response text (first 500 chars): {response.text[:500]}")
        
        response.raise_for_status()
        try:
            data = response.json()
            # The v1 API returns a list of models directly
            return data
        except Exception as e:
            print(f"Error parsing JSON: {str(e)}")
            return []
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific model.
        
        Args:
            model_id: Model ID (e.g., 'BIOMD0000000001')
            
        Returns:
            Model metadata dictionary if found, None otherwise
        """
        # Use the v1 API endpoint for specific model
        url = f"{self.base_url}/models/{model_id}"
        print(f"Requesting model from: {url}")
        
        response = requests.get(url, headers=self.headers)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response text (first 500 chars): {response.text[:500]}")
        
        if response.status_code == 404:
            return None
        response.raise_for_status()
        try:
            return response.json()
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