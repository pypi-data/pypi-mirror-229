"""Main module."""
# import base64
import asyncio
import json
import sys
import traceback

# import os

# import yaml

from asyncio import sleep
from datetime import datetime

from select import select
from typing import Union, List, Dict, Tuple, Any

# from anyio import wrap_file, run

from dateutil.parser import parse

from .filesystem import iVFS

# ----------------------------------------------------------
# loggers
# ----------------------------------------------------------
from pycelium.tools.logs import logger

log = logger(__name__)

# ----------------------------------------------------------
# Record
# ----------------------------------------------------------
RECORD_HASH = "_hash_"
RECORD_PK = "_pk_"
RECORD_TIMESTAMP = "_ts_"
RECORD_TOPIC = "topic"
RECORD_RAW = "raw"
RECORD_PAYLOAD = "payload"
RECORD_RETAIN = "retain"
RECORD_URI = "uri"

RECORD_KEYS = (
    RECORD_PK,
    RECORD_TIMESTAMP,
    RECORD_URI,
    RECORD_RETAIN,
    RECORD_TOPIC,
    RECORD_RAW,
)


class Record(dict):
    """Base Class for any record that may be stored in an
    Incremental Book.
    """

    ORDER: List = []

    @classmethod
    def set_order(cls, order: Union[List, Dict, Tuple]) -> None:
        """Set the render order for all record of the same class."""
        cls.ORDER = [RECORD_PK, RECORD_TIMESTAMP, RECORD_TOPIC] + list(order)

    def __init__(self, *args, **kw):
        self["_ts_"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
        super().__init__(*args, **kw)

    def items(self):
        keys = list(self.keys())
        for key in self.ORDER:
            if key in self:
                yield key, self[key]
                keys.remove(key)

        for key in keys:
            yield key, self[key]


# ----------------------------------------------------------
# Cluster
# ----------------------------------------------------------


# class Book:
# """ahead pre-definition for annotations."""


class iCluster:
    """Data Partition of Book.
    Handles writing records to iVFS.
    """

    def __init__(self, book: "Book", lbound: Any, rbound: Any, flush_rate: float = 5):
        self.book = book
        self.lbound = lbound
        self.rbound = rbound

        # TODO: check rename file (due last PK mismatch) before serving it.
        self.pointer = self.get_fd()
        self.flush = getattr(self.pointer, "flush", None)

        self.flush_pending = False
        self.flush_rate = flush_rate

    def get_fd(self, mode="a", **kw):
        tags = self.book.tags
        return self.book.fs.open(tags, self.lbound, self.rbound, mode=mode, **kw)

    def add(self, record: Record):
        """Add record to cluster in CSV format"""
        try:
            out = self.book.encoder.encode(record)
            self.pointer.write(out)
            if self.flush:
                if not self.flush_pending:
                    loop = asyncio.get_running_loop()
                    loop.call_later(self.flush_rate, self.do_flush)
                    self.flush_pending = True

        except Exception as why:
            print(why)
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)

    def do_flush(self):
        self.flush()
        self.flush_pending = False


# ----------------------------------------------------------
# Encoders
# ----------------------------------------------------------
class Encoder:
    """Encoders"""

    PK_FIELD = RECORD_PK

    @classmethod
    def encode(cls, record: Record) -> str:
        raise NotImplementedError()

    @classmethod
    def decode(cls, raw):
        raise NotImplementedError()


class RawCSV(Encoder):
    """Store Raw info, encapsulating all message in a 'payload' field"""

    PK_FIELD = RECORD_PK

    @classmethod
    def encode(cls, record: Record) -> str:
        values = [record[key] for key in RECORD_KEYS]
        # TODO: use other separator to avoid conflict with ultralight format
        result = "|".join([str(v) for v in values]) + "\n"
        return result

    @classmethod
    def decode(cls, raw):
        data = raw.split("|")
        record = {key: data[i] for i, key in enumerate(RECORD_KEYS)}
        record[RECORD_PAYLOAD] = json.loads(record.pop(RECORD_RAW))
        record[RECORD_PK] = parse(record[RECORD_PK])
        return record


# ----------------------------------------------------------
# Book
# ----------------------------------------------------------
class iBook:
    """Interface for Incremental Book"""

    def __init__(
        self, fs: iVFS, tags: list = [], flush_rate: float = 5, encoder=RawCSV
    ):
        assert isinstance(fs, iVFS)
        self.fs = fs
        self.tags = tags
        self.clusters = {}
        self.flush_rate = flush_rate
        self.last_cluster = None
        self.encoder = encoder

    def add(self, record: Record):
        """Add record to Book"""
        self.last_cluster = self.find_cluster(record)
        self.last_cluster.add(record)
        log.debug(f"{self}: cluster: {self.last_cluster}: add record: {record}")

    def find_cluster(self, record: Record) -> iCluster:
        idx = self._find_idx_cluster(record)
        cluster = self.clusters.get(idx)
        if cluster is None:
            cluster = self._new_cluster(idx)
        return cluster

    def _find_idx_cluster(self, record: Record):
        """Add record to Book"""
        pk = record[RECORD_PK]
        bind = self._to_bind(pk)
        idx = int(bind)
        return idx

    def _new_cluster(self, idx: int) -> iCluster:
        raise NotImplementedError()

    def _to_bind(self, pk):
        raise NotImplementedError()

    def close(self):
        self.running = False
        if self.last_cluster:
            self.last_cluster.flush()

    async def subscribe(self, since=None, idle=0.25):
        self.running = True
        PK = self.encoder.PK_FIELD
        current_cluster, file = None, None
        while self.running:
            if file:
                rx, _, ex = select([file], [], [file], 0.0)
                if rx:
                    raw = file.readline()
                    if raw:
                        record = self.encoder.decode(raw)
                        if not since or since < record[PK]:
                            yield record
                        continue
            if current_cluster != self.last_cluster:
                file = self.last_cluster.get_fd(mode="r")
                current_cluster = self.last_cluster
                continue

            await sleep(idle)
            # await sleep(random.random() * 10)


class Book(iBook):
    """Interface for Incremental Book"""
