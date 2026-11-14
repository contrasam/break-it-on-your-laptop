# Lab 04: Retry storms

A client sends 100 requests per second through Nginx to two `api` replicas.
Each `api` call needs one call to `dep`, a dependency that can do 4 things at once
at 20 ms each: 200 calls per second of capacity, so it runs at about half load.
`dep` also fails 2% of calls at once, the kind of transient error retries are for.

Five seconds in, `dep` slows to 100 ms per call for five seconds, then goes back to normal.
The question the auditor answers: **when the dependency recovers, does the system?**

```
loadgen ──► nginx ──► api1 ─┐
 (retries)            api2 ─┴──► dep  (4 workers, 20 ms, 2% errors)
                    (retries)
```

Both the client and the `api` time out and retry. Neither `api` nor `dep` notices when its
caller gives up, as with most web frameworks, so abandoned work is still done.

Requires: Docker with Compose v2.20+.

| Command     | What happens                                             |
|-------------|----------------------------------------------------------|
| `make exp1` | Healthy dependency, naive (immediate) retries            |
| `make exp2` | Dependency slow for 5 s, naive retries                   |
| `make exp3` | Same slowdown, exponential backoff with full jitter      |
| `make fix`  | Same slowdown, backoff + jitter + a 10% retry budget     |

Each run lasts 30 s. The auditor prints a per-second timeline, then:

- how many calls reached the dependency per request (amplification),
- how much of the dependency's work finished after its caller had already given up (wasted),
- when the system recovered compared with the dependency,
- `PASS:` or `FAIL: <n> of <m> requests failed once the dependency had been healthy for 10 s`.

## Knobs (env vars)

| Variable | Default | Meaning |
| --- | --- | --- |
| `RATE` | 100 | New requests per second (open loop: they keep coming) |
| `DURATION` | 30 | Seconds of load |
| `RETRY` | per target | `none`, `naive`, `backoff` or `budget` (use with `make run`) |
| `CLIENT_TIMEOUT_MS` | 1000 | Client timeout per attempt |
| `CLIENT_RETRIES` | 2 | Client retries after the first attempt |
| `API_TIMEOUT_MS` | 300 | `api` timeout per call to `dep` |
| `API_RETRIES` | 2 | `api` retries after the first call |
| `BUDGET` | 0.1 | With `budget`: retries allowed per request, on average |
| `WORKERS` | 4 | Calls `dep` can work on at once |
| `SERVICE_MS` | 20 | Normal time per `dep` call |
| `ERROR_RATE` | 0.02 | Share of `dep` calls that fail at once |
| `SLOW_AT` | 5 | When the slowdown starts (s) |
| `SLOW_FOR` | 5 | How long it lasts (s); 0 = never slow |
| `SLOW_MS` | 100 | Time per `dep` call while slow |
| `GRACE` | 10 | Seconds after recovery before the auditor counts failures |

Examples:

```bash
make run RETRY=none SLOW_FOR=5      # no retries at all: what do you lose, what do you gain?
make exp2 SLOW_FOR=1                # is a 1-second blip enough to start a storm?
make fix BUDGET=0.5                 # how generous can the budget be before it stops working?
```

## Things to try

1. Turn on Nginx's own retries: in `nginx.conf`, set `proxy_next_upstream error timeout http_503;`
   and `proxy_read_timeout 1s;`. That is a third layer. What happens to calls per request?
2. Make `dep` drop work whose caller has already given up: check `X-Give-Up-At` before
   doing the work. How much faster does `make fix` recover?
3. Retry at one layer only: run `make exp2 API_RETRIES=0`. Is the storm smaller, or gone?

Full explanation: chapter 4 of the book.
