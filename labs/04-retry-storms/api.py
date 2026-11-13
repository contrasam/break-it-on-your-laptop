"""The api service: Nginx sends it requests, and it calls the dependency.

Each call to the dependency has a timeout (API_TIMEOUT_MS). On a timeout or an
error it retries according to RETRY (see retry.py). If the client hangs up, this
handler keeps going, as most web frameworks do by default.
"""
import asyncio, os, time
from aiohttp import web, ClientSession, ClientTimeout, TCPConnector
from retry import Policy

DEP = os.getenv("DEP_URL", "http://dep:8081/work")
TIMEOUT = float(os.getenv("API_TIMEOUT_MS", "300")) / 1000
policy = Policy(os.getenv("RETRY", "naive"), int(os.getenv("API_RETRIES", "2")),
                base_ms=50, cap_ms=500, budget_ratio=float(os.getenv("BUDGET", "0.1")))
stats = {"requests": 0, "attempts": 0, "ok": 0, "failed": 0}


async def handle(request):
    s = request.app["session"]
    stats["requests"] += 1
    policy.on_request()
    attempt = 0
    while True:
        attempt += 1
        stats["attempts"] += 1
        try:
            hdr = {"X-Give-Up-At": str(time.time() + TIMEOUT)}
            async with s.get(DEP, headers=hdr, timeout=ClientTimeout(total=TIMEOUT)) as r:
                if r.status == 200:
                    stats["ok"] += 1
                    return web.Response(text="ok")
        except (asyncio.TimeoutError, OSError):
            pass
        if not policy.may_retry(attempt):
            stats["failed"] += 1
            return web.Response(status=503, text="dependency unavailable")
        await asyncio.sleep(policy.delay(attempt))


async def get_stats(request):
    return web.json_response({**stats, "budget_denied": policy.denied})


async def start(app):
    app["session"] = ClientSession(connector=TCPConnector(limit=0))


app = web.Application()
app.on_startup.append(start)
app.add_routes([web.get("/work", handle), web.get("/stats", get_stats)])
web.run_app(app, port=8080, access_log=None, print=None)
