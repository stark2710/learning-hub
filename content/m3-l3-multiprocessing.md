---
title: "Multiprocessing — True Parallelism"
module: "Concurrency"
domain: "Python Mastery"
lesson_id: "m3-l3-multiprocessing"
prev: "m3-l2-threading"
next: "m3-l4-asyncio"
duration: "~45 min"
---

```system_prompt
You are a Python expert teaching an experienced Java/backend developer (3 years Java, 1+ year Python).
Always respond in plain English.
This lesson covers Python's multiprocessing module — Process creation, inter-process communication (Queue, Pipe, shared memory), and ProcessPoolExecutor.
The user has completed the GIL and threading lessons. They understand that Python threads cannot parallelize CPU-bound Python code due to the GIL. They asked specifically about Java's true parallelism — emphasize that multiprocessing gives Python the same capability by running separate interpreter processes, each with its own GIL.
Focus on practical patterns: when to use multiprocessing vs threading, data serialization costs (pickle), shared state strategies, and graceful shutdown. Show the memory and startup overhead tradeoffs.
```

## What You'll Learn

- How `multiprocessing` bypasses the GIL by running separate Python interpreter processes
- The three ways to share data between processes: Queue, Pipe, and shared memory
- When multiprocessing helps (CPU-bound) and when it hurts (high serialization overhead)
- How to use `ProcessPoolExecutor` for clean, production-ready parallel computation

```narration
Yaar, ab tak GIL aur threading seekh li — samajh gaye ki Python threads CPU-bound code ke liye kaam nahi karti. Ab solution seekhte hain — multiprocessing. Yeh cheating jaisi lagti hai lekin actually brilliant hai. Har process ka apna Python interpreter, apna GIL, apna memory space. True parallelism exactly jaise Java threads karte hain. Aaj dekhenge kab use karna hai, kab nahi, aur production mein kaise properly implement karte hain.
```

---

## The Mental Model

Each Python process has its own GIL. Separate processes = separate GILs = true parallelism.

```
THREADING (Single Process)              MULTIPROCESSING (Multiple Processes)
──────────────────────────────          ──────────────────────────────────────
┌─────────────────────────────┐         ┌─────────────┐  ┌─────────────┐
│      PROCESS 1              │         │  PROCESS 1  │  │  PROCESS 2  │
│  ┌─────┐ ┌─────┐ ┌─────┐   │         │  ┌───────┐  │  │  ┌───────┐  │
│  │ T1  │ │ T2  │ │ T3  │   │         │  │Thread │  │  │  │Thread │  │
│  │WAIT │ │ RUN │ │WAIT │   │         │  │ RUN   │  │  │  │ RUN   │  │
│  └──┬──┘ └──┬──┘ └──┬──┘   │         │  └───────┘  │  │  └───────┘  │
│     │       │       │      │         │     GIL 1   │  │     GIL 2   │
│     └───────┼───────┘      │         │   MEMORY 1  │  │   MEMORY 2  │
│          GIL (one!)        │         └──────┬──────┘  └──────┬──────┘
│         SHARED MEMORY      │                │                │
└─────────────────────────────┘                ▼                ▼
         │                              ┌─────────────────────────┐
         ▼                              │    CPU CORE 1  CORE 2   │
┌─────────────────────────────┐         │    (true parallelism)   │
│    CPU CORE 1 (only one     │         └─────────────────────────┘
│    used for Python code)    │
└─────────────────────────────┘
```

**The tradeoff:** Processes don't share memory automatically. Data must be explicitly passed between them — which means serialization (pickle) and copying.

```
Process 1                    Process 2
─────────────────────────    ─────────────────────────
data = {"key": [1,2,3]}      
         │                   
         ▼ pickle.dumps()    
    b'\x80\x04...'  ────────→  pickle.loads()
                                      │
                                      ▼
                              data = {"key": [1,2,3]}
                              (separate copy in separate memory)
```

**Rule of thumb:** If your work is CPU-bound and each task is self-contained (doesn't need frequent communication with other tasks), multiprocessing gives linear speedup with cores. If tasks need to share state constantly, the serialization overhead may kill your gains.

```narration
Dekho difference — threading mein ek process, ek GIL, sab threads turns lete hain. Multiprocessing mein alag alag processes, har ek ka apna GIL, apna memory. Dono cores pe genuinely parallel execution. Lekin — aur yeh important hai — processes ke beech data share karna free nahi hai. Pickle se serialize karo, copy karo, doosre process mein deserialize karo. Agar bahut zyada data move karna hai, toh yeh overhead speedup kha jaata hai.
```

---

## How It Actually Works

### Creating processes — three ways

**Way 1: Direct Process creation**

```python
import multiprocessing
import os

def cpu_intensive(n):
    """Compute sum of squares — pure CPU work"""
    print(f"Process {os.getpid()} computing...")
    total = sum(i * i for i in range(n))
    print(f"Process {os.getpid()} done: {total}")
    return total

if __name__ == '__main__':  # REQUIRED on Windows and recommended everywhere
    p1 = multiprocessing.Process(target=cpu_intensive, args=(10_000_000,))
    p2 = multiprocessing.Process(target=cpu_intensive, args=(10_000_000,))
    
    p1.start()  # spawn new Python interpreter process
    p2.start()
    
    p1.join()   # wait for completion
    p2.join()
    
    print("Both processes complete")
```

**Critical:** The `if __name__ == '__main__':` guard is required. Without it, on Windows (which uses `spawn`), the child process would re-import the module and start infinite process creation.

**Way 2: ProcessPoolExecutor (recommended)**

```python
from concurrent.futures import ProcessPoolExecutor
import time

def compute_factorial(n):
    """CPU-bound task"""
    result = 1
    for i in range(1, n + 1):
        result *= i
    return n, result

if __name__ == '__main__':
    numbers = [50000, 60000, 70000, 80000]
    
    # Sequential baseline
    start = time.time()
    sequential_results = [compute_factorial(n) for n in numbers]
    print(f"Sequential: {time.time() - start:.2f}s")
    
    # Parallel with ProcessPoolExecutor
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        parallel_results = list(executor.map(compute_factorial, numbers))
    print(f"Parallel: {time.time() - start:.2f}s")
    
    # On 4-core machine: Sequential ~8s, Parallel ~2s
```

`ProcessPoolExecutor` has the same API as `ThreadPoolExecutor`. The only change is the import — your code structure stays identical.

**Way 3: Pool (older but still common)**

```python
from multiprocessing import Pool

def square(x):
    return x * x

if __name__ == '__main__':
    with Pool(processes=4) as pool:
        # map — apply function to each item, return list
        results = pool.map(square, range(10))
        print(results)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
        
        # starmap — when function takes multiple arguments
        pairs = [(1, 2), (3, 4), (5, 6)]
        results = pool.starmap(pow, pairs)
        print(results)  # [1, 81, 15625]
```

`Pool` is the older API. `ProcessPoolExecutor` is preferred for new code — better error handling and consistent with threading API.

```narration
Teen tarike hain processes banane ke, exactly jaise threading mein the. Direct Process creation simple cases ke liye. ProcessPoolExecutor production mein — same API as ThreadPoolExecutor, sirf import change karo. Pool purana API hai lekin abhi bhi common hai. Ek important baat — if __name__ == '__main__' guard zaroor lagao, especially Windows pe, nahi toh infinite process spawn ho jaayenge.
```

---

### Inter-process communication

Processes don't share memory. Here's how to pass data between them.

**Queue — producer-consumer pattern**

```python
from multiprocessing import Process, Queue
import time

def producer(queue, items):
    for item in items:
        print(f"Producing: {item}")
        queue.put(item)  # serializes and sends to queue
        time.sleep(0.1)
    queue.put(None)  # sentinel to signal completion

def consumer(queue, results):
    while True:
        item = queue.get()  # blocks until item available
        if item is None:
            break
        processed = item * 2
        results.put(processed)
        print(f"Consumed: {item} -> {processed}")

if __name__ == '__main__':
    work_queue = Queue()
    result_queue = Queue()
    
    p = Process(target=producer, args=(work_queue, [1, 2, 3, 4, 5]))
    c = Process(target=consumer, args=(work_queue, result_queue))
    
    p.start()
    c.start()
    
    p.join()
    c.join()
    
    # Collect results
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
    print(f"Results: {results}")  # [2, 4, 6, 8, 10]
```

`multiprocessing.Queue` uses pickle to serialize objects. Large objects = high serialization cost.

**Pipe — fast two-way communication**

```python
from multiprocessing import Process, Pipe

def sender(conn):
    conn.send("Hello from sender")
    conn.send([1, 2, 3])
    response = conn.recv()  # blocks until data received
    print(f"Sender got: {response}")
    conn.close()

def receiver(conn):
    msg = conn.recv()
    print(f"Receiver got: {msg}")
    data = conn.recv()
    print(f"Receiver got: {data}")
    conn.send("Acknowledged")
    conn.close()

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()  # returns two connection objects
    
    p1 = Process(target=sender, args=(parent_conn,))
    p2 = Process(target=receiver, args=(child_conn,))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
```

Pipes are faster than Queues for two-process communication but only connect exactly two endpoints.

**Shared memory — zero-copy for large data**

```python
from multiprocessing import Process, Value, Array
import ctypes

def increment_counter(counter, lock):
    for _ in range(100000):
        with lock:  # still need synchronization!
            counter.value += 1

def modify_array(arr):
    for i in range(len(arr)):
        arr[i] = arr[i] * 2

if __name__ == '__main__':
    from multiprocessing import Lock
    
    # Shared integer
    counter = Value(ctypes.c_int, 0)  # 'i' for int
    lock = Lock()
    
    processes = [Process(target=increment_counter, args=(counter, lock)) 
                 for _ in range(4)]
    for p in processes: p.start()
    for p in processes: p.join()
    
    print(f"Counter: {counter.value}")  # 400000
    
    # Shared array
    arr = Array(ctypes.c_double, [1.0, 2.0, 3.0, 4.0])
    p = Process(target=modify_array, args=(arr,))
    p.start()
    p.join()
    
    print(f"Array: {list(arr)}")  # [2.0, 4.0, 6.0, 8.0]
```

`Value` and `Array` create shared memory backed by `ctypes` types. No pickling, no copying — but you're limited to simple types (numbers, fixed-size arrays).

For large NumPy arrays, use `multiprocessing.shared_memory` (Python 3.8+):

```python
from multiprocessing import shared_memory, Process
import numpy as np

def modify_shared_array(shm_name, shape, dtype):
    # Attach to existing shared memory
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    arr = np.ndarray(shape, dtype=dtype, buffer=existing_shm.buf)
    arr[:] = arr * 2  # modify in place
    existing_shm.close()

if __name__ == '__main__':
    # Create large array in shared memory
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    shm = shared_memory.SharedMemory(create=True, size=arr.nbytes)
    shared_arr = np.ndarray(arr.shape, dtype=arr.dtype, buffer=shm.buf)
    shared_arr[:] = arr[:]  # copy data to shared memory
    
    p = Process(target=modify_shared_array, args=(shm.name, arr.shape, arr.dtype))
    p.start()
    p.join()
    
    print(f"Modified array: {shared_arr}")  # [2.0, 4.0, 6.0, 8.0, 10.0]
    
    shm.close()
    shm.unlink()  # cleanup
```

```narration
IPC — inter-process communication — teen main tarike hain. Queue sabse common hai, producer-consumer ke liye perfect. Pipe fast hai lekin sirf do processes ke beech kaam karti hai. Shared memory zero-copy hai — large arrays ke liye best. Value aur Array simple types ke liye, shared_memory NumPy arrays ke liye. Yaad rakho — shared memory mein bhi locks chahiye, processes ke beech race conditions hoti hain exactly jaise threads mein.
```

---

## The Rule

> **Rule:** Use multiprocessing for CPU-bound tasks where each task is independent. The speedup is roughly linear with the number of CPU cores, minus serialization overhead.

> **Corollary 1:** If tasks require frequent data exchange, serialization overhead may exceed computation time. Profile before committing to multiprocessing.

> **Corollary 2:** Process creation is expensive (~100-200ms). Use pools to amortize this cost across many tasks. Don't spawn a process per small task.

> **Corollary 3:** Objects passed to processes must be picklable. Lambdas, local functions, and many objects with open file handles cannot be pickled.

```narration
Rules yaad rakho — multiprocessing CPU-bound independent tasks ke liye hai. Speedup linear hota hai cores ke saath, but serialization cost minus karo. Frequent data exchange chahiye toh carefully profile karo. Process spawn karna expensive hai, pools use karo. Aur jo bhi pass karo woh picklable hona chahiye — lambdas nahi chalti, open file handles nahi chalte.
```

---

## Production Story

A data science team processes satellite images. Each image is 50MB, and the processing (edge detection, classification) takes 2 seconds per image. The initial implementation:

```python
# BUGGY — serialization overhead kills performance
from concurrent.futures import ProcessPoolExecutor
import numpy as np

def process_image(image_array):
    """CPU-intensive image processing"""
    # Edge detection, classification, etc.
    result = expensive_computation(image_array)
    return result

if __name__ == '__main__':
    images = [load_image(f"satellite_{i}.tif") for i in range(100)]
    # Each image is 50MB numpy array
    
    with ProcessPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(process_image, images))
    # Expected: ~25 seconds (100 images / 8 workers * 2s each)
    # Actual: ~180 seconds — slower than sequential!
```

**What went wrong:** Each 50MB array is pickled, copied to the worker process, unpickled. 100 images × 50MB × 2 (send + receive result) = 10GB of serialization. Pickle is CPU-bound and single-threaded — it became the bottleneck.

```python
# FIXED — pass file paths, load in worker, use shared memory for results
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import shared_memory
import numpy as np

def process_image_file(image_path):
    """Load and process in worker — no serialization of large arrays"""
    image_array = load_image(image_path)  # load inside worker
    result = expensive_computation(image_array)
    # Return only small metadata, not the full result array
    return {"path": image_path, "classification": result.label, "score": result.score}

if __name__ == '__main__':
    image_paths = [f"satellite_{i}.tif" for i in range(100)]  # just strings
    
    with ProcessPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(process_image_file, image_paths))
    # Now: ~25 seconds as expected
```

**Key fix:** Pass lightweight references (file paths, database IDs) instead of heavy data. Let workers load data themselves. Return only summarized results.

For cases where you must share large arrays between processes:

```python
# ALTERNATIVE — shared memory for truly shared data
from multiprocessing import shared_memory, Process
import numpy as np

def worker(shm_name, shape, dtype, start_idx, end_idx):
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    arr = np.ndarray(shape, dtype=dtype, buffer=existing_shm.buf)
    
    # Process only my slice — no copying
    for i in range(start_idx, end_idx):
        arr[i] = expensive_per_pixel_operation(arr[i])
    
    existing_shm.close()
```

> **Warning:** Shared memory requires careful lifecycle management. Always `close()` in workers and `unlink()` in the main process. Leaked shared memory persists until system reboot on some OSes.

```narration
Yeh classic production bug hai — team ne socha multiprocessing fast hogi, but 50MB images pickle karna zyada slow ho gaya computation se. Fix simple hai — heavy data pass mat karo, file paths ya database IDs pass karo. Workers khud load karein. Results mein bhi sirf summary return karo, full arrays nahi. Shared memory use karo jab genuinely zero-copy chahiye, lekin lifecycle carefully manage karo — leaked shared memory system reboot tak rehti hai.
```

---

## Going Deeper

### Process start methods

Python has three ways to create new processes:

```python
import multiprocessing

# Check current method
print(multiprocessing.get_start_method())

# Set method (must be done before any process creation)
multiprocessing.set_start_method('spawn')  # or 'fork' or 'forkserver'
```

| Method | Default On | How It Works | Pros | Cons |
|--------|-----------|--------------|------|------|
| `fork` | Linux/macOS | Copy parent's memory (copy-on-write) | Fast, inherits state | Not thread-safe, can cause deadlocks |
| `spawn` | Windows | Start fresh Python, pickle args | Clean, safe | Slow, must pickle everything |
| `forkserver` | None | Fork from clean server process | Safer fork, no import side effects | Moderate overhead |

**The fork trap:** If the parent process has threads when it forks, the child inherits only the calling thread — other threads' locks may be held forever, causing deadlocks.

```python
# DANGEROUS — threading + fork = potential deadlock
import threading
import multiprocessing

lock = threading.Lock()

def worker():
    with lock:  # may deadlock if parent held lock during fork
        print("Worker running")

def background():
    while True:
        with lock:
            pass  # constantly holding/releasing lock

if __name__ == '__main__':
    multiprocessing.set_start_method('fork')  # dangerous!
    
    bg = threading.Thread(target=background, daemon=True)
    bg.start()
    
    # If fork happens while bg thread holds lock, child deadlocks
    p = multiprocessing.Process(target=worker)
    p.start()
    p.join(timeout=5)
    print(f"Worker alive: {p.is_alive()}")  # may be True (deadlocked)
```

**Rule:** If you mix threading and multiprocessing, use `spawn` or `forkserver`, not `fork`.

### What can and cannot be pickled

```python
import pickle

# CAN pickle
pickle.dumps(42)                          # numbers
pickle.dumps("hello")                     # strings
pickle.dumps([1, 2, 3])                   # lists, dicts, tuples
pickle.dumps({"a": 1})
pickle.dumps(sum)                         # module-level functions

def top_level_function(x):
    return x * 2
pickle.dumps(top_level_function)          # module-level functions

class MyClass:
    def __init__(self, x):
        self.x = x
pickle.dumps(MyClass(10))                 # instances of picklable classes

# CANNOT pickle
pickle.dumps(lambda x: x * 2)             # PicklingError: lambdas
pickle.dumps(open("file.txt"))            # TypeError: file handles

def outer():
    def inner(x):                         # local functions
        return x * 2
    return inner
pickle.dumps(outer())                     # PicklingError

import threading
pickle.dumps(threading.Lock())            # TypeError: locks
```

**Workaround for lambdas:** Use `functools.partial` or define a module-level function:

```python
from functools import partial

def multiply(x, factor):
    return x * factor

# Instead of: lambda x: x * 2
double = partial(multiply, factor=2)

# Now picklable
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor() as executor:
    results = list(executor.map(double, [1, 2, 3, 4]))
```

### Debugging multiprocessing

```python
import multiprocessing
import logging

# Enable multiprocessing debug logging
multiprocessing.log_to_stderr(logging.DEBUG)

# Or set up custom logging in workers
def worker(x):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(f"worker-{multiprocessing.current_process().pid}")
    logger.debug(f"Processing {x}")
    return x * 2
```

For deadlock debugging, each process has a separate stack — use `faulthandler`:

```python
import faulthandler
faulthandler.enable()

# Now SIGSEGV or hang will print stack traces
# Send SIGABRT to dump all threads: kill -ABRT <pid>
```

### Memory overhead

Each process is a full Python interpreter:

```python
import os
import psutil

def worker():
    process = psutil.Process(os.getpid())
    print(f"Worker memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    import time
    time.sleep(10)

if __name__ == '__main__':
    # Single process memory
    main_process = psutil.Process(os.getpid())
    print(f"Main memory: {main_process.memory_info().rss / 1024 / 1024:.1f} MB")
    
    # With 8 workers
    from multiprocessing import Pool
    with Pool(8) as pool:
        pool.map(worker, range(8))
    
    # Typical: Main ~30MB, each worker ~30MB = 270MB total for 8+1 processes
```

Threads share memory (a few MB overhead per thread). Processes don't (30-50MB per process minimum). For thousands of concurrent tasks, prefer asyncio or threading.

```narration
Internals samjho — fork vs spawn vs forkserver. fork fast hai lekin threading ke saath deadlock kar sakta hai. spawn safe hai lekin slow aur sab kuch pickle karna padta hai. Lambdas pickle nahi hoti — functools.partial use karo. Har process 30-50MB minimum leta hai — 1000 processes matlab 30-50GB RAM. Thousands of concurrent tasks ke liye asyncio better hai, multiprocessing nahi. Debug karne ke liye log_to_stderr aur faulthandler useful hain.
```

---

## Connecting the Dots

**Lesson 3.1 (GIL):** The GIL is why multiprocessing exists. Each process has its own GIL, so CPU-bound Python code can finally use multiple cores. Remember — the GIL was a design choice to simplify CPython's memory management. Multiprocessing is Python's escape hatch.

**Lesson 3.2 (Threading):** `ProcessPoolExecutor` has the exact same API as `ThreadPoolExecutor`. Choose based on workload:
- I/O-bound → `ThreadPoolExecutor` (lower overhead, shared memory)
- CPU-bound → `ProcessPoolExecutor` (bypasses GIL, true parallelism)

**Lesson 3.4 (asyncio):** For massive concurrency (10K+ connections), asyncio beats both threading and multiprocessing. Single thread, no serialization, minimal memory per task. But asyncio doesn't help CPU-bound code — combine with multiprocessing via `loop.run_in_executor(ProcessPoolExecutor(), ...)`.

**Module 1 (Memory):** Remember copy-on-write from memory management? The `fork` start method uses CoW — child processes share parent's memory pages until they write. This is why forked workers can be memory-efficient if they mostly read shared data.

**Java comparison:** Java's `ForkJoinPool` and parallel streams use threads that truly parallelize. Python's `ProcessPoolExecutor` achieves similar parallelism but with process isolation instead of shared memory. Java's approach is more efficient for fine-grained parallelism; Python's is better for coarse-grained, independent tasks.

```narration
Sab connect ho raha hai. GIL ki wajah se threading CPU-bound mein kaam nahi karti — multiprocessing solution hai. ThreadPoolExecutor aur ProcessPoolExecutor same API — sirf use case ke hisaab se choose karo. Asyncio massive concurrency ke liye best hai lekin CPU work nahi karti — toh combine karo multiprocessing ke saath. Java mein threads directly parallelize karte hain, Python mein processes. Java fine-grained ke liye better, Python coarse-grained independent tasks ke liye.
```

---

## Practice

### Exercise 1 — Identify the Bottleneck

```python
from concurrent.futures import ProcessPoolExecutor
import numpy as np

def transform(arr):
    """Simple transformation — should be fast"""
    return arr * 2 + 1

if __name__ == '__main__':
    # Create 1000 small arrays
    arrays = [np.random.rand(100) for _ in range(1000)]
    
    # Process in parallel
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(transform, arrays))
    
    print(f"Processed {len(results)} arrays")
```

This code is slower than sequential. Why? What would you change?

<details>
<summary>Answer</summary>

**Problem:** The work per task is tiny (multiplying a 100-element array), but each task requires:
1. Pickling the input array
2. Copying to worker process
3. Unpickling
4. Actual computation (microseconds)
5. Pickling result
6. Copying back
7. Unpickling result

The serialization overhead vastly exceeds the computation time.

**Fixes:**

1. **Batch the work** — process multiple arrays per task:

```python
def transform_batch(arrays):
    return [arr * 2 + 1 for arr in arrays]

# Split into 4 batches (one per worker)
batch_size = len(arrays) // 4
batches = [arrays[i:i+batch_size] for i in range(0, len(arrays), batch_size)]

with ProcessPoolExecutor(max_workers=4) as executor:
    result_batches = list(executor.map(transform_batch, batches))
results = [r for batch in result_batches for r in batch]
```

2. **Use threading instead** — NumPy releases the GIL during computation:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(transform, arrays))
```

3. **Just use sequential** — for tiny tasks, overhead exceeds benefit:

```python
results = [transform(arr) for arr in arrays]
```

**Rule:** Multiprocessing overhead is ~1-10ms per task. If your task takes less than 10ms, batch it or use threading.

</details>

### Exercise 2 — Implement Parallel Map-Reduce

Write a parallel word counter that processes multiple text files:

```python
from concurrent.futures import ProcessPoolExecutor
from collections import Counter

# Each file is ~1MB of text
files = ["book1.txt", "book2.txt", "book3.txt", "book4.txt"]

def count_words_in_file(filepath):
    """Count words in a single file"""
    # Your implementation here
    pass

def parallel_word_count(files):
    """
    Return total word count across all files.
    Use ProcessPoolExecutor to parallelize.
    Combine results from all workers.
    """
    # Your implementation here
    pass

# Expected output: Counter with total word frequencies
# e.g., Counter({'the': 45000, 'a': 32000, 'is': 28000, ...})
```

<details>
<summary>Solution</summary>

```python
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
import re

def count_words_in_file(filepath):
    """Count words in a single file — runs in worker process"""
    counter = Counter()
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            # Simple word extraction
            words = re.findall(r'\b\w+\b', line.lower())
            counter.update(words)
    return counter  # Counter is picklable

def parallel_word_count(files):
    """Parallel map-reduce: map in workers, reduce in main process"""
    with ProcessPoolExecutor() as executor:
        # Map phase — parallel
        counters = list(executor.map(count_words_in_file, files))
    
    # Reduce phase — sequential (combine counters)
    total = Counter()
    for counter in counters:
        total.update(counter)
    
    return total

if __name__ == '__main__':
    files = ["book1.txt", "book2.txt", "book3.txt", "book4.txt"]
    
    result = parallel_word_count(files)
    print(f"Total unique words: {len(result)}")
    print(f"Top 10: {result.most_common(10)}")
```

**Why this works well:**
1. Each file is processed independently — no inter-process communication during computation
2. File paths (strings) are passed, not file contents