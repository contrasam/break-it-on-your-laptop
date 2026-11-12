# break-it-on-your-laptop (public labs)

Hands-on labs for the book *Break It On Your Laptop*. Each lab reproduces a real
distributed-systems failure with Docker, measures it, then proves a fix.
The book's manuscript lives in a separate private repo; keep chapter prose out of this one.

## Every lab MUST
1. Run with only Docker + Compose v2.20+, using `make exp1`, `make exp2`, ..., `make fix`.
2. Fit in 4 GB of RAM and finish each experiment in under 60 s by default.
3. End with an auditor that prints one line: `PASS:` or `FAIL: <n> of <m> <thing>`.
4. Expose knobs as env vars (`RATE`, `SKEW_MS`, `KEYS`, `DURATION`, ...) and document them in its README.
5. Ship `AI.md` with three prompts: find the breaking point, vary the experiment, read my results.
6. Use Python for load generators and auditors and real infrastructure (Postgres, Redis, Kafka,
   Nginx, Toxiproxy) for the system under test.
7. Pin image tags and Python deps.
8. Add a row to the Labs table in the root README.

Layout: `labs/NN-slug/` with `docker-compose.yml`, `Makefile`, `README.md`, `AI.md`, and the scripts.
