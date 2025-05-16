"""
Test BioModels v1 API endpoints.
"""
import sys
import requests

def test_v1_api():
    base_url = "https://www.ebi.ac.uk/biomodels/api/v1"
    headers = {"Accept": "application/json"}
    
    # Test 1: Get all models
    url = f"{base_url}/models"
    response = requests.get(url, headers=headers)
    print(f"\nGET {url}")
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}")
    
    # Test 2: Get specific model
    model_id = "BIOMD0000000413"
    url = f"{base_url}/models/{model_id}"
    response = requests.get(url, headers=headers)
    print(f"\nGET {url}")
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}")

if __name__ == "__main__":
    test_v1_api() 