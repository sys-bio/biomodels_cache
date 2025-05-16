import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from biomodels_cache_admin.cache import CacheManager
import requests

@pytest.fixture
def temp_cache_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def sample_cache_data():
    return {
        "BIOMD0000000001": {
            "id": "BIOMD0000000001",
            "name": "Test Model 1",
            "title": "Test Title 1",
            "curators": ["Curator 1"],
            "publicationAuthors": ["Author 1"],
            "synopsis": "Test synopsis 1",
            "citation": "Test citation 1",
            "date": "2020-01-01",
            "journal": "Test Journal 1",
            "lastUpdated": "2023-01-01",
            "files": {
                "model.xml": "content1",
                "model.sbml": "content2"
            }
        },
        "BIOMD0000000002": {
            "id": "BIOMD0000000002",
            "name": "Test Model 2",
            "title": "Test Title 2",
            "curators": ["Curator 2"],
            "publicationAuthors": ["Author 2"],
            "synopsis": "Test synopsis 2",
            "citation": "Test citation 2",
            "date": "2021-01-01",
            "journal": "Test Journal 2",
            "lastUpdated": "2023-02-01",
            "files": {
                "model.xml": "content3",
                "model.sbml": "content4"
            }
        }
    }

@pytest.fixture
def mock_api_response():
    mock = MagicMock()
    mock.get_models.return_value = [
        {
            "id": "BIOMD0000000001",
            "name": "Test Model 1",
            "title": "Test Title 1",
            "curators": ["Curator 1"],
            "publicationAuthors": ["Author 1"],
            "synopsis": "Test synopsis 1",
            "citation": "Test citation 1",
            "date": "2020-01-01",
            "journal": "Test Journal 1",
            "lastUpdated": "2023-01-01",
            "files": {
                "model.xml": "content1",
                "model.sbml": "content2"
            }
        }
    ]
    return mock

def test_initialize_cache(temp_cache_dir):
    cache_manager = CacheManager(temp_cache_dir)
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    
    # Cache file should be created after first access
    cache_manager.cache = {}  # Force cache initialization
    assert os.path.exists(cache_file)
    assert cache_manager.cache == {}

def test_load_existing_cache(temp_cache_dir, sample_cache_data):
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    with open(cache_file, "w") as f:
        json.dump(sample_cache_data, f)
    
    cache_manager = CacheManager(temp_cache_dir)
    assert cache_manager.cache == sample_cache_data

def test_update_cache(temp_cache_dir, mock_api_response):
    # Mock the get_model method to return a serializable dictionary
    mock_api_response.get_model.return_value = {
        "id": "BIOMD0000000001",
        "name": "Test Model 1",
        "title": "Test Title 1",
        "curators": ["Curator 1"],
        "publicationAuthors": ["Author 1"],
        "synopsis": "Test synopsis 1",
        "citation": "Test citation 1",
        "date": "2020-01-01",
        "journal": "Test Journal 1",
        "lastUpdated": "2023-01-01",
        "files": {
            "model.xml": "content1",
            "model.sbml": "content2"
        }
    }
    
    with patch('biomodels_cache_admin.cache.BioModelsAPI', return_value=mock_api_response):
        cache_manager = CacheManager(temp_cache_dir)
        cache_manager.update_cache()
        
        assert len(cache_manager.cache) == 1
        assert "BIOMD0000000001" in cache_manager.cache

def test_get_model(temp_cache_dir, sample_cache_data):
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    with open(cache_file, "w") as f:
        json.dump(sample_cache_data, f)
    
    cache_manager = CacheManager(temp_cache_dir)
    
    # Test with numeric ID
    model = cache_manager.get_model("1")
    assert model["id"] == "BIOMD0000000001"
    
    # Test with full ID
    model = cache_manager.get_model("BIOMD0000000002")
    assert model["id"] == "BIOMD0000000002"

def test_search_models(temp_cache_dir, sample_cache_data):
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    print(f"Cache file path: {cache_file}")
    print('123')
    with open(cache_file, "w") as f:
        json.dump(sample_cache_data, f)
    
    cache_manager = CacheManager(temp_cache_dir)
    
    # Test basic search
    results = cache_manager.search_models("Test")
    assert len(results) == 2
    
    # Test search with filters
    results = cache_manager.search_models(
        "Test",
        filters={
            "authors": ["Author 1"],
            "journals": ["Test Journal 1"],
            "dateRange": {
                "start": "2019-01-01",
                "end": "2020-12-31"
            }
        }
    )
    
    # Verify we got exactly one result
    assert len(results) == 1
    
    # Verify the result matches all our criteria
    model = results[0]
    assert model["id"] == "BIOMD0000000001"
    assert "Author 1" in model["publicationAuthors"]
    assert model["journal"] == "Test Journal 1"
    assert model["date"] == "2020-01-01"
    
    # Verify the other model is not included
    assert "BIOMD0000000002" not in [m["id"] for m in results]

def test_export_import_json(temp_cache_dir, sample_cache_data):
    cache_manager = CacheManager(temp_cache_dir)
    cache_manager.cache = sample_cache_data
    
    # Export to a temporary file
    export_path = os.path.join(temp_cache_dir, "export.json")
    cache_manager.export_json(export_path)
    
    # Create a new cache manager and import the file
    new_cache_manager = CacheManager(temp_cache_dir)
    new_cache_manager.import_json(export_path)
    
    assert new_cache_manager.cache == sample_cache_data

def test_load_invalid_cache(temp_cache_dir):
    # Create an invalid JSON file
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    with open(cache_file, "w") as f:
        f.write("invalid json")
    
    # Should initialize empty cache when file is invalid
    cache_manager = CacheManager(temp_cache_dir)
    assert cache_manager.cache == {}  # Should be empty due to JSON decode error

def test_update_cache_network_error(temp_cache_dir):
    mock_api = MagicMock()
    mock_api.get_models.side_effect = requests.exceptions.RequestException("Network error")
    
    with patch('biomodels_cache_admin.cache.BioModelsAPI', return_value=mock_api):
        cache_manager = CacheManager(temp_cache_dir)
        with pytest.raises(requests.exceptions.RequestException):
            cache_manager.update_cache()

def test_export_json_permission_error(temp_cache_dir, sample_cache_data):
    cache_manager = CacheManager(temp_cache_dir)
    cache_manager.cache = sample_cache_data
    
    # Create a directory with the same name as the export file
    export_path = os.path.join(temp_cache_dir, "export.json")
    os.makedirs(export_path)
    
    with pytest.raises(OSError):
        cache_manager.export_json(export_path)

def test_import_json_not_found(temp_cache_dir):
    cache_manager = CacheManager(temp_cache_dir)
    with pytest.raises(FileNotFoundError):
        cache_manager.import_json("nonexistent.json")

def test_import_json_invalid_format(temp_cache_dir):
    cache_manager = CacheManager(temp_cache_dir)
    
    # Create an invalid JSON file
    invalid_file = os.path.join(temp_cache_dir, "invalid.json")
    with open(invalid_file, "w") as f:
        f.write("invalid json")
    
    with pytest.raises(json.JSONDecodeError):
        cache_manager.import_json(invalid_file)

def test_search_models_invalid_filters(temp_cache_dir, sample_cache_data):
    cache_file = os.path.join(temp_cache_dir, "biomodels_cache.json")
    with open(cache_file, "w") as f:
        json.dump(sample_cache_data, f)
    
    cache_manager = CacheManager(temp_cache_dir)
    
    # Test with invalid date format
    with pytest.raises(ValueError):
        cache_manager.search_models(
            "Test",
            filters={
                "dateRange": {
                    "start": "invalid-date",
                    "end": "2020-12-31"
                }
            }
        ) 