"""Load generator: RATE new requests per second, whatever happens.

Arrivals are open-loop (Poisson), like real users: a slow system does not make
people stop clicking. Each request goes to Nginx with a timeout
(CLIENT_TIMEOUT_MS) and is retried according to RETRY. At SLOW_AT seconds the
dependency slows to SLOW_MS per call for SLOW_FOR seconds, then goes back to normal.
"""
import asyncio, json, os, random, time
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from retry import Policy

URL = os.getenv("TARGET", "http://nginx/work")
DEP_ADMIN = os.getenv("DEP_ADMIN", "http://dep:8081/admin/slow")
RATE = float(os.getenv("RATE", "100"))
DURATION = float(os.getenv("DURATION", "30"))
TIMEOUT = float(os.getenv("CLIENT_TIMEOUT_MS", "1000")) / 1000
SLOW_AT = float(os.getenv("SLOW_AT", "5"))
SLOW_FOR = float(os.getenv("SLOW_FOR", "5"))
SLOW_MS = float(os.getenv("SLOW_MS", "100"))
SERVICE_MS = float(os.getenv("SERVICE_MS", "20"))
policy = Policy(os.getenv("RETRY", "naive"), int(os.getenv("CLIENT_RETRIES", "2")),
                base_ms=100, cap_ms=1000, budget_ratio=float(os.getenv("BUDGET", "0.1")))
results = []                 # (arrival offset s, ok, latency s, attempts)
attempt_times = []           # offset of every attempt sent


async def one_request(s, t0):
    arrived = time.time()
    policy.on_request()
    attempt = 0
    while True:
        attempt += 1
        attempt_times.append(time.time() - t0)
        try:
            async with s.get(URL, timeout=ClientTimeout(total=TIMEOUT)) as r:
                await r.read()
                if r.status == 200:
                    results.append((arrived - t0, 1, time.time() - arrived, attempt))
                    return
        except (asyncio.TimeoutError, OSError):
            pass
        if not policy.may_retry(attempt):
            results.append((arrived - t0, 0, time.time() - arrived, attempt))
            return
        await asyncio.sleep(policy.delay(attempt))


async def set_dep_speed(s, ms):
    async with s.post(DEP_ADMIN, params={"ms": str(ms)}) as r:
        await r.read()


async def chaos(s, t0):
    if SLOW_FOR <= 0:
        return
    await asyncio.sleep(max(0, t0 + SLOW_AT - time.time()))
    await set_dep_speed(s, SLOW_MS)
    await asyncio.sleep(SLOW_FOR)
    await set_dep_speed(s, SERVICE_MS)


async def main():
    async with ClientSession(connector=TCPConnector(limit=0)) as s:
        for _ in range(50):                       # wait for the stack to come up
            try:
                async with s.get(URL, timeout=ClientTimeout(total=2)) as r:
                    if r.status == 200:
                        break
            except Exception:
                pass
            await asyncio.sleep(0.2)
        await set_dep_speed(s, SERVICE_MS)
        t0 = time.time()
        tasks = [asyncio.create_task(chaos(s, t0))]
        next_at = t0
        while next_at < t0 + DURATION:
            await asyncio.sleep(max(0, next_at - time.time()))
            tasks.append(asyncio.create_task(one_request(s, t0)))
            next_at += random.expovariate(RATE)
        await asyncio.gather(*tasks)
    meta = dict(t0=t0, duration=DURATION, rate=RATE, slow_at=SLOW_AT, slow_for=SLOW_FOR,
                slow_ms=SLOW_MS, service_ms=SERVICE_MS, retry=policy.mode,
                client_timeout=TIMEOUT, budget_denied=policy.denied)
    with open("/results/run.json", "w") as f:
        json.dump(dict(meta=meta, results=results, attempts=attempt_times), f)
    print(f"load generator done: {len(results)} requests, retry={policy.mode}")


asyncio.run(main())
