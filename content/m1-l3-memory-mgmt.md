---
title: "Python Memory Management & GC"
module: "Python Object Model"
domain: "Python Mastery"
lesson_id: "m1-l3-memory-mgmt"
prev: "m1-l2-mutability"
next: "m2-l1-first-class-functions"
duration: "~30 min"
---

# Module 1, Lesson 3 — Python Memory Management

## Where We Left Off

In Lessons 1 and 2 you learned that every Python name is a label bound to an object, and that mutation changes the object without moving the label. Now the question is: **how does Python know when an object is done and can be freed?** The answer is built on the same name-binding model you already know.

---

## What You'll Learn

- **Reference counting** — how Python tracks live objects (every name binding is +1, every unbind is -1, zero means free)
- **Why reference counting alone fails** — reference cycles keep refcounts above zero forever
- **The cyclic garbage collector** — the `gc` module, generational collection, and when to disable it
- **`weakref`** — referencing without owning, and `WeakValueDictionary` for in-memory caches

---

## The Mental Model — Every name is a +1. Every unbind is a -1. Zero means free.

CPython keeps a counter inside every object — the **reference count**. It tracks how many names, list slots, dict values, or function arguments currently point to that object.

```python
a = [1, 2, 3]   # list([1,2,3]) | refcount: 1
b = a            # list([1,2,3]) | refcount: 2
del a            # list([1,2,3]) | refcount: 1
del b            # list([1,2,3]) | refcount: 0 → freed immediately
```

This is **deterministic deallocation** — unlike Java's GC, CPython frees the object *the instant* the last reference drops. No GC pause, no wait.

What increments the refcount:
- Assigning a name: `x = obj`
- Passing as a function argument: the parameter name is +1 for the call duration
- Appending to a list: `lst.append(obj)`
- Storing as a dict value: `d['k'] = obj`
- Inside a `for` loop: the loop variable holds a reference each iteration

**The `sys.getrefcount()` gotcha:**

```python
import sys
x = []
print(sys.getrefcount(x))  # prints 2, not 1
```

Calling `getrefcount(x)` itself creates a temporary reference — the function's parameter. So it always prints one more than you expect.

---

## How Python Actually Works

### sys.getrefcount — see the count yourself

```python
import sys

a = []
print(sys.getrefcount(a))   # 2 — 'a' + getrefcount's own arg binding

b = a                        # b points to the same list → refcount 3
print(sys.getrefcount(a))   # 3

del b                        # removes b's binding → refcount 2
print(sys.getrefcount(a))   # 2
```

### Reference cycles — the case refcounting fails

```python
a = {}
b = {}
a['other'] = b   # a holds a reference to b
b['other'] = a   # b holds a reference back to a → CYCLE

del a
del b
# Both objects still alive! a still referenced by b['other'],
# b still referenced by a['other']. Refcounts are 1 each.
# Refcounting alone cannot free them.

import gc
gc.collect()   # cyclic GC detects the unreachable cycle and frees both
```

### weakref — reference without incrementing the refcount

```python
import weakref

class Expensive:
    def __del__(self):
        print("Expensive freed")

obj = Expensive()
weak = weakref.ref(obj)   # does NOT increment refcount of obj

print(weak())             # <Expensive object> — alive, deref with weak()

del obj                   # refcount drops to 0 → freed immediately
                          # prints: "Expensive freed"

print(weak())             # None — object is gone, weakref returns None
```

### tracemalloc — find memory leaks by snapshot diff

```python
import tracemalloc

tracemalloc.start()

data = [dict(i=i, val=i*2) for i in range(10_000)]

snapshot = tracemalloc.take_snapshot()
top = snapshot.statistics('lineno')[:5]
for stat in top:
    print(stat)
# Typical output:
# script.py:5: size=1.8 MiB, count=10000, average=189 B
```

---

## The Rule

> Refcounting handles 99% of memory. The cyclic GC handles the other 1%. `weakref` is how you reference without owning.

**Never use `__del__` for cleanup** — it won't fire if the object is in a cycle. Always use context managers for resource cleanup.

| Tool | When to use |
|------|-------------|
| Normal cleanup | Refcounting handles it — no action needed |
| Cyclic cleanup | `gc.collect()` or let the generational GC run automatically |
| Caches / observers | `weakref.ref()` or `WeakValueDictionary()` |

---

## Production Story — The in-memory cache that grew until the server OOMed

A high-traffic API service. Memory grew 50 MB per hour. Pod hit container memory limit, killed, restarted, grew again.

**The bug:**
```python
# ⚠ BUGGY CODE — grows without bound
class ProfileCache:
    def __init__(self):
        self._cache: dict[int, "UserProfile"] = {}   # strong reference

    def get(self, user_id: int):
        if user_id not in self._cache:
            self._cache[user_id] = fetch_profile(user_id)
        return self._cache[user_id]
```

Every profile stored holds a strong reference. The dict is the last owner. Profile's refcount never reaches 0. 50K daily active users × 80KB per profile = 4 GB. Pod OOMs.

**The fix:**
```python
import weakref

class ProfileCache:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()   # ← fix

    def get(self, user_id: int):
        profile = self._cache.get(user_id)
        if profile is None:
            profile = fetch_profile(user_id)
            self._cache[user_id] = profile   # weak reference only
        return profile
# Profile freed when the caller is done with it. Cache entry removed automatically.
```

**The lesson:** Use `WeakValueDictionary` when the cache should not be the thing keeping objects alive. The caller's active use should determine lifetime, not the cache's presence.

---

## Going Deeper

### GC generations — why Python uses three

```python
import gc

print(gc.get_threshold())    # (700, 10, 10) — default thresholds
# Gen 0 collected when 700 new objects allocated since last gen-0 collection
# Gen 1 collected every 10 gen-0 collections
# Gen 2 collected every 10 gen-1 collections

gc.collect(0)               # collect only generation 0
gc.collect()                # full collection — all generations
```

### The small integer cache

CPython pre-allocates integer objects for `-5` to `256` at startup. These are singletons:

```python
a = 100; b = 100
print(a is b)   # True — same object

a = 1000; b = 1000
print(a is b)   # False — separate objects
# Always use == for value comparison, never 'is'
```

### gc.disable() — when engineers do this

```python
# Pattern: disable GC around a cycle-free hot loop
gc.disable()
try:
    results = [process(item) for item in large_dataset]
finally:
    gc.enable()
    gc.collect()
# Instagram engineering blog (2017) reported ~10% throughput gain from this.
```

Only safe if you know the loop creates no reference cycles.

### `__del__` ordering with cycles

If two objects in a cycle both define `__del__`, Python cannot determine which to call first. Before Python 3.4, such objects leaked permanently into `gc.garbage`. Since 3.4, CPython handles it, but ordering is arbitrary. This is the primary reason `__del__` is unreliable — use context managers instead.

---

## Connecting the Dots

**← Built on Lesson 1 (Names & Objects):** Refcounting *is* the name-binding model made concrete. Every name binding is a +1. Every name going out of scope is a -1.

**← Built on Lesson 2 (Mutability):** Mutation doesn't change refcounts — the name still points to the same object. Rebinding does — it decrements the old object's refcount and increments the new one's.

**→ Module 2 (Closures & Generators):** Closures keep a reference to the outer scope's names — those names hold refcounts above zero even after the function returns. This is the closure memory model.

**→ Module 3 (The GIL):** CPython's Global Interpreter Lock exists *because* refcounting is not thread-safe. Incrementing and decrementing a counter from multiple threads simultaneously causes races. The GIL serializes these increments.

---

## Practice

### Exercise 1 — Predict the refcount

```python
import sys

data = [1, 2, 3]
# Q1: what does sys.getrefcount(data) return here?

container = [data, data]   # two list slots, both pointing to same object
# Q2: sys.getrefcount(data) now?

def inspect(obj):
    return sys.getrefcount(obj)
    # Q3: what does inspect(data) return?

result = inspect(data)
# Q4: sys.getrefcount(data) now?
```

<details>
<summary>Answers</summary>

```
Q1: 2  — 'data' name (1) + getrefcount's own arg binding (1)
Q2: 4  — 'data' name (1) + container[0] (1) + container[1] (1) + getrefcount arg (1)
Q3: 5  — same 3 external refs + 'obj' param binding (1) + getrefcount arg (1)
Q4: 4  — function returned, 'obj' frame is gone; 3 external refs + getrefcount arg
```
</details>

---

### Exercise 2 — Fix the leaking cache

```python
class Session:
    def __init__(self, sid):
        self.sid = sid
        self.data = {"key": "x" * 100_000}   # ~100 KB per session

    def __del__(self):
        print(f"Session {self.sid} freed")

class SessionRegistry:
    def __init__(self):
        self._sessions = {}            # sid -> Session (LEAKING)

    def register(self, sid):
        s = Session(sid)
        self._sessions[sid] = s
        return s

registry = SessionRegistry()

def handle_request(sid):
    session = registry.register(sid)
    return "done"

for i in range(1000):
    handle_request(i)

# Problem: all 1000 Sessions are still alive.
# Fix: sessions should be freed when handle_request returns.
```

<details>
<summary>Solution</summary>

```python
import weakref

class SessionRegistry:
    def __init__(self):
        self._sessions = weakref.WeakValueDictionary()   # ← fix

    def register(self, sid):
        s = Session(sid)
        self._sessions[sid] = s   # weak reference — registry doesn't own it
        return s

# Now: when handle_request() returns, 'session' goes out of scope.
# Refcount → 0. Session freed immediately.
# Registry entry auto-removed. Memory stays bounded.
```
</details>
