---
title: "Generators & Iterators"
module: "Python Functions Deep Dive"
domain: "Python Mastery"
lesson_id: "m2-l3-generators"
prev: "m2-l2-decorators"
next: "m3-l1-gil"
duration: "~40 min"
---

```system_prompt
You are a Python expert teaching an experienced Java/backend developer (3 years Java, 1+ year Python).
Always respond in plain English.
This lesson covers Python generators and iterators — the iterator protocol, yield mechanics, generator expressions, yield from, and memory efficiency.
When comparing to Java: Python's iterator protocol maps to Java's Iterable/Iterator interfaces. Python generators are equivalent to Java lazy sequences or Stream.generate/Stream.iterate. The yield keyword is Python's way of returning a value from a stream pipeline stage while keeping all local state frozen.
Be concrete and mechanical. When the user asks "what does this mean", break it down line by line. Build simple analogies before technical definitions — the user learns better from concrete examples before abstractions.
```

## What You'll Learn

- How Python's iterator protocol works under the hood (`__iter__` and `__next__`)
- What `yield` actually does to a function — and why it is completely different from `return`
- Why generator expressions use far less memory than list comprehensions for large data
- How `yield from` delegates to another iterable and when to reach for it

```narration
Yaar, aaj hum generators seekhenge — Python ke sabse powerful aur underused features mein se ek. Agar tumne kabhi socha hai ki Flask ya FastAPI mein streaming responses kaise kaam karti hain, ya asyncio kyun itna fast hai — generators ke bina yeh possible nahi tha. Lesson 2.1 mein closures dekhe the, 2.2 mein decorators — ab generators ke saath Module 2 complete ho jaayega.
```

---

## The Mental Model

Think of a generator as a **paused function**.

A normal function runs start to finish and returns one value. A generator function can **pause in the middle**, hand you a value, and when you ask for the next one, it **resumes from exactly where it left off** — local variables and all.

**The vending machine vs the chef:**

```
VENDING MACHINE (list)         CHEF (generator)
────────────────────────────   ────────────────────────────
Stocks ALL items upfront       Makes one dish on demand
Fast random access             No random access
Uses all the shelf space       Uses minimal space
[1, 2, 3 ... 1,000,000]        next() → 1, next() → 2 ...
```

A list builds everything immediately. A generator builds nothing until you ask.

**Memory comparison:**

```
squares = [x**2 for x in range(1_000_000)]   # list: ~8 MB RAM, all computed NOW
squares = (x**2 for x in range(1_000_000))   # generator: ~200 bytes, nothing computed yet
```

**The iterator protocol — how Python's for loop works internally:**

```
any iterable (list, file, generator...)
        │
        ▼  iter()
   iterator object
        │
        ├── next() ──→ value 1
        ├── next() ──→ value 2
        ├── next() ──→ value 3
        └── next() ──→ StopIteration  (signals: done)
```

Every `for x in something` loop is secretly calling `iter()` once and `next()` repeatedly until `StopIteration`.

```narration
Yaar dekho — generator ka mental model simple hai: ek paused movie. Jab function `yield` pe pahunchta hai, woh wahan freeze ho jaata hai — sari local variables waise ki waise — aur ek value de deta hai. Next baar jab tum `next()` call karo, woh freeze point se resume karta hai. Yeh Java ke Iterator interface ka hi Python version hai — bas bahut zyada elegant aur powerful. Memory benefit toh bonus hai.
```

---
## How It Actually Works

### The iterator protocol under the hood

Python's `for` loop is just syntax sugar over two dunder methods:

```python
my_list = [10, 20, 30]

# What the for loop actually does:
it = iter(my_list)          # calls my_list.__iter__() → returns a list_iterator
print(next(it))             # calls it.__next__() → 10
print(next(it))             # → 20
print(next(it))             # → 30
# next(it) now raises StopIteration → for loop catches this and exits cleanly
```

You can implement your own iterator with just those two methods:

```python
class CountUp:
    def __init__(self, n):
        self.n = n
        self.current = 0

    def __iter__(self):
        return self                     # iterator returns itself

    def __next__(self):
        if self.current >= self.n:
            raise StopIteration
        val = self.current
        self.current += 1
        return val

for x in CountUp(3):
    print(x)                            # 0, 1, 2
```

Generators give you this same behaviour — without writing a class.

---

### yield suspends the frame

When Python hits `yield`, it freezes the entire function frame — local variables, loop counters, everything — and hands back the yielded value. `next()` thaws it.

```python
def count_up(n):
    print("generator started")          # runs on FIRST next() call
    i = 0
    while i < n:
        yield i                         # ← pauses here, returns i to caller
        i += 1                          # ← resumes here on next next()
    print("generator exhausted")        # runs after last yield

gen = count_up(3)                       # creates generator object — runs NOTHING yet
print(next(gen))                        # "generator started" then → 0
print(next(gen))                        # → 1  (resumed: ran i+=1, looped, hit yield)
print(next(gen))                        # → 2
print(next(gen))                        # "generator exhausted" then StopIteration
```

`count_up(3)` does not run any code. It returns a generator object. Code runs only when you pull values.

---

### Generator expressions

Swap `[]` for `()` and you get a lazy generator instead of an eager list:

```python
# List comprehension — ALL values computed immediately, stored in RAM
big_list = [x ** 2 for x in range(1_000_000)]      # ~8 MB

# Generator expression — nothing computed yet, object is ~200 bytes
big_gen  = (x ** 2 for x in range(1_000_000))

# Same iteration interface:
total = sum(big_gen)         # pulls values one at a time, never builds the list
```

Rule of thumb: if you only iterate once and don't need indexing, use a generator expression.

---

### yield from — clean delegation

`yield from iterable` hands off iteration to another iterable, forwarding every value:

```python
def flatten(nested):
    for sublist in nested:
        yield from sublist              # delegates — no manual inner loop needed

list(flatten([[1, 2], [3, 4], [5]]))    # → [1, 2, 3, 4, 5]
```

Without `yield from` you'd write `for item in sublist: yield item` — equivalent for simple cases, but `yield from` also properly forwards `send()` and exceptions into sub-generators (important for coroutines).

```narration
Ab samjho — `yield` ek pause button hai. Function ka poora state freeze hota hai — variables, loop counter, sab kuch — aur value caller ko milti hai. `next()` se resume. Yeh Java ke Iterator ke `hasNext()` + `next()` pattern se kahin zyada clean hai. Generator expressions list comprehensions ki hi tarah dikhte hain, bas `[]` ki jagah `()`. Aur `yield from` se tum kisi bhi iterable ko apne generator ke andar delegate kar sakte ho — nested loops ki zaroorat nahi.
```

---
## The Rule

> **Rule:** Calling a generator function returns a generator object — it runs zero lines of code. Code runs only when you pull values with `next()` or a `for` loop. This is lazy evaluation.

> **Rule:** Every generator is an iterator (`__iter__` returns `self`, `__next__` yields values). But not every iterator is a generator — a list is iterable, not an iterator. `iter(my_list)` creates a `list_iterator`.

> **Rule:** Generators are single-use. Once exhausted, iterating again yields nothing. If you need multiple passes, convert to a list with `list(gen)` or call the generator function again.

```narration
Teeno rules yaad rakho yaar. Pehla — generator function call karna koi code nahi chalata, sirf object banata hai. Dusra — generator ek iterator hai, lekin list iterator nahi hai, woh iterable hai. Teesra aur sabse important — generator ek baar hi use hota hai. Exhaust ho gaya toh khatam, dobara iterate karo toh kuch nahi milega. Yeh Java stream ka behaviour bilkul waise hi hai.
```

---

## Production Story

**The bug:** A data pipeline processes 2M order rows from the database, loads all into a list, filters active ones, then passes to a reporting function. Works in dev with 1,000 rows. Crashes in production with an OOM kill.

```python
# BUGGY — OOM on large tables
def get_active_orders(db):
    rows = db.execute("SELECT * FROM orders").fetchall()     # loads ALL 2M rows into RAM
    return [transform(row) for row in rows if row['status'] == 'active']

# caller
for order in get_active_orders(db):     # already crashed above
    write_report(order)
```

`fetchall()` materialises every row into a Python list before any filtering happens. 2M rows × ~500 bytes = ~1 GB just to find the 50K active ones.

```python
# FIXED — constant memory, same result
def get_active_orders(db):
    cursor = db.execute("SELECT * FROM orders")  # cursor is already lazy
    for row in cursor:                           # fetches one row at a time from DB
        if row['status'] == 'active':
            yield transform(row)                 # caller receives one at a time

# caller is identical — no change needed
for order in get_active_orders(db):
    write_report(order)
```

The fix converts the function into a generator. The DB cursor is already lazy — it fetches rows in batches. `yield` makes the entire pipeline lazy: one row fetched, filtered, transformed, written, garbage collected. Peak memory stays near zero regardless of table size.

> **Warning:** If you call `list(get_active_orders(db))` anywhere downstream, you immediately re-materialise everything and lose all the benefit. Audit every caller when converting a function to a generator.

```narration
Yeh production bug bahut common hai yaar — especially jab dev mein chhota data hota hai aur prod mein bada. `fetchall()` ek classic trap hai. Database cursor already lazy hota hai, tum usse seedha iterate kar sakte ho. `yield` add karo aur pura pipeline lazy ho jaata hai — ek row aati hai, process hoti hai, delete hoti hai. Memory nearly zero. Aur caller ka code change nahi karna padta, woh same `for` loop se kaam karta hai.
```

---
## Going Deeper

### CPython generator frame objects

When Python creates a generator, it allocates a `PyFrameObject` — the same structure used for regular function calls — and keeps it alive between `next()` calls:

```python
def demo():
    x = 42
    yield x
    x = 99
    yield x

g = demo()
next(g)                         # runs to first yield, freezes frame

print(g.gi_frame.f_locals)      # {'x': 42} — local state is frozen here
print(g.gi_running)             # False — not currently executing
print(g.gi_frame.f_lasti)       # bytecode offset of last executed instruction

next(g)                         # resumes, x becomes 99
print(g.gi_frame.f_locals)      # {'x': 99}
```

`g.gi_frame` is `None` once the generator is exhausted — CPython drops the frame.

---

### send() — two-way generators

`yield` can also **receive** values, making generators a two-way channel. This is the foundation of `asyncio`:

```python
def running_average():
    total, count = 0, 0
    while True:
        value = yield (total / count if count else 0)   # receives via send(), yields result
        total += value
        count += 1

avg = running_average()
next(avg)           # REQUIRED first step — primes the generator, runs to first yield
avg.send(10)        # → 10.0
avg.send(20)        # → 15.0
avg.send(30)        # → 20.0
```

You must call `next(gen)` (or `gen.send(None)`) once to advance to the first `yield` before you can `send` real values. This is called "priming" the generator.

---

### Generator pipelines

Generators compose naturally into Unix-style pipelines — each stage pulls from the previous, nothing is buffered:

```python
def read_lines(path):
    with open(path) as f:
        yield from f                                    # one line at a time from disk

def only_errors(lines):
    return (line for line in lines if 'ERROR' in line)  # generator expression

def parse_json(lines):
    import json
    return (json.loads(line.strip()) for line in lines)

# Build pipeline — zero intermediate lists, constant memory
pipeline = parse_json(only_errors(read_lines('/var/log/app.log')))

for event in pipeline:
    alert(event)
```

Each stage is lazy — a value moves through the whole pipeline before the next one is pulled from disk. Compare to Java: `Files.lines(path).filter(...).map(...).forEach(...)` — same idea, same laziness.

```narration
CPython mein generator ka state ek `PyFrameObject` mein store hota hai — wahi jo normal function calls use karte hain. Isliye generators Python mein "free" hain performance wise. `send()` generators ko two-way channel banata hai — yeh `asyncio` ka foundation hai. Aur pipelines — yeh Unix pipes ki tarah kaam karte hain, ek stage se value niklo, process karo, agla stage ko do. Koi intermediate list nahi, constant memory.
```

---
## Connecting the Dots

- **Module 3 — GIL & asyncio:** `async def` + `await` is syntactic sugar over generators with `send()`. Under the hood, CPython's event loop calls `gen.send(None)` to resume coroutines. Understanding generators makes `asyncio` click immediately.
- **Module 10 — Context Managers:** `@contextmanager` is a decorator that turns a single-`yield` generator into a `with` block. You'll write `def managed_resource(): ... yield resource ...` and the decorator wraps it with `__enter__`/`__exit__`. Decorators + generators = context managers.
- **Java Streams comparison:** `Stream.filter().map().forEach()` is Python's `(transform(x) for x in source if predicate(x))`. Both are lazy. Key difference: Java streams push data through the pipeline; Python generators pull. Python's pull model makes composition and backpressure simpler.
- **Lesson 2.1 closures:** Generator expressions close over variables just like lambdas do — the same late-binding trap applies. `(x for x in range(3))` is fine, but be careful with generator expressions inside loops that capture a mutable variable.

```narration
Yaar generators sirf memory efficiency ke liye nahi hain — yeh Python ki concurrency model ka base hain. `async/await` generators ke upar bana hai. Jab tum Module 3 mein asyncio padhoge, sab kuch immediately sense karega kyunki tum already jaante ho `yield` aur `send()` kaise kaam karte hain. Aur `@contextmanager` — woh decorator plus generator ka ek elegant combination hai. Yeh sab cheezein connect ho rahi hain.
```

---

## Practice

### Exercise 1 — Trace the Output

```python
def mystery():
    print("A")
    yield 1
    print("B")
    yield 2
    print("C")

g = mystery()
x = next(g)
print(x)
y = next(g)
print(y)
```

What is the exact output, and why does "C" never print?

<details>
<summary>Answer</summary>

```
A
1
B
2
```

`mystery()` creates the generator — nothing runs. `next(g)` runs the body until the first `yield 1`: prints "A", pauses, hands back `1`. `print(x)` prints `1`. `next(g)` resumes after the first yield, runs until the second `yield 2`: prints "B", pauses, hands back `2`. `print(y)` prints `2`. "C" never prints because we never call `next(g)` a third time — the generator is suspended after the second yield, not exhausted. A fourth `next(g)` would print "C" then raise `StopIteration`.

</details>

---

### Exercise 2 — Fix the Memory Bug

```python
# This works on small files but OOMs on 500 MB log files. Fix it with a generator.
def get_slow_queries(log_path, threshold_ms=1000):
    with open(log_path) as f:
        lines = f.readlines()                              # BUG: loads entire file into RAM
    slow = [line for line in lines if 'query_time' in line]
    return [parse_query(line) for line in slow if extract_ms(line) > threshold_ms]

for query in get_slow_queries('/var/log/mysql/slow.log'):
    alert(query)
```

<details>
<summary>Answer</summary>

```python
def get_slow_queries(log_path, threshold_ms=1000):
    with open(log_path) as f:
        for line in f:                                     # file iterator: one line at a time
            if 'query_time' in line and extract_ms(line) > threshold_ms:
                yield parse_query(line)                    # yield one result, stay lazy

for query in get_slow_queries('/var/log/mysql/slow.log'):
    alert(query)
```

Three changes: `readlines()` → `for line in f` (file is already an iterator, no list needed), the two-pass list comprehension becomes a single-pass `if` inside the loop, and `return [...]` becomes `yield`. The caller loop is unchanged. Peak memory is now the size of one line — constant regardless of file size.

</details>

```narration
Practice mein pehla exercise output trace karna hai — generators ke execution order ko solidify karne ke liye. Dusra ek real production bug hai — log file ka OOM. Solve karo khud pehle, phir answer dekho. Yeh exact pattern tum production mein use karoge — database cursors, file readers, API pagination — sab jagah generators kaam aate hain.
```

---
## Study Notes

**Q: Is a generator the same as a list? Can I index into it like `gen[0]`?**
No — generators have no length and no indexing. `gen[0]` raises `TypeError: 'generator' object is not subscriptable`. A generator only supports `next()`. If you need random access, convert with `items = list(gen)`, but then you lose the memory benefit. Think of a generator as a stream, not a collection.

**Q: In Java I use `.collect(Collectors.toList())` to materialise a stream. What is the Python equivalent?**
`list(gen)` is Python's equivalent — it exhausts the generator and collects all values into a list. `sum(gen)`, `max(gen)`, `set(gen)`, and `dict(gen)` are like other collectors. Just like Java streams, once you collect you lose laziness. And once you exhaust a generator, iterating it again gives nothing — you must recreate it.

**Q: Can I iterate a generator more than once?**
No — generators are single-pass. Once `StopIteration` is raised, the generator is permanently exhausted. A second `for` loop over the same generator yields nothing. This is unlike a list, which resets on each `for` loop. If you need multiple passes, either store as `data = list(gen)` or wrap the generator call in a function and call it again each time.

**Q: What does `yield from` do that a nested for loop cannot?**
For simple iteration they are equivalent: `yield from iterable` and `for item in iterable: yield item` produce the same values. But `yield from` also transparently forwards `send()` values into the sub-generator and forwards `throw()` exceptions — two things a manual loop cannot do. In `asyncio`, `await expr` is essentially `yield from expr` for coroutines. For plain iteration you can use either; for coroutines, `yield from` (or `await`) is required.

**Q: Why must I call `next(gen)` before `gen.send(value)` for two-way generators?**
Because `send()` resumes the generator and delivers the value to the `yield` expression — but the generator must already be paused at a `yield` for that to make sense. On the very first call, the generator has not run at all, so there is no `yield` waiting to receive a value. `next(gen)` (which is `gen.send(None)`) advances to the first `yield`, pausing it there. After that, `send(value)` can deliver values. Skipping the prime step raises `TypeError: can't send non-None value to a just-started generator`.

---

## Lesson Complete

- A generator function returns a generator object when called — no code runs until the first `next()`
- `yield` freezes the entire function frame (locals + instruction pointer) and hands a value to the caller
- Generator expressions `(x for x in ...)` are lazy; list comprehensions `[x for x in ...]` are eager
- `yield from iterable` delegates iteration and properly forwards `send()`/`throw()` into sub-generators
- Generators are single-use — exhausted generators yield nothing on re-iteration
- `send()` makes generators two-way channels; this is the foundation of `asyncio` coroutines
