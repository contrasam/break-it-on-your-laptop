"""The dependency: it can do WORKERS things at once, each takes SERVICE_MS.

Think of it as a database or a downstream API with a fixed amount of capacity.
Requests beyond WORKERS wait in a queue. Like most servers, it does NOT notice
when a caller gives up: queued work is still done, even if nobody is waiting.
It also fails ERROR_RATE of calls at once (a dropped connection, a node restarting):
the transient errors that retries exist to hide.
The load generator slows it down for a few seconds via POST /admin/slow.
"""
import asyncio, os, random, time
from collections import defaultdict
from aiohttp import web

WORKERS = int(os.getenv("WORKERS", "4"))
service_ms = float(os.getenv("SERVICE_MS", "20"))
ERROR_RATE = float(os.getenv("ERROR_RATE", "0.02"))
sem = asyncio.Semaphore(WORKERS)
stats = defaultdict(lambda: defaultdict(int))   # epoch second -> counters
waiting = 0


async def work(request):
    global waiting
    give_up_at = float(request.headers.get("X-Give-Up-At", "inf"))
    sec = int(time.time())
    stats[sec]["received"] += 1
    if random.random() < ERROR_RATE:
        stats[sec]["errors"] += 1
        return web.Response(status=503, text="transient error")
    waiting += 1
    stats[sec]["queue_max"] = max(stats[sec]["queue_max"], waiting)
    async with sem:
        waiting -= 1
        await asyncio.sleep(service_ms / 1000)
    done = time.time()
    stats[int(done)]["completed"] += 1
    if done > give_up_at:
        stats[int(done)]["wasted"] += 1   # finished after the caller stopped waiting
    return web.Response(text="ok")


async def slow(request):
    global service_ms
    service_ms = float(request.query["ms"])
    return web.Response(text=f"service time now {service_ms} ms")


async def get_stats(request):
    return web.json_response({str(k): v for k, v in stats.items()})


app = web.Application()
app.add_routes([web.get("/work", work), web.post("/admin/slow", slow), web.get("/stats", get_stats)])
web.run_app(app, port=8081, access_log=None, print=None)
