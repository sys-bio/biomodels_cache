"""
BioModels API client for fetching model data.
"""
import requests  # type: ignore
import os
import json
from typing import Dict, List, Any, Optional
from .cache import CacheManager


def normalize_model(model: Dict[str, Any], requested_id: Optional[str] = None) -> Dict[str, Any]:
    """Normalize model data to a consistent format.
    
    Args:
        model: Dict[str, Any] - Raw model data from API or cache
        requested_id: Optional[str] - Model ID if not present in model data
        
    Returns:
        Dict[str, Any] - Normalized model data with consistent fields:
            - name: str - Model name
            - authors: List[str] - List of author names
            - url: str - Model URL
            - id: str - Model ID (for backward compatibility)
            - model_id: str - Model ID
            - title: str - Model title
            - synopsis: str - Model description
            - citation: str - Citation information
            - date: str - Publication date
            - journal: str - Journal name
            
    Raises:
        ValueError: If model_id is missing and not provided in requested_id
        RuntimeError: If model data structure is invalid
    """
    # If already normalized, just return
    if all(k in model for k in ["name", "authors", "model_id", "title", "synopsis", "date", "journal"]):
        return model
        
    try:
        # Flatten publication info if present
        publication = model.get("publication", {})
        authors = model.get("authors") or publication.get("authors") or []
        if isinstance(authors, list) and authors and isinstance(authors[0], dict):
            authors = [a.get("name", "") for a in authors]

        # Ensure we have a valid model_id
        model_id = model.get("id") or requested_id
        if not model_id:
            raise ValueError("Model ID is required")

        return {
            "name": model.get("name") or publication.get("title"),
            "authors": authors,
            "url": model.get("url") or publication.get("link"),
            "id": model_id,  # Add id field for backward compatibility
            "model_id": model_id,
            "title": model.get("title") or publication.get("title"),
            "synopsis": model.get("synopsis") or publication.get("synopsis"),
            "citation": model.get("citation"),
            "date": model.get("date") or publication.get("date") or publication.get("year"),
            "journal": model.get("journal") or publication.get("journal"),
        }
    except Exception as e:
        raise RuntimeError(f"Failed to normalize model data: {str(e)}")


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
        # Convert numeric ID to full ID if needed
        if model_id.isdigit():
            model_id = f"BIOMD{model_id.zfill(10)}"

        # Check cache first
        cached_model = self.cache_manager.get_model(model_id)
        if cached_model:
            print(f"Model {model_id} found in cache")
            return cached_model

        # Model not in cache, fetch from API
        url = f"{self.base_url}/{model_id}"
        print(f"Requesting model from: {url}")

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise e
        except requests.exceptions.RequestException as e:
            raise e

        try:
            model = response.json()
            normalized = normalize_model(model, requested_id=model_id)
            # Save normalized to cache using normalized model_id as key
            self.cache_manager.cache[normalized["model_id"]] = normalized
            self.cache_manager._save_cache()
            print(f"Model {model_id} saved to cache")
            return normalized
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
            download_url = f"{self.base_url}/model/download/{model_id}"
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

    def export_models_to_json(self, filepath: str, model_ids: List[str]) -> bool:
        """Export specified models to a JSON file.

        Args:
            filepath: str - Path where the JSON file will be saved
            model_ids: List[str] - List of model IDs to export

        Returns:
            bool: True if export was successful

        Raises:
            ValueError: If filepath is invalid or file cannot be written
            RuntimeError: If there's an error processing the models
        """
        try:
            # Get all models
            models_data = {}
            for model_id in model_ids:
                model = self.get_model(model_id)
                if model:
                    models_data[model_id] = model

            # Write to JSON file
            try:
                with open(filepath, 'w') as f:
                    json.dump(models_data, f, indent=2)
            except (IOError, OSError) as e:
                raise ValueError(f"Cannot write to file {filepath}: {str(e)}")

            return True
        except ValueError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Error exporting models: {str(e)}")

    def import_models_from_json(self, filepath: str) -> List[Dict[str, Any]]:
        """Import models from a JSON file.

        Args:
            filepath: str - Path to the JSON file to import from

        Returns:
            List[Dict[str, Any]]: List of imported models

        Raises:
            ValueError: If filepath is invalid or file cannot be read
            RuntimeError: If there's an error processing the models
        """
        try:
            try:
                with open(filepath, 'r') as f:
                    models_data = json.load(f)
            except (IOError, OSError) as e:
                raise ValueError(f"Cannot read file {filepath}: {str(e)}")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in file {filepath}: {str(e)}")

            # Convert to list of models
            models = []
            for model_id, model_data in models_data.items():
                try:
                    model_data['model_id'] = model_id
                    models.append(model_data)
                except Exception as e:
                    raise RuntimeError(f"Error processing model {model_id}: {str(e)}")

            return models
        except ValueError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Error importing models: {str(e)}")
