/**
 * RIGHT FIT — Ultra-Fast Client-Side SWR Cache
 * Provides 0ms instant page loads and seamless background revalidation.
 * Persists across navigations and tab switching using Memory + SessionStorage.
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttlMs: number;
}

class FastCache {
  private memCache = new Map<string, CacheEntry<any>>();
  private defaultTtl = 20 * 1000; // 20 seconds for responsive live sync

  get<T>(key: string, forceFresh: boolean = false): T | null {
    if (forceFresh) {
      return null;
    }

    // 1. Check in-memory cache first (0ms)
    const mem = this.memCache.get(key);
    if (mem) {
      if (Date.now() - mem.timestamp < mem.ttlMs) {
        return mem.data as T;
      }
      // Expired entry
      return mem.data as T;
    }

    // 2. Fallback to SessionStorage (persists across Next.js route transitions)
    if (typeof window !== "undefined" && window.sessionStorage) {
      try {
        const raw = sessionStorage.getItem(`rf_cache_${key}`);
        if (raw) {
          const parsed: CacheEntry<T> = JSON.parse(raw);
          if (Date.now() - parsed.timestamp < parsed.ttlMs * 2) {
            // Populate memCache if within reasonable window
            this.memCache.set(key, parsed);
            return parsed.data;
          }
        }
      } catch (e) {
        // Ignore storage parse issues
      }
    }

    return null;
  }

  isFresh(key: string): boolean {
    const mem = this.memCache.get(key);
    if (mem) {
      return Date.now() - mem.timestamp < mem.ttlMs;
    }
    return false;
  }

  set<T>(key: string, data: T, ttlMs?: number): void {
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttlMs: ttlMs ?? this.defaultTtl,
    };
    this.memCache.set(key, entry);

    if (typeof window !== "undefined" && window.sessionStorage) {
      try {
        sessionStorage.setItem(`rf_cache_${key}`, JSON.stringify(entry));
      } catch (e) {
        // Storage might be full, safe to ignore
      }
    }
  }

  delete(key: string): void {
    this.memCache.delete(key);
    if (typeof window !== "undefined" && window.sessionStorage) {
      try {
        sessionStorage.removeItem(`rf_cache_${key}`);
      } catch (e) { }
    }
  }

  clear(prefix?: string): void {
    if (!prefix) {
      this.memCache.clear();
      if (typeof window !== "undefined" && window.sessionStorage) {
        try {
          Object.keys(sessionStorage).forEach((k) => {
            if (k.startsWith("rf_cache_")) {
              sessionStorage.removeItem(k);
            }
          });
        } catch (e) { }
      }
      return;
    }

    // Clear matching prefix
    for (const k of this.memCache.keys()) {
      if (k.startsWith(prefix)) {
        this.memCache.delete(k);
      }
    }
    if (typeof window !== "undefined" && window.sessionStorage) {
      try {
        Object.keys(sessionStorage).forEach((k) => {
          if (k.startsWith(`rf_cache_${prefix}`)) {
            sessionStorage.removeItem(k);
          }
        });
      } catch (e) { }
    }
  }
}

export const fastCache = new FastCache();

