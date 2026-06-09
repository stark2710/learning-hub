---
title: "Asyncio — Event Loop & async/await"
module: "Concurrency"
domain: "Python Mastery"
lesson_id: "m3-l4-asyncio"
prev: "m3-l3-multiprocessing"
next: "m4-l1-rest-api"
duration: "~55 min"
---

```system_prompt
You are a Python concurrency expert and backend systems architect with 15+ years of experience, including building high-throughput async APIs, event-driven microservices, and distributed data pipelines. The student has 4+ years backend experience (3 years Java, 1+ year Python) and has already completed lessons on the GIL, threading, and multiprocessing.

For this lesson on Asyncio:
- Connect asyncio to what they already know: GIL (m3-l1), threading (m3-l2), multiprocessing (m3-l3), and generators (m2-l3)
- Compare async/await to Java's CompletableFuture and reactive streams (Project Reactor) — they'll recognize the concept
- Be explicit about what "concurrent but single-threaded" means — this is the #1 confusion point
- Show real patterns: web scrapers, API clients, async DB access
- Warn about blocking the event loop — this is the most common production mistake
- Always respond in plain English.
```

## What You'll Learn

- How the event loop works under the hood — the `select`/`epoll` machinery Python sits on top of
- What `async def` actually creates (hint: it's a coroutine object, not a call) and what `await` does at the bytecode level
- When asyncio wins (I/O-bound, thousands of connections) and when it's wrong (CPU-bound tasks)
- How to safely mix blocking code into an async world using `run_in_executor`

---

```narration
Ab hum concurrency module ka last aur sabse powerful lesson cover karne waale hain — asyncio. Yaar, GIL dekha, threading dekha, multiprocessing dekha — ab single thread mein hazaron connections handle karna seekhenge. Yeh Node.js wala concept hai, but Python mein. Aur honestly, yeh samajhna thoda tricky hai, but ek baar mental model click ho jaaye toh sab clear ho jaata hai.
```

## The Mental Model

You've seen the GIL prevent true thread parallelism, and you've seen multiprocessing bypass it with separate processes. Asyncio takes a completely different philosophy: **don't fight the GIL — instead, never waste CPU waiting**.

### The Waiter Analogy

Imagine a restaurant with **one extremely efficient waiter** (single thread) and 100 tables. A bad waiter takes Order 1, goes to the kitchen, stands there waiting for the food, brings it back, then goes to Table 2. That's synchronous blocking.

A smart waiter takes Order 1, submits it to the kitchen, immediately goes to Table 2, takes their order, submits it, goes to Table 3 — and when the kitchen rings a bell saying "Order 1 is ready," the waiter picks it up and delivers it. That waiter is serving 100 tables **concurrently** without any help.

That bell system? That's the **event loop**.

```
┌─────────────────────────────────────────────────────────────┐
│                    THE EVENT LOOP                           │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Ready Queue (coroutines ready to run)                │  │
│  │  [fetch_user(), process_order(), send_email()]        │  │
│  └─────────────────────┬─────────────────────────────────┘  │
│                        │  pick next                         │
│                        ▼                                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Run coroutine until it hits `await`                  │  │
│  │  fetch_user() → "await db.fetch()" → SUSPEND          │  │
│  └─────────────────────┬─────────────────────────────────┘  │
│                        │  suspended, register callback      │
│                        ▼                                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  I/O Poller (select/epoll/kqueue)                     │  │
│  │  "Tell me when db socket has data"                    │  │
│  │  [socket_fd_42, socket_fd_87, socket_fd_103 ...]      │  │
│  └─────────────────────┬─────────────────────────────────┘  │
│                        │  OS says "fd_42 is ready"          │
│                        ▼                                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Wake up fetch_user(), put back in Ready Queue        │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

The event loop never sleeps. It continuously asks the OS: "Which of my registered file descriptors are ready?" The OS is efficient at this — it has `epoll` on Linux which can watch 100,000 sockets with almost zero overhead.

### Java Comparison

If you've used Java's `CompletableFuture` or Spring WebFlux (Project Reactor), this is the same idea. Python's `async/await` ≈ Java's `CompletableFuture.thenCompose()`. The difference is Python's syntax makes the async code *look* like regular synchronous code.

```python
# Python asyncio — looks sequential, runs concurrently
async def get_user_profile(user_id):
    user = await db.fetch_user(user_id)     # suspend here
    posts = await db.fetch_posts(user_id)   # suspend here
    return {"user": user, "posts": posts}

# Java equivalent (much more verbose)
CompletableFuture<UserProfile> getUserProfile(String userId) {
    return db.fetchUser(userId)
        .thenCompose(user -> db.fetchPosts(userId)
            .thenApply(posts -> new UserProfile(user, posts)));
}
```

```narration
Yaar, Java wale ko yeh concept familiar lagega — CompletableFuture ya reactive streams jaisa hi hai. Lekin Python ki beauty yeh hai ki async code bilkul synchronous jaisa dikhta hai. Ek callback hell nahi hai, ek chain of thenApply nahi hai — seedha await likhdo aur kaam ho jaata hai. Isliye Python mein async code likhna aur padhna dono asaan hai.
```

---

## How It Actually Works

### Coroutines: Generators in Disguise

In Lesson m2-l3 (Generators), you learned that `yield` suspends a function and returns control to the caller. Coroutines are **built on exactly that mechanism**.

When you define `async def`, Python creates a coroutine function. Calling it returns a **coroutine object** — the function body hasn't executed at all yet.

```python
import asyncio
import dis

async def greet(name):
    print(f"Hello {name}")
    await asyncio.sleep(1)       # this is the suspension point
    print(f"Goodbye {name}")

# Calling async def does NOT run it
coro = greet("Bharat")
print(type(coro))    # <class 'coroutine'>
print(coro)          # <coroutine object greet at 0x...>

# You have to give it to the event loop
asyncio.run(greet("Bharat"))
```

Let's look at what `await asyncio.sleep(1)` actually does internally:

```python
# asyncio.sleep simplified (not actual source, but the concept)
async def sleep(delay):
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    # Register: "wake up this future in `delay` seconds"
    loop.call_later(delay, future.set_result, None)
    # Yield control back to the event loop
    # This is the actual suspension — "I'm done for now"
    await future   # <-- event loop sees this, suspends the coroutine
```

Under the hood, `await` is syntactic sugar for `yield from`. The coroutine suspends itself by yielding a Future object to the event loop. The event loop sees the future, registers its callback with the OS I/O poller, and moves on to the next ready coroutine.

```python
# CPython bytecode for `await expr` — simplified
# GET_AWAITABLE  <-- get the awaitable from expr
# YIELD_FROM     <-- suspend, give control back to event loop
# (resume when future resolves)
```

### Creating and Running Coroutines

```python
import asyncio
import time

# async def creates a coroutine function
async def fetch_data(url: str, delay: float) -> dict:
    print(f"[{time.strftime('%H:%M:%S')}] Starting fetch: {url}")
    await asyncio.sleep(delay)   # simulates I/O wait
    print(f"[{time.strftime('%H:%M:%S')}] Done: {url}")
    return {"url": url, "data": f"result from {url}"}

async def main():
    # WRONG: sequential — total time = 2 + 3 = 5 seconds
    r1 = await fetch_data("api/users", 2)
    r2 = await fetch_data("api/orders", 3)
    
    # RIGHT: concurrent — total time = max(2,3) = 3 seconds
    r1, r2 = await asyncio.gather(
        fetch_data("api/users", 2),
        fetch_data("api/orders", 3),
    )
    print(r1, r2)

asyncio.run(main())
```

### `asyncio.gather` vs `asyncio.create_task`

These are the two main ways to run multiple coroutines concurrently. They have a subtle but important difference:

```python
import asyncio

async def work(name: str, duration: float):
    print(f"{name}: started")
    await asyncio.sleep(duration)
    print(f"{name}: done after {duration}s")
    return name

async def demo_gather():
    """
    gather() — schedules all coroutines, waits for ALL to complete.
    Returns results in input order, regardless of completion order.
    If any raises, the exception propagates.
    """
    results = await asyncio.gather(
        work("A", 1.0),
        work("B", 2.0),
        work("C", 0.5),
    )
    print(results)   # ['A', 'B', 'C'] — always in original order

async def demo_create_task():
    """
    create_task() — schedules coroutine immediately on the event loop.
    Gives you a Task object you can cancel, add callbacks to, or just await.
    More flexible than gather for fire-and-forget patterns.
    """
    task_a = asyncio.create_task(work("A", 1.0))
    task_b = asyncio.create_task(work("B", 2.0))
    
    # At this point, both tasks are ALREADY running (scheduled)
    # We can do other work here before awaiting
    print("Tasks are running in background...")
    
    result_a = await task_a   # wait for A specifically
    result_b = await task_b   # wait for B specifically
    
    # Or cancel a task if we don't need it anymore
    # task_b.cancel()

asyncio.run(demo_gather())
asyncio.run(demo_create_task())
```

```
Timeline for gather([A=1s, B=2s, C=0.5s]):

t=0.0s  ──── A started, B started, C started
t=0.5s  ────────────────────── C done
t=1.0s  ──────────────────────────── A done
t=2.0s  ────────────────────────────────────── B done
Total: 2.0s  (not 3.5s!)
```

### Error Handling and Task Cancellation

```python
import asyncio

async def risky_operation(n: int):
    if n == 2:
        raise ValueError(f"Operation {n} failed!")
    await asyncio.sleep(0.5)
    return f"result_{n}"

async def handle_partial_failures():
    # return_exceptions=True: collect exceptions as values, don't propagate
    results = await asyncio.gather(
        risky_operation(1),
        risky_operation(2),   # will raise
        risky_operation(3),
        return_exceptions=True
    )
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Task {i+1} failed: {result}")
        else:
            print(f"Task {i+1} succeeded: {result}")

async def timeout_example():
    try:
        # asyncio.timeout (Python 3.11+) or asyncio.wait_for
        async with asyncio.timeout(1.0):    # cancel if > 1 second
            result = await risky_operation(99)  # takes 0.5s, fine
    except asyncio.TimeoutError:
        print("Timed out!")
    
    # Older style:
    try:
        result = await asyncio.wait_for(risky_operation(1), timeout=1.0)
    except asyncio.TimeoutError:
        print("Timed out!")

asyncio.run(handle_partial_failures())
```

### The `run_in_executor` Bridge: Async + Blocking Code

This is critical for production. You *will* encounter libraries that don't have async versions (psycopg2, some SDKs, CPU-heavy code). Never call them directly in async code — you'll block the entire event loop.

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def blocking_db_call(query: str) -> str:
    """Old-style blocking library — can't be awaited."""
    time.sleep(0.5)   # blocks the ENTIRE thread if called directly
    return f"rows for: {query}"

def cpu_heavy_task(n: int) -> int:
    """CPU-bound work — needs a separate process."""
    return sum(i * i for i in range(n))

async def safe_async_main():
    loop = asyncio.get_event_loop()
    
    # Run blocking I/O in a thread pool (doesn't block event loop)
    # None = use default ThreadPoolExecutor
    result = await loop.run_in_executor(
        None,
        blocking_db_call,
        "SELECT * FROM users"
    )
    print(f"DB result: {result}")
    
    # Run CPU-heavy work in a process pool (bypasses GIL)
    with ProcessPoolExecutor() as process_pool:
        result = await loop.run_in_executor(
            process_pool,
            cpu_heavy_task,
            1_000_000
        )
    print(f"CPU result: {result}")

asyncio.run(safe_async_main())
```

```
┌─────────────────────────────────────────────────────┐
│           run_in_executor Flow                      │
│                                                     │
│  Event Loop Thread                                  │
│  ┌──────────────────────────────┐                   │
│  │  async def main():           │                   │
│  │    await run_in_executor(...)│──────┐            │
│  │    # event loop free here!  │      │ submit      │
│  │    # other coroutines run   │      ▼            │
│  └──────────────────────────────┘  Thread Pool     │
│                                    ┌────────────┐  │
│                                    │ blocking() │  │
│                                    │ runs here  │  │
│                                    └────┬───────┘  │
│                                         │ done     │
│  ┌──────────────────────────────┐       │          │
│  │  coroutine resumes with      │◄──────┘          │
│  │  the return value            │                   │
│  └──────────────────────────────┘                   │
└─────────────────────────────────────────────────────┘
```

```narration
Yaar yeh run_in_executor wali baat bahut important hai production mein. Agar tumhare paas koi purani library hai jo async nahi hai — jaise psycopg2 ya koi legacy SDK — usse directly await mat karo. Woh poora event loop block kar dega. run_in_executor ek bridge hai — blocking code ko thread mein bhejo, aur event loop free rehta hai.
```

---

## The Rule

> **Rule:** `async/await` does NOT add parallelism — it adds *cooperative multitasking*. A coroutine runs until it explicitly `await`s something. If it never awaits, it holds the event loop hostage. Always `await` I/O operations. Always offload blocking/CPU work via `run_in_executor`.

> **Rule:** Calling an `async def` function returns a coroutine object — it runs **zero lines** of code until you `await` it or hand it to the event loop via `asyncio.run()`, `asyncio.create_task()`, or `asyncio.gather()`.

---

## Production Story

### The Silent Killer: Blocking the Event Loop

You're on a FastAPI service. It handles 500 requests/second just fine for months. One day a junior developer adds a feature: thumbnail generation using Pillow (a CPU-heavy image library). The service doesn't crash. But latency on *every* endpoint suddenly jumps from 8ms to 800ms. Nobody can figure out why — thumbnail requests are just 2% of traffic.

**The buggy code:**

```python
from fastapi import FastAPI
from PIL import Image
import io

app = FastAPI()

@app.get("/thumbnail/{image_id}")
async def get_thumbnail(image_id: str):
    # Fetch image bytes from S3 (async — fine)
    image_bytes = await s3_client.get_object(image_id)
    
    # MISTAKE: Pillow resize is CPU-heavy and BLOCKING
    # This runs in the event loop thread and FREEZES IT
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail((128, 128))                    # blocks for ~50ms per image
    output = io.BytesIO()
    img.save(output, format="JPEG")
    return output.getvalue()

# During those 50ms of Pillow work:
# - Event loop is completely frozen
# - ALL other requests queue up
# - A service handling 500 req/s means ~25 requests pile up per blocking call
# - Those requests see 50ms+ delays through no fault of their own
```

**Why it's disastrous:** The event loop is single-threaded. When `img.thumbnail()` runs, *no other coroutine can run*. Not health checks, not other users' requests, nothing. At 2% of traffic, with 50ms CPU time each, you're blocking the event loop for 1ms per 100ms cycle on average — causing latency spikes across *all* endpoints.

**The fix:**

```python
from fastapi import FastAPI
from PIL import Image
import io
import asyncio
from concurrent.futures import ProcessPoolExecutor

app = FastAPI()
# Create once at startup, share across requests
process_pool = ProcessPoolExecutor(max_workers=4)

def _resize_image_sync(image_bytes: bytes) -> bytes:
    """Pure function — runs in a separate process."""
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail((128, 128))
    output = io.BytesIO()
    img.save(output, format="JPEG")
    return output.getvalue()

@app.get("/thumbnail/{image_id}")
async def get_thumbnail(image_id: str):
    image_bytes = await s3_client.get_object(image_id)
    
    loop = asyncio.get_event_loop()
    # Offload CPU work to process pool — event loop stays free
    thumbnail_bytes = await loop.run_in_executor(
        process_pool,
        _resize_image_sync,
        image_bytes
    )
    return thumbnail_bytes

# Now during image resizing:
# - Event loop is FREE to handle other requests
# - Pillow runs in a separate process (bypasses GIL too!)
# - Latency on other endpoints: back to 8ms
```

> **Warning:** FastAPI is async at its core. If you write `async def` endpoint handlers but call any blocking code inside without `run_in_executor`, you're degrading the *entire service* for *all users* — not just the slow requests. This comes up in every async Python interview. Know it cold.

```narration
Yaar yeh production story se ek lesson lena — async mein blocking code likhna ek silent killer hai. Service crash nahi hogi, error nahi aayega, but sab slow ho jaayega mysteriously. Jab tum production mein 800ms latency spikes dekhte ho bina kisi obvious reason ke, toh pehle check karo — koi blocking call event loop pe toh nahi chal raha. Yeh debug karna bahut mushkil hota hai kyunki symptoms aur cause alag jagah dikhte hain.
```

---

## Going Deeper

### How the Event Loop Uses `epoll` (Linux)

The event loop doesn't busy-wait. It calls `epoll_wait()` — a Linux system call that blocks the *OS thread* until at least one registered file descriptor is ready. This is wildly efficient.

```python
# Pseudocode of what asyncio's event loop does internally
import select  # Python wrapper around OS I/O multiplexing

class EventLoop:
    def __init__(self):
        self._ready = []     # Callbacks ready to run right now
        self._scheduled = [] # Callbacks scheduled for future time
        self._selector = selectors.DefaultSelector()  # epoll on Linux
    
    def run_forever(self):
        while True:
            # 1. Run all ready callbacks
            ntodo = len(self._ready)
            for _ in range(ntodo):
                handle = self._ready.popleft()
                handle._run()   # runs coroutine until next await
            
            # 2. Calculate how long to wait for I/O
            timeout = self._next_scheduled_timeout()
            
            # 3. Ask OS: which file descriptors are ready?
            # This is where the loop "sleeps" efficiently
            events = self._selector.select(timeout)
            
            # 4. For each ready fd, schedule its callback
            for key, mask in events:
                callback = key.data
                self._ready.append(callback)
            
            # 5. Run scheduled callbacks whose time has come
            self._run_once_scheduled()
```

### Coroutine State Machine

Every `async def` function compiles to a state machine. Each `await` creates a new state. You can see this with `dis`:

```python
import dis
import asyncio

async def simple():
    await asyncio.sleep(1)
    await asyncio.sleep(2)
    return "done"

dis.dis(simple)
# Relevant output:
#   GET_AWAITABLE   (state 0 → waiting for sleep(1))
#   YIELD_VALUE     (suspend, return to event loop)
#   RESUME          (event loop resumes us)
#   GET_AWAITABLE   (state 1 → waiting for sleep(2))
#   YIELD_VALUE     (suspend again)
#   RESUME          (event loop resumes us again)
#   RETURN_VALUE    (return "done")
```

CPython stores the coroutine's local variables and current state in the frame object. When the event loop resumes a coroutine, it reconstructs the exact execution state — same locals, same position in the bytecode.

### `asyncio.Queue` for Producer-Consumer Patterns

In m3-l2 (Threading), you used `queue.Queue`. Asyncio has its own version that doesn't block:

```python
import asyncio

async def producer(queue: asyncio.Queue, n: int):
    for i in range(n):
        item = f"item_{i}"
        await queue.put(item)          # suspends if queue is full
        print(f"Produced: {item}")
        await asyncio.sleep(0.1)       # simulate work
    await queue.put(None)              # sentinel: done

async def consumer(queue: asyncio.Queue, name: str):
    while True:
        item = await queue.get()       # suspends if queue is empty
        if item is None:
            break
        print(f"{name} consumed: {item}")
        await asyncio.sleep(0.3)       # simulate processing
        queue.task_done()

async def main():
    q = asyncio.Queue(maxsize=5)       # bounded: back-pressure!
    
    prod = asyncio.create_task(producer(q, 10))
    cons1 = asyncio.create_task(consumer(q, "Consumer-1"))
    cons2 = asyncio.create_task(consumer(q, "Consumer-2"))
    
    await asyncio.gather(prod, cons1, cons2)

asyncio.run(main())
```

```narration
Asyncio ka Queue pattern bahut useful hai real backends mein — rate limiting, producer-consumer pipelines, request batching. Yeh threading wale Queue se better hai async context mein kyunki yeh event loop ko block nahi karta. Maxsize set karna important hai — back-pressure mechanism hai yeh, warna producer queue flood kar dega.
```

---

## Connecting the Dots

### Looking Back

- **m2-l3 (Generators):** Coroutines *are* generators. `await` is `yield from`. The suspension mechanism is identical — asyncio just adds the event loop layer on top.
- **m3-l1 (GIL):** Asyncio doesn't solve the GIL — it's still single-threaded. But for I/O-bound work, the GIL is irrelevant because we're not running Python bytecode while waiting for I/O.
- **m3-l2 (Threading):** For blocking third-party libraries, asyncio uses thread pools internally (via `run_in_executor`). They complement each other.
- **m3-l3 (Multiprocessing):** For CPU-bound tasks in async code, use `ProcessPoolExecutor` with `run_in_executor`. Best of both worlds.

### Looking Forward

- **m4-l1 (REST API Design):** FastAPI, Starlette, and AIOHTTP are all asyncio-native. Understanding the event loop means you understand *why* FastAPI can handle 10x the requests of sync Flask at the same hardware.
- **m4-l3 (Caching — Redis):** `aioredis` is the async Redis client. Same patterns you'll use today.
- **m4-l4 (Message Queues):** `aiokafka`, `aio-pika` (RabbitMQ) — event-driven architectures lean heavily on asyncio. A single async consumer can process thousands of messages concurrently.
- **m5-l3 (Distributed Systems):** Async is how modern services achieve the concurrency needed at scale without proportional hardware cost.

---

## Practice

### Exercise 1: Fix the Blocking Event Loop

The following async web scraper has a critical bug. It technically "works" but defeats the entire purpose of asyncio. Find and fix it.

```python
import asyncio
import time
import httpx   # async HTTP client (like requests but async)

# Simulated slow parsing function (CPU-ish work)
def parse_html(html: str) -> list[str]:
    time.sleep(0.2)   # simulating heavy parsing
    return [f"link_{i}" for i in range(5)]

async def scrape_url(client: httpx.AsyncClient, url: str) -> list[str]:
    response = await client.get(url)
    # BUG IS HERE
    links = parse_html(response.text)
    return links

async def scrape_all(urls: list[str]) -> list:
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *[scrape_url(client, url) for url in urls]
        )
    return results

urls = ["https://httpbin.org/delay/0"] * 10
asyncio.run(scrape_all(urls))
```

<details>
<summary>Answer</summary>

**The Bug:** `parse_html()` calls `time.sleep(0.2)` — a blocking call. Even though the HTTP requests are concurrent (via `asyncio.gather`), the parsing of each response blocks the event loop for 200ms. With 10 URLs, that's 2 seconds of pure event loop blocking in serial — despite using async.

**The Fix:** Move `parse_html` to a thread pool via `run_in_executor`. Since it's a CPU-ish task (not GIL-free), thread pool is fine here; for truly heavy CPU work, use ProcessPoolExecutor.

```python
import asyncio
import time
import httpx
from concurrent.futures import ThreadPoolExecutor

thread_pool = ThreadPoolExecutor(max_workers=4)

def parse_html(html: str) -> list[str]:
    time.sleep(0.2)   # blocking, but now runs in thread pool
    return [f"link_{i}" for i in range(5)]

async def scrape_url(client: httpx.AsyncClient, url: str) -> list[str]:
    response = await client.get(url)
    loop = asyncio.get_event_loop()
    # Offload blocking parse to thread pool
    links = await loop.run_in_executor(thread_pool, parse_html, response.text)
    return links

async def scrape_all(urls: list[str]) -> list:
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *[scrape_url(client, url) for url in urls]
        )
    return results

urls = ["https://httpbin.org/delay/0"] * 10
asyncio.run(scrape_all(urls))
# Before fix: ~2s blocking overhead on top of network time
# After fix: parse_html calls run concurrently in thread pool,
#            event loop stays responsive
```

**Key insight:** The `await` before `run_in_executor` means "start this in a thread and suspend until it finishes" — the event loop is free to run other coroutines during that suspension.

</details>

---

### Exercise 2: Implement a Rate-Limited Async Fetcher

Write an async function `fetch_with_rate_limit(urls, max_concurrent)` that:
1. Fetches all URLs concurrently
2. Never makes more than `max_concurrent` requests at the same time
3. Returns results in the same order as input URLs

Use `asyncio.Semaphore`. Don't use any third-party libraries.

```python
import asyncio

async def fake_fetch(url: str) -> str:
    """Simulates an HTTP GET — replace with real httpx call."""
    await asyncio.sleep(0.5)
    return f"result:{url}"

async def fetch_with_rate_limit(urls: list[str], max_concurrent: int) -> list[str]:
    # YOUR CODE HERE
    pass

results = asyncio.run(fetch_with_rate_limit(
    [f"url_{i}" for i in range(20)],
    max_concurrent=3
))
print(results)
```

<details>
<summary>Answer</summary>

```python
import asyncio

async def fake_fetch(url: str) -> str:
    await asyncio.sleep(0.5)
    return f"result:{url}"

async def fetch_with_rate_limit(urls: list[str], max_concurrent: int) -> list[str]:
    # Semaphore is a counter — allows at most `max_concurrent` 
    # coroutines inside the `async with` block simultaneously
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def fetch_one(url: str) -> str:
        async with semaphore:   # blocks (suspends) if counter is 0
            # Counter decremented: we hold one slot
            return await fake_fetch(url)
            # Counter incremented on exit: slot released
    
    # gather preserves ORDER of results — key requirement!
    results = await asyncio.gather(*[fetch_one(url) for url in urls])
    return list(results)

results = asyncio.run(fetch_with_rate_limit(
    [f"url_{i}" for i in range(20)],
    max_concurrent=3
))
print(results)
# url_0 through url_19, in order, fetched 3 at a time
# Total time: ceil(20/3) * 0.5s = 4s  (vs 10s sequential)

# How Semaphore works:
# - Initial count: 3
# - url_0, url_1, url_2 acquire → count = 0
# - url_3 tries to acquire → suspends (count is 0!)
# - url_0 completes → count = 1 → url_3 wakes up
# - Exactly 3 in-flight at all times
```

**Why `asyncio.Semaphore` and not `threading.Semaphore`?**
`threading.Semaphore` uses OS-level blocking — the thread sleeps. `asyncio.Semaphore` suspends the *coroutine* — the thread (event loop) stays free to run other coroutines. Always use async-native primitives inside async code.

</details>

---

## Study Notes

**Q: What's the actual difference between `asyncio.gather` and `asyncio.create_task`?**
Both schedule coroutines concurrently. `create_task` schedules immediately and returns a `Task` handle you can cancel, add callbacks to, or query for status independently. `gather` is a convenience wrapper that schedules all at once and waits for all of them, returning results in input order. Use `create_task` when you need control over individual tasks; use `gather` when you just want "run all these and give me all the results."

**Q: Does asyncio make Python faster than threaded Java services?**
Not inherently — asyncio's advantage is *concurrency with low memory overhead*. A Java thread stack is ~512KB by default; an asyncio coroutine's frame object is a few hundred bytes. So Python asyncio can handle 100,000 concurrent I/O operations in the same memory that 1,000 Java threads would use. For CPU-heavy work, Java's threads (or Python's multiprocessing) will still win.

**Q: Can I use asyncio with Django?**
Django has limited async support (Django 3.1+ allows `async def` views), but it was built on a synchronous foundation. For fully async Python web services, FastAPI (built on Starlette + asyncio) or AIOHTTP are the right tools. Mixing sync Django ORM calls inside async views will block the event loop unless you use `sync_to_async()` from `asgiref`.

**Q: What happens if I forget `await` on an async function call?**
You get a coroutine object that never runs — Python will show a `RuntimeWarning: coroutine 'xyz' was never awaited`. This is a common mistake coming from Java where calling a method executes it immediately. In asyncio, calling `async_func()` is just creating the coroutine object. You must `await` it, `gather` it, or `create_task` it. Always.

**Q: Is asyncio the same as non-blocking I/O in Java NIO?**
Conceptually yes — both use OS-level I/O multiplexing (epoll/kqueue/IOCP) to handle many connections on few threads. Java NIO uses Selectors (which wrap epoll) and callback-based `ChannelHandlers`. Python asyncio wraps the same OS primitives but gives you `async/await` syntax that reads like synchronous code, avoiding the callback complexity of raw NIO. Netty (Java) and asyncio solve the same problem; the ergonomics differ.