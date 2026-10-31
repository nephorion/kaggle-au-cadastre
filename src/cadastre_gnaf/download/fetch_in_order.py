from collections import deque
from concurrent.futures import ThreadPoolExecutor

WINDOW_PER_WORKER = 8


def fetch_in_order(fetch, start, stop, step, workers, find_next=None):
    """Yield (lo, hi, features) for ObjectID ranges from `start` up to `stop`, in OID order.

    Keeps up to `workers * 8` ranges queued so the workers stay busy: a slow request only delays
    the in-order hand-off, not the other workers (unlike waiting for fixed batches).
    `find_next(at_least)` skips large OID gaps: it is called when a whole window came back empty
    and returns the next existing OID (None = no more).
    """
    window = workers * WINDOW_PER_WORKER
    queue, nxt, empty_run = deque(), start, 0
    pool = ThreadPoolExecutor(workers)
    try:
        while True:
            while len(queue) < window and nxt is not None and nxt <= stop:
                queue.append((nxt, nxt + step, pool.submit(fetch, nxt, nxt + step)))
                nxt += step
            if not queue:
                return
            lo, hi, future = queue[0]
            feats = future.result()
            queue.popleft()
            yield lo, hi, feats
            empty_run = 0 if feats else empty_run + 1
            if find_next and empty_run >= window and nxt is not None and nxt <= stop:
                found = find_next(nxt)
                nxt = None if found is None else max(nxt, int(found))
                empty_run = 0
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
