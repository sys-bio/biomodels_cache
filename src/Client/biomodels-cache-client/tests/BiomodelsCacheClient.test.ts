import { BiomodelsCacheClient } from "../src/BiomodelsCacheClient";
import { ModelMetadata, SearchFilters } from "../src/types";
import { LocalStorage } from "../src/storage/LocalStorage";
import { IndexedDBStorage } from "../src/storage/IndexedDBStorage";

// Mock the storage implementations
jest.mock("../src/storage/LocalStorage");
jest.mock("../src/storage/IndexedDBStorage");

describe("BiomodelsCacheClient", () => {
  let client: BiomodelsCacheClient;
  let mockLocalStorage: jest.Mocked<LocalStorage>;
  let mockIndexedDBStorage: jest.Mocked<IndexedDBStorage>;

  const sampleModel: ModelMetadata = {
    id: "BIOMD0000000001",
    name: "Test Model",
    title: "Test Title",
    curators: ["Curator 1"],
    publicationAuthors: ["Author 1"],
    synopsis: "Test synopsis",
    citation: "Test citation",
    date: "2020-01-01",
    journal: "Test Journal",
    lastUpdated: "2023-01-01",
    files: {
      "model.xml": "content1",
      "model.sbml": "content2",
    },
  };

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Create mock instances
    mockLocalStorage = new LocalStorage() as jest.Mocked<LocalStorage>;
    mockIndexedDBStorage =
      new IndexedDBStorage() as jest.Mocked<IndexedDBStorage>;

    // Create client with mock storage
    client = new BiomodelsCacheClient({
      localStorage: mockLocalStorage,
      indexedDBStorage: mockIndexedDBStorage,
    });
  });

  describe("getModel", () => {
    it("should return model from cache if available", async () => {
      mockLocalStorage.getModel.mockResolvedValue(sampleModel);

      const result = await client.getModel("1");
      expect(result).toEqual(sampleModel);
      expect(mockLocalStorage.getModel).toHaveBeenCalledWith("BIOMD0000000001");
    });

    it("should fetch from API if not in cache", async () => {
      mockLocalStorage.getModel.mockResolvedValue(null);
      mockIndexedDBStorage.getModel.mockResolvedValue(null);

      // Mock the fetch API
      global.fetch = jest.fn().mockImplementation(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(sampleModel),
        })
      );

      const result = await client.getModel("1");
      expect(result).toEqual(sampleModel);
      expect(global.fetch).toHaveBeenCalledWith(
        "https://www.ebi.ac.uk/biomodels/api/v1/models/BIOMD0000000001"
      );
    });

    it("should handle API errors gracefully", async () => {
      mockLocalStorage.getModel.mockResolvedValue(null);
      mockIndexedDBStorage.getModel.mockResolvedValue(null);

      // Mock the fetch API to return an error
      global.fetch = jest.fn().mockImplementation(() =>
        Promise.resolve({
          ok: false,
          status: 404,
          statusText: "Not Found",
        })
      );

      await expect(client.getModel("999999")).rejects.toThrow("404 Not Found");
    });
  });

  describe("searchModels", () => {
    const sampleModels: ModelMetadata[] = [
      sampleModel,
      {
        ...sampleModel,
        id: "BIOMD0000000002",
        name: "Another Model",
        publicationAuthors: ["Author 2"],
        journal: "Another Journal",
        date: "2021-01-01",
      },
    ];

    it("should search models with filters", async () => {
      mockLocalStorage.searchModels.mockResolvedValue([sampleModel]);

      const filters: SearchFilters = {
        authors: ["Author 1"],
        journals: ["Test Journal"],
        dateRange: {
          start: "2019-01-01",
          end: "2020-12-31",
        },
      };

      const results = await client.searchModels("Test", filters);
      expect(results).toEqual([sampleModel]);
      expect(mockLocalStorage.searchModels).toHaveBeenCalledWith(
        "Test",
        filters
      );
    });

    it("should handle empty results", async () => {
      mockLocalStorage.searchModels.mockResolvedValue([]);

      const results = await client.searchModels("Nonexistent");
      expect(results).toEqual([]);
    });
  });

  describe("updateCache", () => {
    it("should update cache with new models", async () => {
      // Mock the fetch API to return a list of models
      global.fetch = jest.fn().mockImplementation((url) => {
        if (url.includes("/models")) {
          return Promise.resolve({
            ok: true,
            json: () =>
              Promise.resolve({
                models: [sampleModel],
                total: 1,
              }),
          });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(sampleModel),
        });
      });

      await client.updateCache();

      expect(mockLocalStorage.updateCache).toHaveBeenCalled();
      expect(mockIndexedDBStorage.updateCache).toHaveBeenCalled();
    });

    it("should handle API errors during update", async () => {
      // Mock the fetch API to return an error
      global.fetch = jest.fn().mockImplementation(() =>
        Promise.resolve({
          ok: false,
          status: 500,
          statusText: "Server Error",
        })
      );

      await expect(client.updateCache()).rejects.toThrow("500 Server Error");
    });
  });
});
