export interface CacheConfig {
  localStorage: Storage;
  indexedDBStorage: Storage;
}

export interface ModelMetadata {
  id: string;
  name: string;
  title: string;
  curators: string[];
  publicationAuthors: string[];
  synopsis: string;
  citation: string;
  date: string;
  journal: string;
  lastUpdated: string;
  files: Record<string, string>;
}

export interface CacheEntry {
  modelId: string;
  files: Record<string, string>;
  metadata: ModelMetadata;
}

export interface SearchQuery {
  query: string;
  filters?: SearchFilters;
  page?: number;
  pageSize?: number;
}

export interface SearchFilters {
  authors?: string[];
  journals?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
}

export interface DateRange {
  start: string;
  end: string;
}

export interface SearchResult {
  modelId: string;
  score: number;
  matches: Match[];
  metadata: ModelMetadata;
}

export interface Match {
  field: string;
  snippet: string;
}

export interface CacheStorage {
  initialize(): Promise<void>;
  getEntry(modelId: string): Promise<CacheEntry | null>;
  saveEntry(entry: CacheEntry): Promise<void>;
  deleteEntry(modelId: string): Promise<void>;
  search(query: SearchQuery): Promise<SearchResult[]>;
}

export interface Storage {
  getModel(id: string): Promise<ModelMetadata | null>;
  searchModels(
    query: string,
    filters?: SearchFilters
  ): Promise<ModelMetadata[]>;
  updateCache(models: Record<string, ModelMetadata>): Promise<void>;
  initialize?(): Promise<void>;
}
