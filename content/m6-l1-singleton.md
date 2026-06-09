---
title: "Why Patterns Exist + Singleton"
module: "Creational Patterns"
domain: "Design Patterns"
lesson_id: "m6-l1-singleton"
prev: ""
next: "m6-l2-factory-method"
duration: "~50 min"
---

```system_prompt
You are a senior software engineer and Design Patterns expert with 15+ years of experience in Python, Java, and large-scale backend systems. The student has 4+ years of backend experience (3 years Java, 1+ year Python) and is starting the Design Patterns domain.

For this lesson on Why Patterns Exist + Singleton:
- Relate GoF patterns to Gang of Four book context — they likely know it exists but never read it deeply
- Connect to Java patterns they've seen (Spring beans are Singletons, for example)
- Be honest about Singleton's controversy — it's the most abused pattern
- Show Python-specific implementations — Python has no private constructors, so the approach differs
- When they ask about thread safety, give them the real story about the GIL and why it still matters
- Always respond in plain English.
```

## What You'll Learn

- Why design patterns exist — the problem they solve, not just the definition
- How to read a pattern: intent, structure, consequences (not just code)
- Singleton: the most recognized and most misused creational pattern
- Python-specific Singleton implementations and which one to actually use in production

```narration
Yaar, aaj hum Design Patterns ka duniya mein enter kar rahe hain. Yeh ek aisa topic hai jiske baare mein sabne suna hai, lekin bahut kam log actually samjhe hain kyon yeh exist karte hain. Aaj hum seedha wahan se shuru karte hain — patterns kyun bane, aur phir Singleton, jo sabse famous aur sabse zyada misuse hone wala pattern hai.
```

---

## The Mental Model

### Why Do Patterns Exist?

In 1994, four authors — Gamma, Helm, Johnson, Vlissides (the "Gang of Four") — noticed something interesting: experienced developers kept solving the same problems the same way. Not because they copied each other, but because those solutions were genuinely good answers to recurring problems.

They wrote it down. That book is the **Design Patterns** book.

> Patterns are not code. They are **documented solutions to recurring design problems** in a specific context.

Think of it this way: when a civil engineer designs a bridge, they don't reinvent load distribution from scratch. They use known structural patterns — arch, suspension, truss — because those patterns have known properties, known failure modes, and shared vocabulary. When one engineer says "truss bridge," every other engineer immediately understands the tradeoffs.

Software patterns do the same thing. When you say "I used Strategy here," a senior dev immediately knows: pluggable behavior, same interface, runtime-swappable. That shared vocabulary is half the value.

```
The Three Categories (GoF)
─────────────────────────────────────────────────────────
  CREATIONAL          STRUCTURAL          BEHAVIORAL
  (how objects        (how objects        (how objects
   are created)        are composed)       communicate)
─────────────────────────────────────────────────────────
  Singleton           Adapter             Strategy
  Factory Method      Bridge              Observer
  Abstract Factory    Composite           Command
  Builder             Decorator           Template Method
  Prototype           Facade              State
                      Flyweight           Chain of Resp.
                      Proxy               + more...
─────────────────────────────────────────────────────────
```

### How to Read a Pattern

Every pattern has four parts worth understanding:

1. **Intent** — The one-sentence "what does it do"
2. **Problem** — The specific context/constraint that makes this pattern useful
3. **Structure** — The classes/objects and their relationships
4. **Consequences** — Tradeoffs. What you gain, what you give up.

Most tutorials skip consequences. We won't.

```narration
Dekho yaar, pattern sirf code snippet nahi hai. Jab bhi tum ek pattern dekhte ho, always poocho — "yeh kaunsi problem solve kar raha hai?" aur "kya trade-off hai?" Agar tum sirf code copy karte ho bina context samjhe, toh pattern tumhara dushman ban sakta hai.
```

---

## How It Actually Works

### The Singleton Pattern

**Intent:** Ensure a class has only one instance and provide a global point of access to it.

**When does this actually matter?**

The classic examples: database connection pools, configuration managers, logging systems. The reasoning: creating multiple instances is either expensive (DB connections) or incorrect (two configs fighting each other) or wasteful (100 identical logger objects).

In Java, you've probably seen this:

```java
// Java Singleton — the "classic" approach
public class DatabasePool {
    private static DatabasePool instance;

    private DatabasePool() {}  // private constructor — nobody outside can call new

    public static DatabasePool getInstance() {
        if (instance == null) {
            instance = new DatabasePool();
        }
        return instance;
    }
}
```

Java can enforce the pattern via private constructors. Python cannot. There is no `private` keyword. So how do we do it?

### Python Approach 1: Module-Level Singleton (The Pythonic Way)

```python
# config.py — this IS a singleton already
# Python modules are loaded once and cached in sys.modules

import os

class _Config:
    def __init__(self):
        self.db_url = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
        self.debug = os.environ.get("DEBUG", "false").lower() == "true"
        self.max_connections = int(os.environ.get("MAX_CONN", "10"))

# Module-level instance — created once, imported everywhere
config = _Config()

# Usage in any other file:
# from config import config
# print(config.db_url)  # same object every time
```

When Python imports a module, it executes it once and stores the result in `sys.modules`. Every subsequent `import` returns the cached module. So a module-level object **is already a singleton**. No magic needed.

### Python Approach 2: `__new__` Override

```python
class DatabasePool:
    _instance = None  # class-level variable, shared across all "instances"

    def __new__(cls, *args, **kwargs):
        # __new__ creates the object; __init__ initializes it
        if cls._instance is None:
            # super().__new__(cls) actually allocates memory for the object
            cls._instance = super().__new__(cls)
            # Mark it as uninitialized so __init__ can run once
            cls._instance._initialized = False
        return cls._instance  # always return the same object

    def __init__(self, host="localhost", port=5432):
        if self._initialized:
            return  # __init__ is called every time you do DatabasePool(...)
                    # but we only want to initialize ONCE
        self.host = host
        self.port = port
        self._pool = []  # actual connection pool would go here
        self._initialized = True
        print(f"Pool initialized: {host}:{port}")

# Test it
pool1 = DatabasePool("prod-db", 5432)  # prints: Pool initialized: prod-db:5432
pool2 = DatabasePool("other-db", 5433) # prints nothing — same instance returned
print(pool1 is pool2)                   # True
print(pool2.host)                       # "prod-db" — pool2 IS pool1
```

Notice: `__new__` is called before `__init__`. `__new__` controls whether a new object is allocated. `__init__` initializes it. By overriding `__new__`, we can return the same object every time without preventing `__init__` from being called — hence the `_initialized` guard.

### Python Approach 3: Metaclass Singleton

```python
class SingletonMeta(type):
    """
    A metaclass that makes any class it governs a Singleton.
    The metaclass's __call__ controls what happens when you do ClassName().
    """
    _instances = {}  # stores one instance per class that uses this metaclass

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # super().__call__() runs __new__ + __init__ normally
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger(metaclass=SingletonMeta):
    def __init__(self, name="app"):
        self.name = name
        self.entries = []

    def log(self, message):
        self.entries.append(message)
        print(f"[{self.name}] {message}")


class CacheManager(metaclass=SingletonMeta):
    def __init__(self):
        self._cache = {}


# Each class gets its own singleton — they don't interfere
log1 = Logger("service-a")
log2 = Logger("service-b")   # "service-b" is ignored — same instance
print(log1 is log2)           # True
print(log2.name)              # "service-a"

cache = CacheManager()        # separate singleton from Logger
```

The metaclass approach is the most reusable — you define the Singleton behavior once in the metaclass, and any class that uses `metaclass=SingletonMeta` gets it for free.

```narration
Ab yeh teen approaches dekhe — module-level, __new__ override, aur metaclass. Practical production mein zyada tar module-level hi use hota hai kyunki Python ka import system yeh free mein de deta hai. __new__ approach tab use karo jab tumhe ek class API chahiye. Metaclass tab jab tumhe yeh behavior multiple classes mein spread karna ho.
```

---

## The Rule

> **Rule:** A Singleton guarantees one instance. But "one instance" means one per process, not one per application. In multi-process or multi-node deployments, each process has its own Singleton.

> **Rule:** Prefer module-level singletons in Python. They are simpler, idiomatic, and thread-safe by virtue of the GIL protecting module imports.

---

## Production Story

### The Bug: Config That Lied in Tests

A team built a `Config` class as a Singleton using `__new__`. Their main app worked fine. But their test suite started behaving strangely — tests that ran in isolation passed, but in sequence they failed because a test that modified `Config` was polluting later tests.

**The Buggy Code:**

```python
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db_url = "postgresql://prod/mydb"
            cls._instance.debug = False
        return cls._instance

# test_a.py
def test_with_debug():
    config = Config()
    config.debug = True  # mutates the singleton!
    assert config.debug is True

# test_b.py — runs AFTER test_a
def test_normal_behavior():
    config = Config()
    # config.debug is STILL True because it's the same object
    # This test fails in ways that seem random
    assert config.debug is False  # FAILS
```

The problem: Singletons carry state across test boundaries. There's no "reset" mechanism.

**The Fix — Option A: Add a reset method for tests:**

```python
class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _reset(self):
        """Only for testing. Never call in production."""
        self.__class__._instance = None

# In conftest.py
import pytest

@pytest.fixture(autouse=True)
def reset_config():
    yield
    Config()._reset()  # clean up after every test
```

**The Fix — Option B (better): Don't use Singleton for config. Use dependency injection.**

```python
# config.py
from dataclasses import dataclass

@dataclass
class Config:
    db_url: str = "postgresql://prod/mydb"
    debug: bool = False

# main.py
config = Config()  # one instance, but not enforced by class — just by discipline

# test_a.py — each test gets a fresh config, no pollution
def test_with_debug():
    config = Config(debug=True)
    assert config.debug is True
```

> **Warning:** Singleton is the most tested design pattern in job interviews AND the most argued-about in code reviews. Know when NOT to use it. If you find yourself adding `_reset()` methods for tests, that's a signal your Singleton is causing more harm than good.

```narration
Yaar yeh production story bahut common hai. Jab bhi tum Singleton use karte ho, yaad rakho — global mutable state hamesha tests mein problem karega. Agar tumhara Singleton mutable hai, toh seriously socho kya tum actually ise chahte ho, ya dependency injection better rahega.
```

---

## Going Deeper

### Thread Safety: What the GIL Actually Protects

Python's GIL means only one thread runs Python bytecode at a time. Does this make `__new__`-based Singletons thread-safe?

**Mostly yes, but with a caveat:**

```python
import threading

class DatabasePool:
    _instance = None

    def __new__(cls):
        # This check-then-act is two operations:
        # 1. Read cls._instance
        # 2. If None, create and assign
        # The GIL can release between these two steps
        # on certain Python implementations or IO-heavy scenarios
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

In CPython, the GIL makes simple attribute reads/writes atomic at the bytecode level. But the pattern `if x is None: x = create()` is multiple bytecodes — technically non-atomic. In practice with CPython it's rarely an issue, but to be correct:

```python
import threading

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()  # class-level lock

    def __new__(cls):
        if cls._instance is None:           # First check (no lock — fast path)
            with cls._lock:                 # Acquire lock
                if cls._instance is None:   # Second check (double-checked locking)
                    cls._instance = super().__new__(cls)
        return cls._instance
```

This is the **double-checked locking** pattern — same as Java's volatile-based DCL. Check once without lock (fast), acquire lock only if needed, check again inside lock (correct).

### Singleton vs Borg Pattern

The Borg pattern is a Python curiosity: instead of one instance, you have many instances that **share state**:

```python
class Borg:
    _shared_state = {}  # all instances share this dict

    def __init__(self):
        self.__dict__ = self._shared_state  # every instance's namespace IS the shared dict

b1 = Borg()
b2 = Borg()
b1.x = 42
print(b2.x)        # 42 — they share state
print(b1 is b2)    # False — different objects, same data
```

Borg achieves the practical goal of Singleton (shared state) without restricting instantiation. Useful when subclassing is needed.

### When Singleton Is Justified in 2024

Real production use cases where Singleton genuinely makes sense:

```
JUSTIFIED                          NOT JUSTIFIED
────────────────────────────────── ──────────────────────────────────
Connection pool manager            Service classes ("UserService")
App-level config (read-only)       Repositories
Logger (write-only, thread-safe)   Any class with complex mutable state
Feature flag client                Anything you want to test in isolation
Hardware interface (serial port)   "I only need one anyway"
```

```narration
Thread safety wala part bahut important hai yaar, especially agar tum multi-threaded backends likh rahe ho. Double-checked locking ka pattern Java developers ke liye familiar hoga — Python mein same concept apply hota hai. Borg pattern ek fun trivia hai, but real production mein module-level singleton hi king hai.
```

---

## Connecting the Dots

**What comes next:** Lesson 2 covers Factory Method — the pattern that solves "I need to create objects but don't want to hardcode which class to instant