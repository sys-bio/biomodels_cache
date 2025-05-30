import pytest
from unittest.mock import patch, MagicMock
import requests
import os
import json
from biomodels_cache_admin.api import BioModelsAPI, normalize_model

@pytest.fixture
def mock_model_response():
    mock = MagicMock()
    mock.json.return_value = {
        "id": "BIOMD0000000001",
        "name": "Test Model 1",
        "title": "Test Title",
        "authors": ["Author 1"],
        "synopsis": "Test synopsis",
        "citation": "Test citation",
        "date": "2020-01-01",
        "journal": "Test Journal",
        "publication": {
            "title": "Test Title",
            "authors": [{"name": "Author 1"}],
            "date": "2020-01-01",
            "journal": "Test Journal"
        }
    }
    mock.raise_for_status.return_value = None
    return mock

@pytest.fixture
def temp_cache_dir(tmp_path):
    return str(tmp_path)

def test_normalize_model():
    # Test with full model data
    model = {
        "id": "BIOMD0000000001",
        "name": "Test Model",
        "authors": ["Author 1"],
        "title": "Test Title",
        "synopsis": "Test synopsis",
        "citation": "Test citation",
        "date": "2020-01-01",
        "journal": "Test Journal"
    }
    normalized = normalize_model(model)
    assert normalized["model_id"] == "BIOMD0000000001"
    assert normalized["id"] == "BIOMD0000000001"
    assert normalized["name"] == "Test Model"
    assert normalized["authors"] == ["Author 1"]

    # Test with publication data
    model = {
        "id": "BIOMD0000000001",
        "publication": {
            "title": "Test Title",
            "authors": [{"name": "Author 1"}],
            "date": "2020-01-01",
            "journal": "Test Journal"
        }
    }
    normalized = normalize_model(model)
    assert normalized["model_id"] == "BIOMD0000000001"
    assert normalized["title"] == "Test Title"
    assert normalized["authors"] == ["Author 1"]
    assert normalized["date"] == "2020-01-01"
    assert normalized["journal"] == "Test Journal"

def test_get_model_numeric_id(mock_model_response, temp_cache_dir):
    with patch('requests.get', return_value=mock_model_response):
        api = BioModelsAPI(cache_dir=temp_cache_dir)
        model = api.get_model("1")
        
        assert model["model_id"] == "BIOMD0000000001"
        assert model["id"] == "BIOMD0000000001"
        assert model["name"] == "Test Model 1"
        assert model["authors"] == ["Author 1"]

def test_get_model_full_id(mock_model_response, temp_cache_dir):
    with patch('requests.get', return_value=mock_model_response):
        api = BioModelsAPI(cache_dir=temp_cache_dir)
        model = api.get_model("BIOMD0000000001")
        
        assert model["model_id"] == "BIOMD0000000001"
        assert model["id"] == "BIOMD0000000001"
        assert model["name"] == "Test Model 1"

def test_get_model_not_found(temp_cache_dir):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found", response=mock_response)
    
    with patch('requests.get', return_value=mock_response):
        api = BioModelsAPI(cache_dir=temp_cache_dir)
        model = api.get_model("999999")
        assert model is None

def test_get_model_network_error(temp_cache_dir):
    with patch('requests.get', side_effect=requests.exceptions.RequestException("Network error")):
        api = BioModelsAPI(cache_dir=temp_cache_dir)
        with pytest.raises(requests.exceptions.RequestException):
            api.get_model("1")

def test_export_models_to_json(mock_model_response, temp_cache_dir):
    with patch('requests.get', return_value=mock_model_response):
        api = BioModelsAPI(cache_dir=temp_cache_dir)
        export_path = os.path.join(temp_cache_dir, "exported_models.json")
        
        success = api.export_models_to_json(export_path, ["BIOMD0000000001"])
        assert success
        
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
            assert "BIOMD0000000001" in exported_data
            assert exported_data["BIOMD0000000001"]["name"] == "Test Model 1"

def test_import_models_from_json(temp_cache_dir):
    # Create test JSON file
    test_data = {
        "BIOMD0000000001": {
            "id": "BIOMD0000000001",
            "name": "Test Model 1",
            "authors": ["Author 1"]
        }
    }
    json_path = os.path.join(temp_cache_dir, "test_models.json")
    with open(json_path, 'w') as f:
        json.dump(test_data, f)
    
    api = BioModelsAPI(cache_dir=temp_cache_dir)
    imported_models = api.import_models_from_json(json_path)
    
    assert len(imported_models) == 1
    assert imported_models[0]["id"] == "BIOMD0000000001"
    assert imported_models[0]["name"] == "Test Model 1"

def test_search_cached_models(mock_model_response, temp_cache_dir):
    with patch('requests.get', return_value=mock_model_response):
        api = BioModelsAPI(cache_dir=temp_cache_dir)
        # First get a model to cache it
        api.get_model("1")
        
        # Now search for it
        results = api.search_cached_models("Test")
        assert len(results) == 1
        assert results[0]["name"] == "Test Model 1" 