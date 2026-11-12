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
