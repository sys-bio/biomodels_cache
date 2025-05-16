import { LocalStorage } from "../../src/storage/LocalStorage";
import { ModelMetadata, SearchFilters } from "../../src/types";

describe("LocalStorage", () => {
  let storage: LocalStorage;
  const CACHE_KEY = "biomodels_cache";

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
    // Clear localStorage
    localStorage.clear();
    storage = new LocalStorage();
  });

  describe("getModel", () => {
    it("should return model if it exists in cache", async () => {
      // Store sample model in cache
      const cache = { [sampleModel.id]: sampleModel };
      localStorage.setItem(CACHE_KEY, JSON.stringify(cache));

      const result = await storage.getModel(sampleModel.id);
      expect(result).toEqual(sampleModel);
    });

    it("should return null if model does not exist", async () => {
      const result = await storage.getModel("nonexistent");
      expect(result).toBeNull();
    });

    it("should return null if cache is invalid JSON", async () => {
      localStorage.setItem(CACHE_KEY, "invalid json");
      const result = await storage.getModel(sampleModel.id);
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

    beforeEach(() => {
      localStorage.setItem(CACHE_KEY, JSON.stringify(sampleModels));
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

      const storedCache = JSON.parse(localStorage.getItem(CACHE_KEY) || "{}");
      expect(storedCache).toEqual(newModels);
    });

    it("should merge new models with existing cache", async () => {
      // Store initial model
      const initialCache = { [sampleModel.id]: sampleModel };
      localStorage.setItem(CACHE_KEY, JSON.stringify(initialCache));

      // Add new model
      const newModel = {
        ...sampleModel,
        id: "BIOMD0000000002",
        name: "New Model",
      };
      const newModels = { [newModel.id]: newModel };

      await storage.updateCache(newModels);

      const storedCache = JSON.parse(localStorage.getItem(CACHE_KEY) || "{}");
      expect(storedCache).toEqual({
        ...initialCache,
        ...newModels,
      });
    });
  });
});
