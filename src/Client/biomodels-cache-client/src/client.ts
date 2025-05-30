/* eslint-disable @typescript-eslint/await-thenable */
import fs from "fs";
import path from "path";
import {
  CacheClient,
  CacheConfig,
  ModelData,
  SearchQuery,
  FileDescriptor,
  CacheError,
} from "./types";

export class BioModelsCacheClient implements CacheClient {
  private config: CacheConfig | null = null;
  private cache: Map<string, ModelData> = new Map();
  private initialized = false;
  private cacheFilePath: string | null = null;

  initialize = async (config: CacheConfig): Promise<void> => {
    try {
      // Validate config
      if (!config.path) {
        throw new CacheError("Cache path is required", "INVALID_CONFIG");
      }

      this.config = config;
      // Check if the path points to a directory or file
      const stats = await fs.promises.stat(config.path);
      if (stats.isDirectory()) {
        this.cacheFilePath = path.join(config.path, "biomodels_cache.json");
      } else {
        this.cacheFilePath = config.path;
      }

      this.initialized = true;

      // Load existing cache if local
      if (config.accessType === "local") {
        await this.loadCache();
      }
    } catch (error: any) {
      throw new CacheError(
        `Failed to initialize cache: ${error.message}`,
        "INITIALIZATION_ERROR"
      );
    }
  };

  getByKey = async (key: string): Promise<ModelData | null> => {
    this.checkInitialized();

    try {
      // Check in-memory cache first
      if (this.cache.has(key)) {
        return this.cache.get(key) || null;
      }

      if (this.config?.accessType === "local" && this.cacheFilePath) {
        // Try to load from the main cache file
        const model = await this.loadModelFromCacheFile(key);
        if (model) {
          this.cache.set(key, model);
          return model;
        }
      }

      return null;
    } catch (error: any) {
      throw new CacheError(
        `Failed to get model by key: ${error.message}`,
        "GET_ERROR"
      );
    }
  };

  search = async (query: SearchQuery): Promise<ModelData[]> => {
    this.checkInitialized();

    try {
      const results: ModelData[] = [];
      const searchTerm = query.term.toLowerCase();

      if (!this.cacheFilePath) {
        throw new CacheError("Cache file path not set", "INVALID_CONFIG");
      }

      // Read and parse the cache file
      const data = await fs.promises.readFile(this.cacheFilePath, "utf-8");
      const cacheData: Record<string, ModelData> = JSON.parse(data);

      // Search through all models in the cache file
      for (const [key, model] of Object.entries(cacheData)) {
        const modelWithId: ModelData = {
          ...model,
          id: key,
        };
        if (this.matchesSearch(modelWithId, searchTerm, query.filters)) {
          results.push(modelWithId);
        }
      }

      // Apply pagination
      const offset = query.offset || 0;
      const limit = query.limit || results.length;
      return results.slice(offset, offset + limit);
    } catch (error: any) {
      throw new CacheError(
        `Failed to search models: ${error.message}`,
        "SEARCH_ERROR"
      );
    }
  };

  getFileDescriptor = async (modelId: string): Promise<FileDescriptor> => {
    this.checkInitialized();

    try {
      if (this.config?.accessType === "local") {
        // Get the cache directory from the cache file path
        const cacheDir = path.dirname(this.cacheFilePath || "");

        // Check for both JSON and XML files
        const jsonPath = path.join(cacheDir, `${modelId}.json`);
        const xmlPath = path.join(cacheDir, `${modelId}.xml`);

        let filePath: string;
        let fileType: string;

        if (fs.existsSync(jsonPath)) {
          filePath = jsonPath;
          fileType = "json";
        } else if (fs.existsSync(xmlPath)) {
          filePath = xmlPath;
          fileType = "xml";
        } else {
          throw new CacheError(
            `No file found for model ${modelId}`,
            "FILE_NOT_FOUND"
          );
        }

        const stats = await fs.promises.stat(filePath);
        const descriptor: FileDescriptor = {
          modelId,
          filePath,
          fileType,
          size: stats.size,
          lastModified: stats.mtime,
        };

        return descriptor;
      }

      throw new CacheError(
        "Remote file descriptors not supported yet",
        "NOT_IMPLEMENTED"
      );
    } catch (error: any) {
      throw new CacheError(
        `Failed to get file descriptor: ${error.message}`,
        "FILE_DESCRIPTOR_ERROR"
      );
    }
  };

  private checkInitialized = (): void => {
    if (!this.initialized) {
      throw new CacheError("Cache client not initialized", "NOT_INITIALIZED");
    }
  };

  private loadCache = async (): Promise<void> => {
    try {
      if (!this.cacheFilePath) {
        throw new CacheError("Cache file path not set", "INVALID_CONFIG");
      }

      // Read and parse the main cache file
      const data = await fs.promises.readFile(this.cacheFilePath, "utf-8");
      const cacheData = JSON.parse(data);

      // Clear existing cache
      this.cache.clear();

      // Load all models into memory
      for (const [key, value] of Object.entries(cacheData)) {
        this.cache.set(key, value as ModelData);
      }
    } catch (error: any) {
      if (error.code === "ENOENT") {
        throw new CacheError("Cache file not found", "FILE_NOT_FOUND");
      }
      throw new CacheError(
        `Failed to load cache: ${error.message}`,
        "LOAD_ERROR"
      );
    }
  };

  private loadModelFromCacheFile = async (
    modelId: string
  ): Promise<ModelData | null> => {
    try {
      if (!this.cacheFilePath) {
        return null;
      }

      // Read the cache file
      const data = await fs.promises.readFile(this.cacheFilePath, "utf-8");
      const cacheData = JSON.parse(data);

      return cacheData[modelId] || null;
    } catch (error: any) {
      if (error.code === "ENOENT") {
        return null;
      }
      throw error;
    }
  };

  private matchesSearch = (
    model: ModelData,
    searchTerm: string,
    filters?: SearchQuery["filters"]
  ): boolean => {
    // Basic text search
    const matchesText =
      model.name?.toLowerCase().includes(searchTerm) ||
      false ||
      model.title?.toLowerCase().includes(searchTerm) ||
      false ||
      model.synopsis?.toLowerCase().includes(searchTerm) ||
      false;

    if (!matchesText) return false;

    // Apply filters if specified
    if (filters) {
      // Author filter
      if (filters.authors?.length && model.authors?.length) {
        const modelAuthors = model.authors.map((a) => a.toLowerCase());
        if (
          !filters.authors.some((a) => modelAuthors.includes(a.toLowerCase()))
        ) {
          return false;
        }
      }

      // Journal filter
      if (filters.journals?.length && model.journal) {
        if (!filters.journals.includes(model.journal)) {
          return false;
        }
      }

      // Date range filter
      if (filters.dateRange && model.date) {
        const modelDate = new Date(model.date);
        const startDate = new Date(filters.dateRange.start);
        const endDate = new Date(filters.dateRange.end);
        if (modelDate < startDate || modelDate > endDate) {
          return false;
        }
      }
    }

    return true;
  };

  // private async calculateChecksum(filePath: string): Promise<string> {
  //   // TODO: Implement checksum calculation
  //   return "";
  // }
}
