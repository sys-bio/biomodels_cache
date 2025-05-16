import { ModelMetadata, SearchFilters, Storage } from '../types';

export class IndexedDBStorage implements Storage {
    private readonly DB_NAME = 'biomodels_cache';
    private readonly STORE_NAME = 'models';
    private db: IDBDatabase | null = null;

    async initialize(): Promise<void> {
        if (this.db) return;

        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.DB_NAME, 1);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = (event.target as IDBOpenDBRequest).result;
                if (!db.objectStoreNames.contains(this.STORE_NAME)) {
                    db.createObjectStore(this.STORE_NAME, { keyPath: 'id' });
                }
            };
        });
    }

    async getModel(id: string): Promise<ModelMetadata | null> {
        await this.initialize();
        if (!this.db) throw new Error('Database not initialized');

        return new Promise((resolve, reject) => {
            const transaction = this.db!.transaction([this.STORE_NAME], 'readonly');
            const store = transaction.objectStore(this.STORE_NAME);
            const request = store.get(id);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result || null);
        });
    }

    async searchModels(query: string, filters?: SearchFilters): Promise<ModelMetadata[]> {
        await this.initialize();
        if (!this.db) throw new Error('Database not initialized');

        return new Promise((resolve, reject) => {
            const transaction = this.db!.transaction([this.STORE_NAME], 'readonly');
            const store = transaction.objectStore(this.STORE_NAME);
            const request = store.getAll();

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                let results = request.result as ModelMetadata[];

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

                resolve(results);
            };
        });
    }

    async updateCache(models: Record<string, ModelMetadata>): Promise<void> {
        await this.initialize();
        if (!this.db) throw new Error('Database not initialized');

        return new Promise((resolve, reject) => {
            const transaction = this.db!.transaction([this.STORE_NAME], 'readwrite');
            const store = transaction.objectStore(this.STORE_NAME);

            Object.values(models).forEach(model => {
                store.put(model);
            });

            transaction.oncomplete = () => resolve();
            transaction.onerror = () => reject(transaction.error);
        });
    }
} 