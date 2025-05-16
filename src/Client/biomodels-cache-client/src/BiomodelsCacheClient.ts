import { CacheConfig, ModelMetadata, SearchFilters, Storage } from "./types";

export class BiomodelsCacheClient {
  private readonly API_BASE_URL = "https://www.ebi.ac.uk/biomodels/api/v1";
  private readonly localStorage: Storage;
  private readonly indexedDBStorage: Storage;

  constructor(config: CacheConfig) {
    this.localStorage = config.localStorage;
    this.indexedDBStorage = config.indexedDBStorage;

    // Initialize storage if needed
    if (this.localStorage.initialize) {
      this.localStorage.initialize();
    }
    if (this.indexedDBStorage.initialize) {
      this.indexedDBStorage.initialize();
    }
  }

  private formatModelId(id: string): string {
    const numericId = id.replace(/\D/g, "");
    return `BIOMD${numericId.padStart(10, "0")}`;
  }

  async getModel(id: string): Promise<ModelMetadata> {
    const formattedId = this.formatModelId(id);

    // Try to get from local storage first
    const localModel = await this.localStorage.getModel(formattedId);
    if (localModel) return localModel;

    // Try indexed DB next
    const indexedModel = await this.indexedDBStorage.getModel(formattedId);
    if (indexedModel) return indexedModel;

    // Fetch from API if not in cache
    const response = await fetch(`${this.API_BASE_URL}/models/${formattedId}`);
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }

    const model = await response.json();
    const modelsMap = { [formattedId]: model };

    // Update both storage implementations
    await Promise.all([
      this.localStorage.updateCache(modelsMap),
      this.indexedDBStorage.updateCache(modelsMap),
    ]);

    return model;
  }

  async searchModels(
    query: string,
    filters?: SearchFilters
  ): Promise<ModelMetadata[]> {
    // Search in local storage first
    const localResults = await this.localStorage.searchModels(query, filters);
    if (localResults.length > 0) return localResults;

    // Try indexed DB next
    const indexedResults = await this.indexedDBStorage.searchModels(
      query,
      filters
    );
    return indexedResults || [];
  }

  async updateCache(): Promise<void> {
    // Fetch all models from API
    const response = await fetch(`${this.API_BASE_URL}/models`);
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}`);
    }

    const { models } = await response.json();
    const modelsMap: Record<string, ModelMetadata> = {};

    // Create a map of models by ID
    for (const model of models) {
      modelsMap[model.id] = model;
    }

    // Update both storage implementations
    await Promise.all([
      this.localStorage.updateCache(modelsMap),
      this.indexedDBStorage.updateCache(modelsMap),
    ]);
  }
}
