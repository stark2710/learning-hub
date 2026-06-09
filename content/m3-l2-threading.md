---
title: "Threading — When It Helps, When It Doesn't"
module: "Concurrency"
domain: "Python Mastery"
lesson_id: "m3-l2-threading"
prev: "m3-l1-gil"
next: "m3-l3-multiprocessing"
duration: "~45 min"
---

```system_prompt
You are a Python expert teaching an experienced Java/backend developer (3 years Java, 1+ year Python).
Always respond in plain English.
This lesson covers Python's threading module — Thread creation, synchronization primitives (Lock, RLock, Semaphore, Condition, Event), and when threading actually helps in Python.
The user has completed the GIL lesson and understands that Python threads are real OS threads but only one executes Python bytecode at a time. They asked in the prior lesson about Java thread comparison — be precise: Java threads truly parallelize on multiple cores, Python threads do not for CPU-bound Python code, but both languages' threads are real OS threads and both benefit from I/O concurrency.
Focus on practical patterns: thread pools, producer-consumer, bounded parallelism, graceful shutdown. Show what breaks without proper synchronization and how to fix it.
```

## What You'll Learn

- How to create and manage threads using `threading.Thread` and `concurrent.futures.ThreadPoolExecutor`
- The five core synchronization primitives: `Lock`, `RLock`, `Semaphore`, `Condition`, and `Event`
- Producer-consumer pattern with `queue.Queue` — the safe way to share data between threads
- How to properly shutdown threads and avoid the "daemon thread" trap

```narration
Yaar, last lesson mein GIL samjha — ab practical threading seekhte hain. Java mein tum ExecutorService aur synchronized blocks use karte ho. Python mein same concepts hain, bas syntax alag hai. Aaj hum dekhenge kab threading kaam karti hai, kab nahi, aur production mein kaise properly use karte hain — thread pools, locks, graceful shutdown, sab kuch.
```

---

## The Mental Model

In Java, you think of threads as parallel workers. In Python, think of threads as **concurrent waiters**.

```
JAVA THREADS                           PYTHON THREADS
──────────────────────────────         ──────────────────────────────
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐       ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│ T1  │ │ T2  │ │ T3  │ │ T4  │       │ T1  │ │ T2  │ │ T3  │ │ T4  │
│ RUN │ │ RUN │ │ RUN │ │ RUN │       │ RUN │ │WAIT │ │WAIT │ │WAIT │
│ CPU │ │ CPU │ │ CPU │ │ CPU │       │ GIL │ │ GIL │ │ GIL │ │ GIL │
└──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘       └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
   │       │       │       │              │       │       │       │
   ▼       ▼       ▼       ▼              ▼       ▼       ▼       ▼
┌─────────────────────────────┐       ┌─────────────────────────────┐
│      4 CPU CORES            │       │      4 CPU CORES            │
│  (true parallelism)         │       │  (only 1 used for bytecode) │
└─────────────────────────────┘       └─────────────────────────────┘
```

But when threads wait on I/O:

```
PYTHON THREADS DURING I/O
────────────────────────────────────────────────────────────────
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│ T1  │ │ T2  │ │ T3  │ │ T4  │
│WAIT │ │WAIT │ │WAIT │ │WAIT │
│ I/O │ │ I/O │ │ I/O │ │ I/O │   ← GIL released, all waiting in parallel
└──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
   │       │       │       │
   ▼       ▼       ▼       ▼
┌─────────────────────────────┐
│      KERNEL (OS)            │
│  handles all waits in       │
│  parallel — no GIL needed   │
└─────────────────────────────┘
```

**Rule:** Use Python threads when your code spends most of its time waiting — network calls, file I/O, database queries, subprocess communication. For CPU-heavy computation, threads don't help.

```narration
Dekho — Java mein 4 threads matlab 4 cores pe kaam. Python mein 4 threads matlab ek core pe bytecode, baaki wait kar rahe hain GIL ke liye. Lekin jab I/O hota hai — network, file, database — toh GIL release ho jaata hai aur sab threads OS kernel mein parallel wait karte hain. Yahi reason hai ki web servers, scrapers, API clients — yeh sab threading se benefit karte hain Python mein bhi.
```

---

## How It Actually Works

### Creating threads — three ways

**Way 1: Direct Thread creation**

```python
import threading
import time

def download_file(url):
    print(f"[{threading.current_thread().name}] Downloading {url}")
    time.sleep(2)  # simulate I/O
    print(f"[{threading.current_thread().name}] Done {url}")

# Create and start threads
t1 = threading.Thread(target=download_file, args=("file1.zip",), name="Downloader-1")
t2 = threading.Thread(target=download_file, args=("file2.zip",), name="Downloader-2")

t1.start()  # thread begins executing
t2.start()

t1.join()   # block until t1 finishes
t2.join()   # block until t2 finishes

print("All downloads complete")
```

`start()` spawns the OS thread. `join()` blocks the calling thread until the target thread finishes. Forgetting `join()` means your main program might exit before threads complete.

**Way 2: Subclassing Thread**

```python
class DownloaderThread(threading.Thread):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.result = None
    
    def run(self):
        # This method runs in the new thread
        print(f"Downloading {self.url}")
        time.sleep(2)
        self.result = f"Content of {self.url}"

t = DownloaderThread("file.zip")
t.start()
t.join()
print(t.result)  # Access result after join
```

Override `run()`, call `start()`. Never call `run()` directly — that runs in the current thread, not a new one.

**Way 3: ThreadPoolExecutor (recommended for most cases)**

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_url(url):
    time.sleep(1)  # simulate network
    return f"Data from {url}"

urls = ["url1", "url2", "url3", "url4", "url5"]

with ThreadPoolExecutor(max_workers=3) as executor:
    # Submit returns a Future object
    futures = {executor.submit(fetch_url, url): url for url in urls}
    
    for future in as_completed(futures):
        url = futures[future]
        try:
            result = future.result()  # blocks until this future is done
            print(f"{url}: {result}")
        except Exception as e:
            print(f"{url} failed: {e}")
```

`ThreadPoolExecutor` manages thread lifecycle, limits concurrency, and handles exceptions cleanly. The `with` block ensures proper shutdown.

```narration
Teen tarike hain threads banane ke. Direct Thread creation — simple, lekin tum khud manage karte ho. Subclass karna — jab state rakhna ho. ThreadPoolExecutor — production mein yahi use karo. Java ka ExecutorService exactly same concept hai. with block se automatic shutdown hota hai, exceptions properly handle hote hain. Yahi pattern 90% cases mein use hona chahiye.
```

---

### Synchronization primitives

The GIL protects CPython internals, not your data. These primitives protect your shared state.

**Lock — mutual exclusion**

```python
import threading

class BankAccount:
    def __init__(self, balance):
        self.balance = balance
        self.lock = threading.Lock()
    
    def withdraw(self, amount):
        with self.lock:  # acquire lock
            if self.balance >= amount:
                # Simulate some processing time
                time.sleep(0.001)
                self.balance -= amount
                return True
            return False
        # lock automatically released here
    
    def deposit(self, amount):
        with self.lock:
            self.balance += amount

account = BankAccount(1000)

def make_withdrawals():
    for _ in range(100):
        account.withdraw(10)

threads = [threading.Thread(target=make_withdrawals) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()

print(account.balance)  # Always consistent with Lock
```

Without the lock, multiple threads could pass the `if self.balance >= amount` check simultaneously and withdraw more than available.

**RLock — reentrant lock**

```python
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []
        self.lock = threading.RLock()  # RLock, not Lock
    
    def add_child(self, child):
        with self.lock:
            self.children.append(child)
    
    def total_value(self):
        with self.lock:  # acquired first time
            total = self.value
            for child in self.children:
                total += child.total_value()  # child.total_value() also acquires lock
            return total  # if child == self (cycle), RLock allows re-entry
```

A regular `Lock` would deadlock if the same thread tries to acquire it twice. `RLock` tracks which thread holds it and allows that thread to re-acquire (incrementing a counter). Java's `synchronized` is reentrant by default — Python's `Lock` is not.

**Semaphore — bounded parallelism**

```python
import threading
import time

# Only 3 concurrent downloads at a time
download_semaphore = threading.Semaphore(3)

def download(url):
    with download_semaphore:  # blocks if 3 threads already inside
        print(f"Downloading {url}")
        time.sleep(2)
        print(f"Done {url}")

# Start 10 downloads, but only 3 run at a time
threads = [threading.Thread(target=download, args=(f"file{i}.zip",)) 
           for i in range(10)]
for t in threads: t.start()
for t in threads: t.join()
```

Semaphore maintains a counter. `acquire()` decrements (blocks if zero), `release()` increments. Use it to limit concurrent access to a resource — database connections, API rate limits, file handles.

**Event — signaling between threads**

```python
import threading
import time

shutdown_event = threading.Event()

def worker():
    while not shutdown_event.is_set():
        print("Working...")
        # Wait with timeout — allows checking shutdown_event periodically
        shutdown_event.wait(timeout=1.0)
    print("Worker shutting down gracefully")

t = threading.Thread(target=worker)
t.start()

time.sleep(3)
print("Sending shutdown signal")
shutdown_event.set()  # all wait() calls return immediately

t.join()
```

`Event` is a simple flag with `set()`, `clear()`, `wait()`, and `is_set()`. Perfect for signaling shutdown or one-time notifications.

**Condition — wait for complex state**

```python
import threading
import time
from collections import deque

class BoundedQueue:
    def __init__(self, maxsize):
        self.queue = deque()
        self.maxsize = maxsize
        self.condition = threading.Condition()
    
    def put(self, item):
        with self.condition:
            while len(self.queue) >= self.maxsize:
                self.condition.wait()  # release lock, wait for notify
            self.queue.append(item)
            self.condition.notify()  # wake up one waiting consumer
    
    def get(self):
        with self.condition:
            while len(self.queue) == 0:
                self.condition.wait()  # release lock, wait for notify
            item = self.queue.popleft()
            self.condition.notify()  # wake up one waiting producer
            return item
```

`Condition` wraps a lock and adds `wait()` / `notify()` / `notify_all()`. `wait()` atomically releases the lock and waits for a notification. This is Java's `Object.wait()` / `notify()` equivalent.

```narration
Paanch primitives yaad rakho. Lock — basic mutual exclusion, ek thread andar, baaki wait. RLock — same thread dobara le sakta hai, recursion ke liye. Semaphore — counter-based, bounded parallelism ke liye. Event — ek flag, shutdown signals ke liye perfect. Condition — complex wait conditions ke liye, producer-consumer pattern. Java mein bhi same concepts hain — synchronized, ReentrantLock, Semaphore, Object.wait/notify. Syntax alag, idea same.
```

---

### The producer-consumer pattern with queue.Queue

`queue.Queue` is thread-safe by design — no explicit locking needed:

```python
import threading
import queue
import time
import random

task_queue = queue.Queue(maxsize=10)  # bounded queue
results = []
results_lock = threading.Lock()

def producer(name, count):
    for i in range(count):
        task = f"{name}-task-{i}"
        task_queue.put(task)  # blocks if queue is full
        print(f"Produced: {task}")
        time.sleep(random.uniform(0.1, 0.3))
    
def consumer(name):
    while True:
        try:
            task = task_queue.get(timeout=2.0)  # blocks until item available
            print(f"{name} processing: {task}")
            time.sleep(random.uniform(0.2, 0.5))  # simulate work
            
            with results_lock:
                results.append(f"{task}-done")
            
            task_queue.task_done()  # signal that task is complete
        except queue.Empty:
            print(f"{name} timeout, exiting")
            break

# Start producers and consumers
producers = [
    threading.Thread(target=producer, args=(f"P{i}", 5)) 
    for i in range(2)
]
consumers = [
    threading.Thread(target=consumer, args=(f"C{i}",)) 
    for i in range(3)
]

for t in producers + consumers:
    t.start()

for t in producers:
    t.join()

task_queue.join()  # block until all tasks are task_done()

print(f"Processed {len(results)} tasks")
```

**Key methods:**
- `put(item)` — blocks if queue is full (bounded queue)
- `get(timeout=N)` — blocks until item available or timeout
- `task_done()` — signal that a dequeued item is processed
- `join()` — block until all items are `task_done()`

This is safer and cleaner than managing Conditions manually.

```narration
queue.Queue production mein sabse zyada use hota hai multithreading ke liye. Internally yeh Condition use karta hai, tum manually lock manage nahi karte. put() aur get() block karte hain appropriately. task_done() aur join() se tum ensure kar sakte ho ki sab tasks complete ho gaye. Yeh Java ka BlockingQueue ka exact equivalent hai.
```

---

## The Rule

> **Rule:** Use `threading.Lock` whenever multiple threads access shared mutable state. The GIL does NOT make your code thread-safe — it only protects CPython's internal reference counts.

> **Corollary 1:** Prefer `queue.Queue` over manual Condition management for producer-consumer. It handles all the edge cases correctly.

> **Corollary 2:** Prefer `ThreadPoolExecutor` over raw Thread creation. It provides bounded concurrency, proper exception handling, and clean shutdown.

> **Corollary 3:** Always call `join()` on threads you start, or use `with ThreadPoolExecutor()`. Orphaned threads can cause data corruption or prevent program exit.

```narration
Rules yaad rakho — Lock use karo shared data ke liye, GIL tumhare data protect nahi karta. queue.Queue use karo producer-consumer ke liye. ThreadPoolExecutor use karo production mein, raw threads avoid karo jab possible ho. Aur hamesha join() karo — orphaned threads bahut mushkil bugs create karte hain.
```

---

## Production Story

A team builds an image processing service. Users upload images, the service resizes them to multiple dimensions. The first version creates a thread per image:

```python
# BUGGY — unbounded thread creation
import threading
from PIL import Image
import io

processed_images = []  # shared state without lock!

def process_image(image_data, sizes):
    img = Image.open(io.BytesIO(image_data))
    results = {}
    for size in sizes:
        resized = img.resize(size)
        results[size] = resized
    processed_images.append(results)  # RACE CONDITION
    return results

def handle_upload(image_data):
    # Create new thread for each upload
    t = threading.Thread(target=process_image, args=(image_data, [(100,100), (200,200)]))
    t.start()
    # BUG: no join() — response returns before processing complete
    return {"status": "processing"}
```

**Problems:**
1. Unbounded threads — 1000 concurrent uploads = 1000 threads = memory exhaustion
2. `processed_images.append()` has a race condition (list operations are NOT atomic in Python)
3. No `join()` — threads orphaned, results potentially lost

```python
# FIXED — bounded ThreadPool with proper synchronization
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import threading
import io

# Bounded pool — max 8 concurrent image processing tasks
executor = ThreadPoolExecutor(max_workers=8)
processed_images = []
images_lock = threading.Lock()

def process_image(image_data, sizes):
    img = Image.open(io.BytesIO(image_data))
    results = {}
    for size in sizes:
        resized = img.resize(size)
        results[size] = resized
    
    with images_lock:  # protect shared state
        processed_images.append(results)
    
    return results

def handle_upload(image_data):
    future = executor.submit(process_image, image_data, [(100,100), (200,200)])
    # Can return future.result() if sync response needed
    # Or track future for later retrieval
    return {"status": "processing", "task_id": id(future)}

# On shutdown:
# executor.shutdown(wait=True)
```

> **Warning:** Image processing with Pillow is CPU-bound, and Pillow does NOT release the GIL during resize operations. Threading here provides bounded concurrency (prevents memory exhaustion) but NOT speedup. For true parallelism, use `multiprocessing` or move to a library that releases the GIL (like Pillow-SIMD or OpenCV). We'll cover multiprocessing in the next lesson.

```narration
Yeh real bug hai — production mein unbounded threads memory exhaustion ka cause bante hain. 1000 uploads, 1000 threads, server crash. Fix simple hai — ThreadPoolExecutor se max_workers bound karo. Aur shared list ke liye lock lagao — list.append() atomic nahi hai Python mein. Ek aur important point — Pillow CPU-bound hai aur GIL release nahi karti, toh threading se speedup nahi milega, sirf bounded concurrency milegi. True speedup ke liye multiprocessing chahiye.
```

---

## Going Deeper

### Daemon threads — the dangerous shortcut

```python
import threading
import time

def background_task():
    while True:
        print("Background working...")
        time.sleep(1)

# Daemon thread — killed when main thread exits
t = threading.Thread(target=background_task, daemon=True)
t.start()

time.sleep(3)
print("Main thread exiting")
# Program exits here — daemon thread killed abruptly, no cleanup
```

Daemon threads are killed immediately when the main thread exits. They don't get a chance to clean up — files may not be flushed, connections not closed, transactions not committed.

**When to use daemon threads:** Background tasks that are truly disposable — periodic logging, heartbeats where losing one is fine.

**When NOT to use daemon threads:** Anything with cleanup requirements — database writes, file operations, sending completion notifications.

**Better alternative:** Use `Event` for graceful shutdown:

```python
import threading
import time

shutdown = threading.Event()

def background_task():
    while not shutdown.is_set():
        print("Background working...")
        shutdown.wait(timeout=1.0)  # interruptible sleep
    print("Background task cleaning up")  # cleanup happens

t = threading.Thread(target=background_task)
t.start()

time.sleep(3)
print("Requesting shutdown")
shutdown.set()
t.join()  # wait for graceful shutdown
print("Clean exit")
```

### Thread-local storage

Sometimes each thread needs its own copy of data — database connections, random number generators:

```python
import threading
import random

# Thread-local storage
local = threading.local()

def get_connection():
    # Each thread gets its own connection attribute
    if not hasattr(local, 'connection'):
        local.connection = create_db_connection()
    return local.connection

def worker():
    conn = get_connection()  # first call creates, subsequent calls reuse
    # use conn...

# Example with random
def initialize_rng():
    local.rng = random.Random()  # each thread gets its own RNG

def get_random():
    return local.rng.random()  # no lock needed — each thread has its own
```

Java equivalent is `ThreadLocal<T>`. Use it when sharing would require locking but each thread can work with its own copy.

### Debugging thread issues

```python
import threading
import sys

# List all active threads
for t in threading.enumerate():
    print(f"Thread: {t.name}, Daemon: {t.daemon}, Alive: {t.is_alive()}")

# Get current thread info
current = threading.current_thread()
print(f"Running in: {current.name}, ID: {current.ident}")

# Stack traces for all threads (debugging deadlocks)
import traceback
for thread_id, frame in sys._current_frames().items():
    print(f"\nThread {thread_id}:")
    traceback.print_stack(frame)
```

For deadlock detection, `sys._current_frames()` shows where each thread is stuck.

### Lock ordering to prevent deadlocks

```python
# DEADLOCK-PRONE
lock_a = threading.Lock()
lock_b = threading.Lock()

def thread_1():
    with lock_a:
        time.sleep(0.1)
        with lock_b:  # waits for thread_2 to release lock_b
            pass

def thread_2():
    with lock_b:
        time.sleep(0.1)
        with lock_a:  # waits for thread_1 to release lock_a
            pass
# DEADLOCK — each thread holds one lock, waits for the other

# FIX: Always acquire locks in consistent order
def thread_1_fixed():
    with lock_a:
        with lock_b:
            pass

def thread_2_fixed():
    with lock_a:  # same order as thread_1
        with lock_b:
            pass
```

**Deadlock prevention rule:** If you need multiple locks, always acquire them in the same order across all threads.

```narration
Daemon threads dangerous hain — main exit pe turant kill ho jaate hain, cleanup nahi hota. Graceful shutdown ke liye Event use karo. Thread-local storage jab har thread ko apna data chahiye — database connections, RNG. Debugging ke liye threading.enumerate() aur sys._current_frames() bahut helpful hain deadlocks find karne mein. Aur deadlock prevention — hamesha same order mein locks acquire karo.
```

---

## Connecting the Dots

**Lesson 3.1 (GIL):** Now you understand why we use all these locks even though Python has a GIL. The GIL prevents parallel bytecode execution but doesn't prevent interleaving. Between any two bytecode instructions, another thread can run and see/modify your data.

**Lesson 3.3 (Multiprocessing):** For CPU-bound work, threads don't help. Next lesson covers `multiprocessing` — separate processes, each with its own GIL. The tradeoff: processes can't share memory directly, so data must be serialized (pickle). `ThreadPoolExecutor` patterns transfer directly to `ProcessPoolExecutor`.

**Lesson 3.4 (asyncio):** Single-threaded concurrency. No locks needed because there's only one thread — but you explicitly yield control with `await`. For I/O-bound workloads with thousands of concurrent operations, asyncio often outperforms threading due to lower memory overhead per task.

**Module 10 (Context Managers):** `with lock:` is a context manager. In Module 10, you'll write your own `__enter__` / `__exit__` implementations. Understanding that `with lock:` is exactly `lock.acquire()` + `try/finally lock.release()` helps you appreciate the pattern.

**Java comparison:** `threading.Lock` ≈ `ReentrantLock`, `threading.Semaphore` ≈ `java.util.concurrent.Semaphore`, `queue.Queue` ≈ `BlockingQueue`, `ThreadPoolExecutor` ≈ `ExecutorService`. The concepts are identical; Python's syntax is often more concise due to context managers.

```narration
Sab connect ho raha hai — GIL se samjha ki threads interleave hote hain, isliye locks chahiye. Agle lesson mein multiprocessing — CPU-bound ke liye processes use karte hain, har process ka apna GIL. Asyncio mein single thread, locks ki zaroorat nahi kyunki explicitly yield karte ho. Java comparison — ExecutorService, BlockingQueue, Semaphore — sab same concepts hain, Python mein syntax cleaner hai context managers ke wajah se.
```

---

## Practice

### Exercise 1 — Identify the Bug

```python
import threading
import time

balance = 1000

def withdraw(amount):
    global balance
    if balance >= amount:
        time.sleep(0.001)  # simulate processing
        balance -= amount
        return True
    return False

def make_withdrawals():
    for _ in range(100):
        withdraw(10)

threads = [threading.Thread(target=make_withdrawals) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()

print(f"Final balance: {balance}")
# Expected: 0 (1000 withdrawals of 10 each)
# Actual: often negative or inconsistent
```

What's the bug? How do you fix it?

<details>
<summary>Answer</summary>

**Bug:** Race condition between the `if balance >= amount` check and `balance -= amount` update. Multiple threads can pass the check before any of them updates the balance.

**Timeline:**
1. Thread A checks `balance >= 10` (True, balance is 10)
2. Thread A sleeps
3. Thread B checks `balance >= 10` (True, still 10 — A hasn't updated yet)
4. Thread B sleeps
5. Both threads subtract 10 → balance becomes -10

**Fix:**

```python
import threading
import time

balance = 1000
balance_lock = threading.Lock()

def withdraw(amount):
    global balance
    with balance_lock:  # atomic read-check-modify
        if balance >= amount:
            time.sleep(0.001)
            balance -= amount
            return True
        return False
```

The lock ensures the entire check-and-modify sequence is atomic — no other thread can interleave.

</details>

### Exercise 2 — Implement Rate-Limited Fetcher

Write a function that fetches multiple URLs but limits to at most 5 concurrent requests:

```python
import time
# Your solution should use Semaphore and ThreadPoolExecutor

def fetch_url(url):
    """Simulates fetching a URL — takes 1 second"""
    time.sleep(1)
    return f"Content of {url}"

urls = [f"url_{i}" for i in range(20)]

# Implement rate_limited_fetch_all that:
# 1. Uses ThreadPoolExecutor
# 2. Limits to 5 concurrent fetches using Semaphore
# 3. Returns list of results in same order as input urls

def rate_limited_fetch_all(urls, max_concurrent=5):
    # Your code here
    pass

start = time.time()
results = rate_limited_fetch_all(urls)
elapsed = time.time() - start

print(f"Fetched {len(results)} URLs in {elapsed:.2f}s")
# Should take ~4 seconds (20 URLs, 5 at a time, 1s each)
```

<details>
<summary>Solution</summary>

```python
import threading
import time
from concurrent.futures import ThreadPoolExecutor

def fetch_url(url):
    time.sleep(1)
    return f"Content of {url}"

def rate_limited_fetch_all(urls, max_concurrent=5):
    semaphore = threading.Semaphore(max_concurrent)
    
    def limited_fetch(url):
        with semaphore:  # blocks if 5 threads already fetching
            return fetch_url(url)
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        # map preserves order
        results = list(executor.map(limited_fetch, urls))
    
    return results

urls = [f"url_{i}" for i in range(20)]

start = time.time()
results = rate_limited_fetch_all(urls)
elapsed = time.time() - start

print(f"Fetched {len(results)} URLs in {elapsed:.2f}s")
# Output: Fetched 20 URLs in 4.01s
```

**Key points:**
- `Semaphore(5)` limits concurrent fetches to 5
- `ThreadPoolExecutor(max_workers=20)` could have 20 threads, but only 5 can hold the semaphore at once
- `executor.map()` preserves input order in results
- Alternative: use `max_workers=5` directly without semaphore — but semaphore pattern is more flexible when you need different limits for different resource types

</details>

---

## Study Notes

**Q: In Java, threads truly run in parallel. You said Python threads don't. But both are OS threads — what's the actual difference?**
Both Python and Java threads are real OS threads (pthreads on Linux, Win32 threads on Windows). The OS can schedule them on different cores. The difference is what happens when they run. Java bytecode execution has no global lock — multiple threads genuinely execute JVM instructions simultaneously on different cores. Python bytecode execution requires holding the GIL — only one thread at a time executes Python bytecode. However,