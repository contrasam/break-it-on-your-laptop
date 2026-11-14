# Break It On Your Laptop

Distributed systems failures you can reproduce, measure and fix, on your own laptop.

Each lab breaks something real, such as last-write-wins, retries or a leader lease, and an
auditor tells you exactly how much damage was done. Then you fix it and prove the number goes to zero.

```bash
cd labs/01-timestamps-lie
make exp1   # perfect clocks, 57% of acknowledged writes silently lost
make fix    # versioned compare-and-set, 0 lost
```

Requires Docker with Compose v2.20+. Fits in 4 GB of RAM.

The book that explains every lab: coming soon on [fbounded.com](https://fbounded.com).

## Labs

| # | Lab | Breaks | Fix |
| --- | --- | --- | --- |
| 01 | [timestamps-lie](labs/01-timestamps-lie) | Last-write-wins under ties and 5 ms clock skew | Versioned compare-and-set |
| 04 | [retry-storms](labs/04-retry-storms) | Naive retries keep a system down after a 5 s slowdown ends | Backoff, jitter and a retry budget |

More labs land as chapters ship.

## License

MIT. Run them, break them, share them.
