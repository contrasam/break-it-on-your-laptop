# Break It On Your Laptop

A low-cost ebook plus labs repo. Readers reproduce real distributed-systems
failures on their own laptop with Docker, measure them, then fix them.
Author: Pradeep (13+ years of production firefighting). The voice is that of
an incident responder, not a professor.

The planning doc lives in Claude Docs (positioning, TOC, pricing). This file
is the working contract for the repo.

## Repo layout
- `labs/NN-slug/`: one self-contained lab per chapter
- `book/NN-slug.md`: chapter prose (Markdown, Leanpub-compatible). Gitignored: the book is paid, this repo is public, so chapters never get committed here
- `tools/`: shared helpers (lab runner, result capture), only once 2+ labs need them

## Every lab MUST
1. Run with only Docker + Compose v2.20+, using `make exp1`, `make exp2`, ..., `make fix`.
2. Fit in 4 GB of RAM and finish each experiment in under 60 s by default.
3. End with an auditor that prints one line: `PASS:` or `FAIL: <n> of <m> <thing>`.
4. Expose knobs as env vars (`RATE`, `SKEW_MS`, `KEYS`, `DURATION`, ...) and document them in its README.
5. Ship `AI.md` with three prompts: find the breaking point, vary the experiment, read my results.
6. Use Python for load generators and auditors (readable by everyone) and real infrastructure
   (Postgres, Redis, Kafka, Nginx, Toxiproxy) for the system under test.
7. Pin image tags (e.g. `redis:7-alpine`) and Python deps.

## Every chapter follows this loop
Incident (1 page, postmortem style) → Predict → Break it → Measure (real table from a real run)
→ Explain (min theory, one diagram) → Fix and prove → Going further → Try this
→ In the interview (half page) → Takeaway (one sentence).

## Non-negotiables
- Every number in a chapter comes from an actual run. Paste the auditor output; never estimate.
- Record the machine and run length under each results table.
- No fake urgency or inflated claims anywhere, including the README and landing copy.
- Keep chapters to 3,000–4,500 words.
- Leave a `> Draft note for Pradeep:` marker wherever his real incident story belongs. Don't invent one.

## Chapter plan (status: [x] done, [ ] todo)
Part 1, Time and order
- [x] 01 timestamps-lie: Redis, 3 writers, LWW ties + 5 ms skew → versioned CAS
- [ ] 02 replication-lag: Postgres primary+replica, read-your-writes → LSN tokens
- [ ] 03 kafka-exactly-once: consumer killed mid-batch → idempotency keys + dedupe table
Part 2, Load and overload
- [ ] 04 retry-storms (FREE sample): Nginx + 2 services, slow dep + no backoff → backoff, jitter, retry budget
- [ ] 05 tail-latency: fan-out to 10 backends, 1% slow tail → hedged requests + timeouts
- [ ] 06 queue-collapse: arrival > service rate → backpressure + load shedding
- [ ] 07 connection-pool: slow queries hold the pool → pool sizing, statement timeouts, bulkheads
- [ ] 08 cache-stampede: hot key expiry → request coalescing, early refresh
Part 3, Membership and partitions
- [ ] 09 split-brain: partition the primary via Toxiproxy → quorum writes + fencing tokens
- [ ] 10 gc-pause-leader: `docker pause` the leader past its lease → lease checks + fencing tokens (reuse ch 9)
- [ ] 00 setup chapter, appendix cheat sheet, "write your own lab"

## Next up
1. Run `make exp1 exp2 fix` in labs/01 under Docker and update chapter 1's table with that run.
2. Build lab 04 (retry storms), the second free chapter.
