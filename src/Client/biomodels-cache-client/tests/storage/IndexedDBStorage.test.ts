import { IndexedDBStorage } from "../../src/storage/IndexedDBStorage";
import { ModelMetadata, SearchFilters } from "../../src/types";

// Polyfill structuredClone if not available
if (typeof structuredClone !== "function") {
  (global as any).structuredClone = (obj: any) =>
    JSON.parse(JSON.stringify(obj));
}

jest.setTimeout(30000); // Increase timeout to 30 seconds

describe("IndexedDBStorage", () => {
  let storage: IndexedDBStorage;
  const DB_NAME = "biomodels_cache";
  const STORE_NAME = "models";

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

  beforeAll(async () => {
    // Delete existing database
    const request = indexedDB.deleteDatabase(DB_NAME);
    await new Promise((resolve, reject) => {
      request.onsuccess = resolve;
      request.onerror = reject;
    });
  });

  beforeEach(async () => {
    storage = new IndexedDBStorage();
    await storage.initialize();
  });

  afterEach(async () => {
    // Close the database connection
    if (storage["db"]) {
      storage["db"].close();
    }
  });

  afterAll(async () => {
    // Clean up the database
    const request = indexedDB.deleteDatabase(DB_NAME);
    await new Promise((resolve, reject) => {
      request.onsuccess = resolve;
      request.onerror = reject;
    });
  });

  describe("getModel", () => {
    it("should return model if it exists in cache", async () => {
      // Store sample model in cache
      await storage.updateCache({ [sampleModel.id]: sampleModel });

      const result = await storage.getModel(sampleModel.id);
      expect(result).toEqual(sampleModel);
    });

    it("should return null if model does not exist", async () => {
      const result = await storage.getModel("nonexistent");
      expect(result).toBeNull();
    });
  });

  describe("searchModels", () => {
    const sampleModels: Record<string, ModelMetadata> = {
      BIOMD0000000001: sampleModel,
      BIOMD0000000002: {
        ...sampleModel,
        id: "BIOMD0000000002",
        name: "Another Model",
        publicationAuthors: ["Author 2"],
        journal: "Another Journal",
        date: "2021-01-01",
      },
    };

    beforeEach(async () => {
      await storage.updateCache(sampleModels);
    });

    it("should find models matching search query", async () => {
      const results = await storage.searchModels("Test");
      expect(results).toHaveLength(2);
      expect(results[0].id).toBe("BIOMD0000000001");
    });

    it("should apply author filter", async () => {
      const filters: SearchFilters = {
        authors: ["Author 1"],
      };

      const results = await storage.searchModels("Test", filters);
      expect(results).toHaveLength(1);
      expect(results[0].publicationAuthors).toContain("Author 1");
    });

    it("should apply journal filter", async () => {
      const filters: SearchFilters = {
        journals: ["Test Journal"],
      };

      const results = await storage.searchModels("Test", filters);
      expect(results).toHaveLength(1);
      expect(results[0].journal).toBe("Test Journal");
    });

    it("should apply date range filter", async () => {
      const filters: SearchFilters = {
        dateRange: {
          start: "2019-01-01",
          end: "2020-12-31",
        },
      };

      const results = await storage.searchModels("Test", filters);
      expect(results).toHaveLength(1);
      expect(results[0].date).toBe("2020-01-01");
    });

    it("should return empty array if no matches found", async () => {
      const results = await storage.searchModels("Nonexistent");
      expect(results).toHaveLength(0);
    });
  });

  describe("updateCache", () => {
    it("should update cache with new models", async () => {
      const newModels: Record<string, ModelMetadata> = {
        [sampleModel.id]: sampleModel,
      };

      await storage.updateCache(newModels);

      const result = await storage.getModel(sampleModel.id);
      expect(result).toEqual(sampleModel);
    });

    it("should merge new models with existing cache", async () => {
      // Store initial model
      await storage.updateCache({ [sampleModel.id]: sampleModel });

      // Add new model
      const newModel = {
        ...sampleModel,
        id: "BIOMD0000000002",
        name: "New Model",
      };
      const newModels = { [newModel.id]: newModel };

      await storage.updateCache(newModels);

      const result1 = await storage.getModel(sampleModel.id);
      const result2 = await storage.getModel(newModel.id);

      expect(result1).toEqual(sampleModel);
      expect(result2).toEqual(newModel);
    });
  });
});
