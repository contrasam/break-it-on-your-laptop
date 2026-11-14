"""Lab 04 auditor: did the system recover when the dependency did?

Reads what the load generator saw (/results/run.json) and what the dependency
did (its /stats), then prints a per-second timeline and one verdict line.
"""
import json, os, urllib.request
from collections import Counter

GRACE = float(os.getenv("GRACE", "10"))      # seconds allowed to drain after the dependency recovers
run = json.load(open("/results/run.json"))
m, res = run["meta"], run["results"]
dep = {int(k): v for k, v in json.load(urllib.request.urlopen("http://dep:8081/stats")).items()}
api = [json.load(urllib.request.urlopen(f"http://{h}:8080/stats")) for h in ("api1", "api2")]

t0, dur = m["t0"], m["duration"]
slow_from, slow_to = m["slow_at"], m["slow_at"] + m["slow_for"]
sec0 = int(t0)
arr, ok, att = Counter(), Counter(), Counter()
for a, good, _lat, _n in res:
    arr[int(a)] += 1
    ok[int(a)] += good
for a in run["attempts"]:
    att[int(a)] += 1

print(f"\nretry={m['retry']}  rate={m['rate']:.0f}/s  dependency {m['service_ms']:.0f} ms/call", end="")
if m["slow_for"] > 0:
    print(f", slowed to {m['slow_ms']:.0f} ms from t={slow_from:.0f}s to t={slow_to:.0f}s")
else:
    print(", never slowed")
print(f"\n{'t (s)':>5} {'new':>5} {'ok %':>6} {'client':>7} {'dep in':>7} {'dep done':>9} {'wasted':>7} {'queue':>6}")
for t in range(int(dur)):
    d = dep.get(sec0 + t, {})   # dep counts by wall-clock second, so rows can be off by < 1 s
    mark = " <- slow" if slow_from <= t < slow_to and m["slow_for"] > 0 else ""
    pct = 100 * ok[t] / arr[t] if arr[t] else 0
    print(f"{t:>5} {arr[t]:>5} {pct:>5.0f}% {att[t]:>7} {d.get('received', 0):>7} "
          f"{d.get('completed', 0):>9} {d.get('wasted', 0):>7} {d.get('queue_max', 0):>6}{mark}")

total = len(res)
failed = sum(1 for r in res if not r[1])
dep_in = sum(v.get("received", 0) for v in dep.values())
dep_done = sum(v.get("completed", 0) for v in dep.values())
wasted = sum(v.get("wasted", 0) for v in dep.values())
after = [r for r in res if r[0] >= slow_to + GRACE]
after_failed = sum(1 for r in after if not r[1])
denied = m["budget_denied"] + sum(a["budget_denied"] for a in api)

print(f"\nrequests: {total:,}   failed: {failed:,} ({100 * failed / total:.1f}%)")
print(f"calls reaching the dependency: {dep_in:,} ({dep_in / total:.1f} per request)")
print(f"dependency work wasted (caller had already given up): {wasted:,} of {dep_done:,} completed")
if denied:
    print(f"retries refused by the budget: {denied:,}")
if m["slow_for"] > 0:
    # Recovered = from this second to the end of the run, at least 90% of new requests succeed.
    rec = next((t for t in range(int(slow_to), int(dur))
                if all(ok[u] >= 0.90 * arr[u] for u in range(t, int(dur)))), None)
    if rec is None:
        print(f"the dependency recovered at t={slow_to:.0f}s; the system never did")
    else:
        print(f"the dependency recovered at t={slow_to:.0f}s; the system at t={rec}s ({rec - slow_to:.0f} s later)")
verdict = "FAIL" if after_failed else "PASS"
print(f"{verdict}: {after_failed:,} of {len(after):,} requests failed once the dependency had been healthy for {GRACE:.0f} s\n")
