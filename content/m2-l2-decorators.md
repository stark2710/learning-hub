---
title: "Decorators From Scratch"
module: "Python Functions Deep Dive"
domain: "Python Mastery"
lesson_id: "m2-l2-decorators"
prev: "m2-l1-first-class-functions"
next: "m2-l3-generators"
duration: "~35 min"
---

```system_prompt
You are a Python expert teaching an experienced Java/backend developer.
Always respond in plain English. Be concise and precise.
This lesson covers Python decorators — how they work mechanically, how to write them correctly, and how functools.wraps matters.
When comparing to Java, be precise: Python decorators are runtime callables that execute at import time and transform the function object. Java @Annotation is compile-time metadata read by frameworks via reflection — it does not run code or replace the annotated element.
Explain decorator stacking order clearly: @A @B means greet = A(B(greet)), so B wraps first, A wraps second. At call time, A's wrapper executes first.
When explaining functools.wraps, focus on what concretely breaks without it: Flask/FastAPI routing, pytest test names, inspect.signature, and help() output.
Never use Hinglish or Hindi — only English.
```

## What You'll Learn

- That `@decorator` is syntactic sugar for `func = decorator(func)` — evaluated at import time, nothing magic
- How to write a decorator that preserves the original function's identity using `functools.wraps`
- How parameterized decorators (`@retry(3)`) work — the three-level "decorator factory" pattern
- How decorator stacking order works and how to predict the output when decorators are chained

```narration
Lesson 1 mein humne dekha ki functions objects hain aur closures variables capture karte hain. Aaj woh dono cheezein combine hongi — decorators mein. Ek decorator basically ek function hai jo doosre function ko wrap karta hai. At symbol sirf syntactic sugar hai, andar kuch magical nahi ho raha. Yeh concept Python ka sabse powerful feature hai production code mein — logging, timing, authentication, retry — sab decorator se hota hai.
```

---

## The Mental Model

In Lesson 1 we established that a function is an object, and you can pass it to another function or return it from one. Decorators are exactly that pattern — made convenient with the `@` symbol.

When Python sees this:

```python
@timer
def fetch_user(user_id):
    ...
```

It does **exactly** this after the `def` block executes:

```python
def fetch_user(user_id):
    ...
fetch_user = timer(fetch_user)   # timer receives the function object, returns a new one
```

The `@` line runs `timer(fetch_user)` and rebinds the name `fetch_user` to whatever comes back. `timer` is just a function that takes a function and returns a function.

The function returned by `timer` is almost always a **closure** — it closes over the original `fetch_user` so it can call it from inside the wrapper:

```
BEFORE @timer:

  fetch_user ──────────────► [ function object: fetch_user ]

AFTER @timer:

  fetch_user ──────────────► [ function object: wrapper ]   ← new object
                                        │
                                        │  .__closure__[0]
                                        ▼
                               [ cell: original_fn ]
                                        │
                                        ▼
                              [ original function object ]
```

`fetch_user` now points to `wrapper`. Calling `fetch_user(42)` calls `wrapper(42)`, which calls the original inside. The original function is still alive because `wrapper.__closure__` holds a reference to the cell that holds it — pure refcounting from Module 1.

```narration
Decorator ka mental model seedha hai — at symbol sirf reassignment hai. Python def statement chalati hai, function object banta hai, phir decorator us object ko leke ek naya wrapped object return karta hai, aur original naam woh naya object ko point karne lagta hai. Andar woh closure hai jo original function ko cell mein capture karta hai — wahi cell object mechanics jo humne m2-l1 mein seekhi. Isliye closures ko samajhna decorators ke liye zaroori tha.
```

---

## How It Actually Works

### Writing your first decorator

```python
import time
import functools

def timer(func):                    # receives the function object
    @functools.wraps(func)          # explained in next subsection
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)   # call the original with all its args
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper                  # return the new callable

@timer
def fetch_user(user_id):
    time.sleep(0.1)
    return {"id": user_id, "name": "Bharat"}

user = fetch_user(42)   # prints: fetch_user took 0.1001s
```

`wrapper(*args, **kwargs)` forwards all positional and keyword arguments to the original — this is the standard pattern. The decorator does not need to know the signature of the wrapped function.

### Why `functools.wraps` is non-negotiable

Without `@functools.wraps(func)`, the wrapper replaces the function's identity:

```python
def timer_no_wraps(func):
    def wrapper(*args, **kwargs):    # wrapper's __name__ is literally "wrapper"
        return func(*args, **kwargs)
    return wrapper

@timer_no_wraps
def fetch_user(user_id):
    """Fetch a user by ID from the database."""
    ...

print(fetch_user.__name__)   # 'wrapper'    ← WRONG, should be 'fetch_user'
print(fetch_user.__doc__)    # None         ← WRONG, docstring is gone
```

With `@functools.wraps(func)`, the wrapper inherits the original's identity:

```python
@timer
def fetch_user(user_id):
    """Fetch a user by ID from the database."""
    ...

print(fetch_user.__name__)      # 'fetch_user'                      ✓
print(fetch_user.__doc__)       # 'Fetch a user by ID from the database.'  ✓
print(fetch_user.__wrapped__)   # <function fetch_user at 0x...>    ✓
```

`functools.wraps` copies `__name__`, `__qualname__`, `__doc__`, `__dict__`, `__module__`, and `__annotations__` from the original to the wrapper, and sets `__wrapped__` pointing to the original. The `__wrapped__` attribute lets you reach the unwrapped function:

```python
original = fetch_user.__wrapped__   # bypass the timer entirely
```

### Parameterized decorators — the decorator factory pattern

`@retry(max_attempts=3)` takes an argument. `@timer` does not. The difference is one extra level of nesting:

```
@timer          →   timer(func)          — 2 levels: timer, wrapper
@retry(3)       →   retry(3)(func)       — 3 levels: retry, decorator, wrapper
```

```python
def retry(max_attempts=3, delay=0.5):        # OUTER — accepts configuration
    def decorator(func):                      # MIDDLE — accepts the function
        @functools.wraps(func)
        def wrapper(*args, **kwargs):         # INNER — runs on every call
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.2)
def call_external_api(endpoint):
    ...   # might raise requests.Timeout or ConnectionError
```

When Python executes `@retry(max_attempts=3, delay=0.2)`:
1. Calls `retry(max_attempts=3, delay=0.2)` → returns `decorator` (a closure over the config)
2. Calls `decorator(call_external_api)` → returns `wrapper` (a closure over `func` and the config)
3. Rebinds `call_external_api` to `wrapper`

```narration
Do tarah ke decorators hain — bina argument ke aur argument ke saath. Bina argument ke sirf do levels hain. Argument ke saath teen levels hain — yeh decorator factory pattern hai. retry decorator backend mein bahut common hai — external APIs, database calls, network requests. Ek important baat — outer function mein configuration capture hoti hai, middle mein function capture hota hai, inner wrapper actual replacement hai. Teen closures ek chain mein.
```

---

## The Rule

> **`@decorator` is exactly `func = decorator(func)`, evaluated at import time. A decorator is a function that takes a function and returns a (usually wrapped) function. Always use `functools.wraps` to preserve `__name__`, `__doc__`, and `__wrapped__`.**

> **Corollary: `@retry(n)` is a decorator factory — `retry(n)` runs first and returns the real decorator, which then wraps the function. Three levels of nesting, not two.**

```narration
Rule yaad karo — at symbol sirf reassignment hai, import time par hota hai. functools.wraps hamesha lagao — yeh sirf naam preserve nahi karta, balki frameworks toot jaate hain iske bina. Parameterized decorator mein teen functions hote hain — factory config leti hai, decorator function leti hai, wrapper har call pe run karta hai. Yeh pattern CPython mein har jagah hai — asyncio, functools, standard library.
```

---

## Production Story

A backend developer is adding request logging to a Flask API. They write a clean `@log_request` decorator and apply it to two endpoints:

```python
# BUGGY — missing functools.wraps
from flask import Flask, jsonify

def log_request(func):
    def wrapper(*args, **kwargs):          # wrapper.__name__ == "wrapper"
        print(f"[LOG] {func.__name__} called")
        return func(*args, **kwargs)
    return wrapper

app = Flask(__name__)

@app.route("/users")
@log_request
def get_users():
    return jsonify([])

@app.route("/orders")
@log_request           # both decorated functions are now named "wrapper"
def get_orders():
    return jsonify([])
```

Starting the app raises:

```
AssertionError: View function mapping is overwriting an existing endpoint function: wrapper
```

**Why:** Flask uses `func.__name__` to register route endpoints in an internal dictionary. Both `get_users` and `get_orders` — after decoration — have `__name__ == "wrapper"`. Flask tries to register two routes under the key `"wrapper"` and throws an assertion on the collision.

```python
# FIX — add functools.wraps
def log_request(func):
    @functools.wraps(func)               # preserves __name__
    def wrapper(*args, **kwargs):
        print(f"[LOG] {func.__name__} called")
        return func(*args, **kwargs)
    return wrapper
```

Now `get_users.__name__` is `"get_users"` and `get_orders.__name__` is `"get_orders"`. Flask registers them under separate keys.

> **Warning:** FastAPI has the same requirement — it uses `func.__name__` to generate OpenAPI operation IDs. Missing `functools.wraps` causes duplicate IDs in generated API docs and breaks clients that depend on unique operation names. This also affects pytest: without `wraps`, all your decorated test functions report the same name in failure output, making debugging painful.

```narration
Yeh bug production mein kaafi common hai. Flask mein do routes pe decorator lagao bina functools.wraps ke, aur dono functions ka naam wrapper ho jaata hai. Flask crash karta hai duplicate key se. FastAPI mein OpenAPI docs mein duplicate operation IDs aate hain. Pytest mein test names toot jaate hain. Fix sirf ek line hai — functools.wraps add karo. Yeh ek interview question bhi hai — "functools.wraps kyu zaroori hai?" — aur ab tumhare paas concrete answer hai.
```

---

## Going Deeper

### Class-based decorators

A class can act as a decorator if it implements `__call__`. This is useful when the decorator needs to maintain state across calls:

```python
import functools

class CallCount:
    def __init__(self, func):
        functools.update_wrapper(self, func)   # equivalent of @wraps for classes
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"{self.func.__name__} called {self.count} times")
        return self.func(*args, **kwargs)

@CallCount
def process_order(order_id):
    return f"processed {order_id}"

process_order(1)   # process_order called 1 times
process_order(2)   # process_order called 2 times
print(process_order.count)   # 2 — state lives on the instance
```

When Python sees `@CallCount`, it calls `CallCount(process_order)`, creating an instance with `self.func = process_order`. Calling `process_order(1)` calls `instance.__call__(1)`. State persists across calls because it's an attribute on the instance, not a cell in a closure.

### Decorator stacking order

Multiple decorators apply bottom to top at definition time, but the outermost executes first at call time:

```python
def bold(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper

def italic(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return f"<i>{func(*args, **kwargs)}</i>"
    return wrapper

@bold
@italic
def greet(name):
    return f"Hello, {name}"

# Desugars to: greet = bold(italic(greet))
# Call path:   bold_wrapper → italic_wrapper → original greet
print(greet("Bharat"))   # <b><i>Hello, Bharat</i></b>
```

Think of it as onion layers — `@italic` is the inner layer, `@bold` is the outer skin. Reading the decorators top-to-bottom maps to outermost-to-innermost in the call stack.

### The `__wrapped__` chain and `inspect.unwrap`

`functools.wraps` sets `__wrapped__` on the returned function, pointing to the original. For stacked decorators, this creates a chain:

```python
@bold
@italic
def greet(name):
    return f"Hello, {name}"

import inspect
original = inspect.unwrap(greet)   # follows __wrapped__ chain to the real function
print(original("Bharat"))          # Hello, Bharat  (no bold, no italic)
```

This is how testing frameworks and debuggers reach the underlying function to inspect its signature or run it in isolation.

```narration
Teen advanced points — class-based decorator __init__ mein function leti hai, __call__ mein wrapper run hota hai, aur state instance attributes mein rakhte hain, closure cells mein nahi. Stacking mein bottom decorator pehle apply hota hai, lekin call time pe top wala pehle run karta hai — onion layers ki tarah. __wrapped__ attribute se original function tak pahunch sakte ho, inspect.unwrap poori chain follow karta hai. Yeh testing aur debugging mein useful hai.
```

---

## Connecting the Dots

Everything from Lesson 1 applies here. When `@timer` executes, the original function's refcount increases because `wrapper.__closure__` holds a reference to the cell containing it. When the decorated function goes out of scope, the wrapper is freed, the closure releases the cell, and the original function is freed — classic Module 1 refcounting.

**Lesson 3 (Generators):** `yield` inside a decorator's wrapper can implement setup/teardown without a `try/finally` — a pattern you'll see in database transaction decorators. Generators are also where you encounter `@` applied to methods differently.

**Module 3 (Concurrency):** `@functools.cached_property`, `@asyncio.coroutine` (historical), and lock-as-decorator patterns all use exactly what you just learned. The `@cached_property` implementation is a descriptor-based decorator — same mechanics, different `__get__` hook.

**Module 7 (Structural Patterns):** The Decorator design pattern is the OOP analog — adding behavior by wrapping objects. Python's function decorators show the same composable-wrapping idea without a class hierarchy.

```narration
Decorators Module 1 aur Module 2 Lesson 1 ke direct application hain — refcounting, closures, higher-order functions. Aage generators mein yield decorators ke andar context manager jaise kaam kar sakta hai. Concurrency mein cached_property aur async decorators milenge. Design patterns mein Decorator Pattern same idea hai but classes ke saath. Ek concept ko deeply samajhna itne jagah kaam aata hai.
```

---

## Practice

### Exercise 1 — Trace Stacking Order

```python
import functools

def uppercase(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper

def exclaim(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs) + "!"
    return wrapper

@uppercase
@exclaim
def greet(name):
    return f"hello {name}"

print(greet("bharat"))   # What is the output?
print(greet.__name__)    # What is this?
```

<details>
<summary>Answer</summary>

**Output: `HELLO BHARAT!`**

**`greet.__name__` is `"greet"`** (preserved by `functools.wraps` on both decorators)

**How the stacking works:**

`@uppercase @exclaim def greet` desugars to: `greet = uppercase(exclaim(greet))`

1. `exclaim(greet)` wraps the original → returns `exclaim_wrapper` (named `"greet"` via wraps)
2. `uppercase(exclaim_wrapper)` wraps that → returns `uppercase_wrapper` (named `"greet"` via wraps)

**Call path for `greet("bharat")`:**
1. `uppercase_wrapper("bharat")` executes first (outermost)
2. It calls `exclaim_wrapper("bharat")`
3. `exclaim_wrapper` calls the original `greet("bharat")` → returns `"hello bharat"`
4. `exclaim_wrapper` appends `"!"` → returns `"hello bharat!"`
5. `uppercase_wrapper` calls `.upper()` → returns `"HELLO BHARAT!"`

**The rule in action:** bottom decorator (`@exclaim`) wraps first, top decorator (`@uppercase`) wraps last. At call time, top executes first (outermost), bottom executes last (innermost, closest to original).

</details>

### Exercise 2 — Write a Parameterized Decorator

Write a `@validate_types` decorator that checks the types of positional arguments against a sequence of expected types. If any argument is the wrong type, raise `TypeError` with a descriptive message:

```python
@validate_types(int, str)
def create_user(user_id, username):
    return {"id": user_id, "name": username}

create_user(42, "bharat")    # works fine
create_user("42", "bharat")  # TypeError: argument 0: expected int, got str
```

<details>
<summary>Solution</summary>

```python
import functools

def validate_types(*expected_types):           # outer: captures type specs
    def decorator(func):                        # middle: captures the function
        @functools.wraps(func)
        def wrapper(*args, **kwargs):           # inner: runs on every call
            for i, (arg, expected) in enumerate(zip(args, expected_types)):
                if not isinstance(arg, expected):
                    raise TypeError(
                        f"argument {i}: expected {expected.__name__}, "
                        f"got {type(arg).__name__}"
                    )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate_types(int, str)
def create_user(user_id, username):
    return {"id": user_id, "name": username}

# create_user(42, "bharat")   → {"id": 42, "name": "bharat"}
# create_user("42", "bharat") → TypeError: argument 0: expected int, got str
# create_user(42, 99)         → TypeError: argument 1: expected str, got int
```

**Key points:**
- Three levels match the pattern: `validate_types` (factory), `decorator` (receives `func`), `wrapper` (runs each call)
- `zip(args, expected_types)` pairs each positional arg with its expected type — stops at the shorter sequence, so extra args beyond the type list are silently allowed
- `isinstance` handles subclasses: `isinstance(True, int)` is `True` because `bool` is a subclass of `int` — if you want strict type equality, use `type(arg) is expected`
- `functools.wraps` is on `wrapper`, not `decorator` — it wraps the innermost replacement function

</details>

---

## Study Notes

**Q: How is Python's `@decorator` different from Java's `@Annotation`?**
Java annotations are compile-time metadata attached to a declaration — they don't execute code and don't transform the annotated method. Spring reads them via reflection at runtime to decide routing or injection, but the annotation itself does nothing. Python decorators are runtime callables that execute at import time and actually replace the function object with a new one. `@app.route("/users")` in Flask *calls* `app.route("/users")` which registers the route and returns the decorator function that then wraps your handler. They look similar syntactically but are fundamentally different mechanisms.

**Q: If I stack `@A @B @C` on a function, in what order do they apply at definition time and execute at call time?**
At definition time, they apply bottom to top: `func = A(B(C(func)))` — `C` wraps first, then `B` wraps that result, then `A` wraps that. At call time, they execute top to bottom: `A`'s wrapper runs first, calls `B`'s wrapper, which calls `C`'s wrapper, which finally calls the original. Think of it as concentric onion layers — `@C` is the innermost layer closest to the original, `@A` is the outermost skin. Reading decorators top-to-bottom maps to outermost-to-innermost in the call stack.

**Q: What exactly does `functools.wraps` copy, and what concretely breaks without it?**
`functools.wraps` copies `__name__`, `__qualname__`, `__doc__`, `__dict__`, `__module__`, and `__annotations__` from the wrapped function to the wrapper, and sets `__wrapped__` to point to the original. Without it: Flask and FastAPI use `__name__` to register routes — two decorated functions both named `"wrapper"` cause an `AssertionError` or duplicate OpenAPI operation IDs. `pytest` identifies tests by `__name__` — all decorated tests report the same failure name. `inspect.signature` shows `*args, **kwargs` instead of the real parameter names. `help()` shows no docstring. In production, always use `functools.wraps`.

---

## Lesson Complete

- A decorator is a callable that takes a function and returns a replacement function
- `@decorator` is syntactic sugar for `func = decorator(func)` executed at import time
- The wrapper pattern: outer function captures `func`, inner `wrapper` runs before/after, returns `wrapper`
- `functools.wraps` preserves `__name__`, `__doc__`, and signature — always use it in production decorators
- Decorators with arguments need three levels: factory → decorator → wrapper
- Stacking decorators applies bottom-up at definition and top-down at call time
