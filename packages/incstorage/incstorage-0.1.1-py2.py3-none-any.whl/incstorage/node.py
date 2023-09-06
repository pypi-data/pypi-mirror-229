import json
import sys
import pickle

from typing import Any, List


from .incstorage import Book, RECORD_PK, RECORD_PAYLOAD, RECORD_RAW
from .agent import Agent

# ----------------------------------------------------------
# loggers
# ----------------------------------------------------------
from pycelium.tools.logs import logger

log = logger(__name__)


# ----------------------------------------------------------
# Node
# ----------------------------------------------------------
class Node(Agent):
    """A processor with multiples input sources and a single
    output stream.

    input data may hay different keys (i.e. timestamps) but
    somehow we need to process them as if they where generated
    at the same moment.

    To archive this, we split input stream to match the keys
    received and interpolate data to figure out what value
    may have at that particular key.

    We only interpolate float results, not Integers of booleans.
    """

    def __init__(self, sources: List[Book], target: Book, processor: Any = None):
        super().__init__()

        self.sources = sources
        self.target = target
        self.processor = processor
        self.running = False
        self.input = []

    async def main(self, since=None, max_records=sys.float_info.max):
        await super().main()
        assert self.running

        # create async generators
        streams = [book.subscribe(since=since) for book in self.sources]
        PK_FIELD = [book.encoder.PK_FIELD for book in self.sources]

        def new_holder():
            holder = [None] * len(self.sources)
            return holder

        def borders(holder):
            return [record[PK_FIELD[i]] for i, record in enumerate(holder)]

        def argmin(sequence):
            current = None
            best = None
            for i, value in enumerate(sequence):
                if current is None or value < current:
                    best, current = i, value

            return best, current

        def interpolate_row(holder0, holder1, min0):
            row = []
            for i, record0 in enumerate(holder0):
                record1 = holder1[i]
                result = interpolate(record0, record1, min0)
                row.append(result)

            # for record0 in holder0:
            # record0['pk'] = min0
            return row

        def interpolate(record0, record1, x):
            result = pickle.loads(pickle.dumps(record0))
            pk0, pk1 = record0[RECORD_PK], record1[RECORD_PK]
            delta = pk1 - pk0
            f = (x - pk0) / delta
            if f < 0:
                # there is no data for this input. Default POLICY
                # is returning first known record values instead NAN
                f = 0
            payload, payload0, payload1 = (
                result[RECORD_PAYLOAD],
                record0[RECORD_PAYLOAD],
                record1[RECORD_PAYLOAD],
            )

            # 'shift' record0 --> f ---> record1
            for key, value0 in payload0.items():
                if isinstance(value0, (float,)) or key in ("clock",):
                    value1 = payload1[key]
                    assert isinstance(value1, (float,)) or key in ("clock",)
                    value = value1 * f + value0 * (1 - f)
                    value = value1.__class__(value)
                    payload[key] = value

            result[RECORD_PK] = x
            return result

        def check():
            holder0, holder1 = self.input[0], self.input[1]
            for i in range(len(streams)):
                keys0 = list(holder0[i]["payload"].keys())
                keys1 = list(holder1[i]["payload"].keys())
                assert keys0 == keys1, f"record payload {i} have different struct!"

        # setup input streams
        if max_records <= 0:
            return

        # get 1st values for all input sources
        # 1st and 2nd complete rows
        holder0 = new_holder()
        holder1 = new_holder()
        self.input.append(holder0)
        self.input.append(holder1)
        # fill with the next data
        for j in range(2):
            for i, stream in enumerate(streams):
                self.input[j][i] = await anext(stream)

        self.last_read = holder0

        # loop
        n = 0
        processor = self.processor
        target = self.target

        while self.running:
            # border0 = borders(holder0)
            # fetch new data when input source is exhausted
            border1 = borders(holder1)
            idx, min1 = argmin(border1)
            # min0 = border0[idx]
            check()
            result = interpolate_row(holder0, holder1, min1)
            check()

            fetch = 0
            for i, record1 in enumerate(holder1):
                assert record1[RECORD_PK] >= min1
                if record1[RECORD_PK] == min1:
                    holder0[i] = holder1[i]
                    stream = streams[i]
                    holder1[i] = await anext(stream)
                    fetch += 1

            assert fetch, "almost one stream have to be fetched on every cycle..."

            # process interpolated event
            payloads = [record[RECORD_PAYLOAD] for record in result]

            if processor and target:
                payload = processor(payloads)
                sample = result[0]
                # record = pickle.loads(pickle.dumps(sample))
                record = sample.__class__(sample)
                record[RECORD_PAYLOAD] = payload
                # TODO: use CSV encoders instead RawCSV ones
                record[RECORD_RAW] = json.dumps(payload)
                target.add(record)

            n += 1
            max_records -= 1
            if not self.running or max_records <= 0:
                break
