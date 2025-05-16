import { ModelMetadata, SearchFilters, Storage } from '../types';

export class LocalStorage implements Storage {
    private readonly CACHE_KEY = 'biomodels_cache';

    async getModel(id: string): Promise<ModelMetadata | null> {
        try {
            const cache = JSON.parse(localStorage.getItem(this.CACHE_KEY) || '{}');
            return cache[id] || null;
        } catch {
            return null;
        }
    }

    async searchModels(query: string, filters?: SearchFilters): Promise<ModelMetadata[]> {
        try {
            const cache = JSON.parse(localStorage.getItem(this.CACHE_KEY) || '{}');
            let results = Object.values(cache) as ModelMetadata[];

            // Apply text search
            if (query) {
                const lowerQuery = query.toLowerCase();
                results = results.filter(model => 
                    model.name.toLowerCase().includes(lowerQuery) ||
                    model.title.toLowerCase().includes(lowerQuery) ||
                    model.synopsis.toLowerCase().includes(lowerQuery)
                );
            }

            // Apply filters
            if (filters) {
                if (filters.authors?.length) {
                    results = results.filter(model =>
                        model.publicationAuthors.some(author =>
                            filters.authors!.includes(author)
                        )
                    );
                }

                if (filters.journals?.length) {
                    results = results.filter(model =>
                        filters.journals!.includes(model.journal)
                    );
                }

                if (filters.dateRange) {
                    const { start, end } = filters.dateRange;
                    results = results.filter(model =>
                        model.date >= start && model.date <= end
                    );
                }
            }

            return results;
        } catch {
            return [];
        }
    }

    async updateCache(models: Record<string, ModelMetadata>): Promise<void> {
        try {
            const existingCache = JSON.parse(localStorage.getItem(this.CACHE_KEY) || '{}');
            const updatedCache = { ...existingCache, ...models };
            localStorage.setItem(this.CACHE_KEY, JSON.stringify(updatedCache));
        } catch (error) {
            console.error('Failed to update cache:', error);
            throw error;
        }
    }
} 