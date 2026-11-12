# Lab 01 — Timestamps lie at 10k req/s

Three writers update 10 hot keys as fast as they can. Redis keeps whichever
write has the newest timestamp (last-write-wins). Every caller is told "saved".
The auditor counts how many of those "saved" writes actually survived.

Requires: Docker with Compose v2.20+ (for `docker compose wait`).

| Command     | What happens                                   |
|-------------|------------------------------------------------|
| `make exp1` | Perfect clocks, last-write-wins                |
| `make exp2` | Writer C's clock runs 5 ms behind              |
| `make fix`  | Same skew, versioned compare-and-set           |

Knobs (env vars): `DURATION` (s, default 20), `KEYS` (default 10),
`THREADS` per writer (default 8), `SKEW_C` (ms), `MODE` (`lww` | `cas`).

Try: `make exp1 KEYS=10000` — spread the load and watch losses fall to about 0.1%. Not zero.
Then ask yourself why your production hot keys don't get that luxury.

Full explanation: chapter 1 of the book.

No Docker? Run Redis on 6379, then start `writer.py` three times with
`WRITER_ID=A/B/C SKEW_MS=...` and run `auditor.py`.
