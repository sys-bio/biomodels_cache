import { BiomodelsCacheClient } from "biomodels-cache-client";

// Mock data for testing
const mockModel = {
  id: "BIOMD0000000001",
  name: "Sample Model",
  title: "Sample Model Title",
  curators: ["John Doe"],
  publicationAuthors: ["Jane Smith"],
  synopsis: "This is a sample model",
  citation: "Sample Citation",
  date: "2024-01-01",
  journal: "Sample Journal",
  lastUpdated: "2024-01-01",
  files: {
    "model.xml": "https://example.com/model.xml",
  },
};

// Mock API response
const mockApiResponse = {
  models: [mockModel],
};

// Mock fetch function
global.fetch = async (url) => {
  console.log(`Mock API call to: ${url}`);
  return {
    ok: true,
    json: async () => mockApiResponse,
  };
};

// Define the configuration object
const config = {
  localStorage: {
    // Example configuration for localStorage
    key: "biomodels_cache", // Key to store data in localStorage
    getModel: async (id) => {
      // Example implementation for getModel
      console.log(`Getting model with ID: ${id} from localStorage`);
      return mockModel; // Return mock data for testing
    },
    searchModels: async (query, filters) => {
      // Example implementation for searchModels
      console.log(
        `Searching models with query: ${query} in localStorage`,
        filters
      );
      return [mockModel]; // Return mock data for testing
    },
    updateCache: async (modelsMap) => {
      // Example implementation for updateCache
      console.log("Updating localStorage cache with models:", modelsMap);
    },
  },
  indexedDBStorage: {
    initialize: async function () {
      // Example initialization logic
      console.log("Initializing IndexedDB storage...");
      // Add any necessary initialization code here
    },
    dbName: "biomodels_cache_db", // Name of the IndexedDB database
    storeName: "models", // Name of the object store
    version: 1, // Database version
    getModel: async (id) => {
      // Example implementation for getModel
      console.log(`Getting model with ID: ${id} from IndexedDB`);
      return mockModel; // Return mock data for testing
    },
    searchModels: async (query, filters) => {
      // Example implementation for searchModels
      console.log(
        `Searching models with query: ${query} in IndexedDB`,
        filters
      );
      return [mockModel]; // Return mock data for testing
    },
    updateCache: async (modelsMap) => {
      // Example implementation for updateCache
      console.log("Updating IndexedDB cache with models:", modelsMap);
    },
  },
};

const client = new BiomodelsCacheClient(config);

// Example: Get a model by ID
async function getModel() {
  try {
    const model = await client.getModel("modelId1");
    console.log("Fetched model:", model);
  } catch (error) {
    console.error("Error fetching model:", error);
  }
}

// Example: Search for models
async function searchModels() {
  try {
    const results = await client.searchModels("sample");
    console.log("Search results:", results);
  } catch (error) {
    console.error("Error searching models:", error);
  }
}

// Example: Update the cache
async function updateCache() {
  try {
    await client.updateCache();
    console.log("Cache updated successfully.");
  } catch (error) {
    console.error("Error updating cache:", error);
  }
}

// Call the example functions
getModel();
searchModels();
updateCache();
