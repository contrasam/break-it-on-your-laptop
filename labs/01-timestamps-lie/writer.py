"""Lab 01 writer: hammers a few hot keys with updates.

MODE=lww  -> last-write-wins by the writer's own wall-clock timestamp (ms)
MODE=cas  -> versioned compare-and-set; the server's version decides, not clocks

Every write is acknowledged to the "caller" (counted in acked:<writer>).
Redis records which writes actually survived, so the auditor can tell
you how many acknowledged writes were silently thrown away.
"""
import os, random, threading, time
import redis

HOST = os.getenv("REDIS_HOST", "localhost")
PORT = int(os.getenv("REDIS_PORT", "6379"))
WRITER = os.getenv("WRITER_ID", "A")
SKEW_MS = int(os.getenv("SKEW_MS", "0"))        # how wrong this machine's clock is
MODE = os.getenv("MODE", "lww")
KEYS = int(os.getenv("KEYS", "10"))             # few keys = hot keys = contention
THREADS = int(os.getenv("THREADS", "8"))
DURATION = float(os.getenv("DURATION", "20"))

# Last-write-wins, the way most "updated_at" columns behave.
# Ties go to whoever is already stored (">" not ">="), as many systems do.
LWW = """
local cur = redis.call('HGET', KEYS[1], 'ts')
local ts = tonumber(ARGV[1])
if cur and ts < tonumber(cur) then
  redis.call('HINCRBY', 'stats', 'drop_older:' .. ARGV[2], 1)
  return 0
end
if cur and ts == tonumber(cur) then
  redis.call('HINCRBY', 'stats', 'drop_tie:' .. ARGV[2], 1)
  return 0
end
redis.call('HSET', KEYS[1], 'ts', ts, 'writer', ARGV[2])
redis.call('HINCRBY', 'stats', 'applied:' .. ARGV[2], 1)
return 1
"""

# Compare-and-set on a server-side version number. Clocks are never consulted.
CAS = """
local cur = tonumber(redis.call('HGET', KEYS[1], 'ver') or '0')
if cur ~= tonumber(ARGV[1]) then return -1 end
redis.call('HSET', KEYS[1], 'ver', cur + 1, 'writer', ARGV[2])
redis.call('HINCRBY', 'stats', 'applied:' .. ARGV[2], 1)
return 1
"""

def now_ms():
    return time.time_ns() // 1_000_000 + SKEW_MS

def worker(stop):
    r = redis.Redis(host=HOST, port=PORT)
    lww, cas = r.register_script(LWW), r.register_script(CAS)
    acked = retries = 0
    while not stop.is_set():
        key = f"k:{random.randrange(KEYS)}"
        if MODE == "lww":
            lww(keys=[key], args=[now_ms(), WRITER])
        else:
            while True:
                ver = int(r.hget(key, "ver") or 0)
                if cas(keys=[key], args=[ver, WRITER]) == 1:
                    break
                retries += 1          # conflict is visible, so we retry
        acked += 1                    # the caller was told "saved"
    r.hincrby("stats", f"acked:{WRITER}", acked)
    r.hincrby("stats", f"retries:{WRITER}", retries)

if __name__ == "__main__":
    stop = threading.Event()
    ts = [threading.Thread(target=worker, args=(stop,)) for _ in range(THREADS)]
    for t in ts: t.start()
    time.sleep(DURATION)
    stop.set()
    for t in ts: t.join()
    print(f"writer {WRITER} done (mode={MODE}, skew={SKEW_MS}ms)")
