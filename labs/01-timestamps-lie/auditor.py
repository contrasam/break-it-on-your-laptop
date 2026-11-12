"""Lab 01 auditor: how many writes were acknowledged but never survived?"""
import os
import redis

r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")), decode_responses=True)
s = {k: int(v) for k, v in r.hgetall("stats").items()}
writers = sorted({k.split(":")[1] for k in s})
dur = float(os.getenv("DURATION", "20"))

tot_acked = tot_lost = 0
print(f"\n{'writer':<8}{'acked':>10}{'applied':>10}{'lost':>10}{'tie':>8}{'older':>8}{'loss %':>8}")
for w in writers:
    acked, applied = s.get(f"acked:{w}", 0), s.get(f"applied:{w}", 0)
    tie, older = s.get(f"drop_tie:{w}", 0), s.get(f"drop_older:{w}", 0)
    lost = acked - applied
    tot_acked += acked; tot_lost += lost
    pct = 100 * lost / acked if acked else 0
    print(f"{w:<8}{acked:>10,}{applied:>10,}{lost:>10,}{tie:>8,}{older:>8,}{pct:>7.1f}%")

print(f"\nthroughput: {tot_acked / dur:,.0f} writes/s")
retries = sum(v for k, v in s.items() if k.startswith("retries:"))
if retries:
    print(f"conflicts detected and retried: {retries:,}")
verdict = "FAIL" if tot_lost else "PASS"
print(f"{verdict}: {tot_lost:,} of {tot_acked:,} acknowledged writes were silently lost\n")
