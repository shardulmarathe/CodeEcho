"""A small thread-safe LRU map for the process-local caches.

These caches exist because the backend is deliberately single-worker and long-lived
(see ARCHITECTURE.md). Previously they were plain dicts that only ever grew — on
Render's free tier the 15-minute spin-down happened to clear them, so the growth was
invisible. Keeping the service warm removes that accidental reclamation, so the bound
has to be explicit.

Eviction is least-recently-USED, not least-recently-written: an in-progress interview
stays resident as long as it's being touched. Evicting is always safe when Supabase is
configured — the durable row is re-read on the next miss. Without Supabase (local/demo)
an eviction does lose the entry, which is why the bounds are far above any single
session's working set.
"""

from collections import OrderedDict
from threading import RLock
from typing import Generic, Iterator, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class BoundedCache(Generic[K, V]):
    def __init__(self, maxsize: int) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be positive")
        self._maxsize = maxsize
        self._data: "OrderedDict[K, V]" = OrderedDict()
        self._lock = RLock()

    def __setitem__(self, key: K, value: V) -> None:
        with self._lock:
            self._data[key] = value
            self._data.move_to_end(key)
            while len(self._data) > self._maxsize:
                self._data.popitem(last=False)

    def __getitem__(self, key: K) -> V:
        with self._lock:
            value = self._data[key]
            self._data.move_to_end(key)
            return value

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        with self._lock:
            if key not in self._data:
                return default
            self._data.move_to_end(key)
            return self._data[key]

    def __contains__(self, key: object) -> bool:
        # Membership alone is not a use; it must not reorder. Callers that follow a
        # hit with __getitem__ get the LRU bump there.
        with self._lock:
            return key in self._data

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)

    def values(self) -> list[V]:
        """A snapshot, so callers can iterate while other threads write."""
        with self._lock:
            return list(self._data.values())

    def __iter__(self) -> Iterator[K]:
        with self._lock:
            return iter(list(self._data.keys()))

    def clear(self) -> None:
        with self._lock:
            self._data.clear()
