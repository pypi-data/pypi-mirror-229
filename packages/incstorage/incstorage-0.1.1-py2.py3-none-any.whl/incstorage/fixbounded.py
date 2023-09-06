from typing import Any
from datetime import datetime, timedelta
from .incstorage import iVFS, iCluster, Book


class BoundedCluster(iCluster):
    pass


class FixBoundedBook(Book):
    def __init__(self, bind: Any, fs: iVFS, tags: list, flush_rate: float = 5):
        self.bind = bind
        super().__init__(fs, tags=tags, flush_rate=flush_rate)

    def _new_cluster(self, idx: int) -> iCluster:
        lbound = self._to_pk_fmt(idx)
        rbound = self._to_pk_fmt(idx + 1)
        cluster = BoundedCluster(self, lbound, rbound, flush_rate=self.flush_rate)
        self.clusters[idx] = cluster
        return cluster

    def _to_pk(self, bind):
        raise NotImplementedError()

    def _to_pk_fmt(self, bind):
        raise NotImplementedError()


class TimeBoundedBook(FixBoundedBook):
    def __init__(
        self, bind: timedelta, fs: iVFS, tags: list = [], flush_rate: float = 5
    ):
        bind = bind.total_seconds()
        super().__init__(bind, fs, tags, flush_rate=flush_rate)

    def _to_bind(self, pk: datetime):
        n = pk.timestamp() / self.bind
        return n

    def _to_pk(self, bind):
        t = bind * self.bind
        dt = datetime.fromtimestamp(t)
        return dt

    def _to_pk_fmt(self, bind):
        dt = self._to_pk(bind)
        return dt.strftime('%Y%m%d_%H%M%S')
