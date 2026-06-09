---
title: "First-class Functions & Closures"
module: "Python Functions Deep Dive"
domain: "Python Mastery"
lesson_id: "m2-l1-first-class-functions"
prev: "m1-l3-memory-mgmt"
next: "m2-l2-decorators"
duration: "~40 min"
---

```system_prompt
You are a Python expert teaching an experienced Java/backend developer.
Always respond in plain English. Be concise and precise.
Relate Python concepts to Java equivalents when helpful — e.g. functional interfaces, lambdas, anonymous classes.
When explaining closures, use the "cell object" mental model.
Never use Hinglish or Hindi — only English.
```

## What You'll Learn

- How Python functions are full objects with attributes like `__code__`, `__defaults__`, and `__closure__`
- What a closure actually is — how Python uses cell objects to share a variable between an outer and inner scope
- Why closures capture the *variable*, not the *value* — and how this causes the infamous loop bug
- How `nonlocal` modifies a variable in the enclosing scope without making it global

```narration
Module 1 mein humne dekha ki Python mein names objects ko point karte hain. Ab woh same concept functions par apply karte hain. Python mein function ek object hai — exactly jaise integer ya list. Aaj hum closures samjhenge — yeh Java developers ke liye ek completely naya concept hai.
```

---

## The Mental Model

**Where we left off** — Module 1 showed that Python names are labels pointing to objects, refcounting tracks how many labels point to an object, and the GC handles cycles. Now we apply all of that to functions — which are just objects you can pass around, store in variables, and nest inside other functions.

In Java, a method belongs to a class — you can't store a method in a variable and pass it around on its own without functional interfaces. Python has no such restriction. **Every function is an object**, just like an integer or a list. This is what "first-class" means: functions have the same rights as any other value.

### Functions are objects — this is not a metaphor

When Python executes a `def` statement, it creates a **function object** in memory and binds the function's name to it, exactly like an assignment. That function object has attributes you can read and even modify:

```python
def greet(name):
    return f"Hello, {name}"

# greet is just a name pointing to a function object
print(type(greet))                      # <class 'function'>
print(greet.__name__)                   # 'greet'
print(greet.__code__)                   # code object at 0x...
print(greet.__code__.co_varnames)       # ('name',) — local variable names

# Assign a function to another name — just like any object
say_hi = greet
print(say_hi("Bharat"))                 # Hello, Bharat
print(say_hi is greet)                  # True — same object, two names
```

Notice `say_hi is greet` is `True`. Two names, one object — exactly what we saw in Module 1 with integers and lists.

### Higher-order functions

Because functions are objects, you can pass them to other functions, return them from functions, and store them in lists and dicts:

```python
def apply_twice(func, value):
    return func(func(value))

def double(x):
    return x * 2

print(apply_twice(double, 3))  # 12  (double(double(3)))
```

### What is a closure?

A closure is a function that **remembers the variables from the scope where it was created**, even after that scope has finished executing:

```python
def make_multiplier(factor):     # outer function
    def multiply(x):             # inner function
        return x * factor        # uses 'factor' from outer scope
    return multiply              # return the inner function object

triple = make_multiplier(3)
print(triple(10))  # 30
print(triple(7))   # 21

# make_multiplier() has returned, its stack frame is gone.
# Yet 'factor' (the value 3) is still accessible via triple.
print(triple.__closure__)                        # (<cell at 0x...>,)
print(triple.__closure__[0].cell_contents)       # 3
```

When `make_multiplier` creates `multiply`, Python sees that `multiply` uses `factor` from the enclosing scope. It wraps `factor` in a **cell object** — a small shared container. Both the outer scope and `multiply` hold a reference to that same cell. When `make_multiplier` returns and its stack frame is gone, the cell object lives on because `triple.__closure__` still holds a reference to it.

```
make_multiplier(3) returns, stack frame gone. But:

triple ───────────────────► [ function object: multiply ]
                                       │
                                       │  .__closure__[0]
                                       ▼
                                [ cell object ]
                                       │
                                       │  .cell_contents
                                       ▼
                                 [ int object: 3 ]

The cell object is the shared container between outer and inner scope.
As long as triple is alive, the cell is alive, and 3 is alive.
```

```narration
Functions pehli cheez — Java mein method class ka hissa hota hai, Python mein function ek object hai jo aap variable mein store kar sakte ho, pass kar sakte ho, return kar sakte ho. Jab def statement chalti hai, ek function object memory mein banta hai. Closure tab hota hai jab inner function outer scope ki variable ko use karta hai. Python us variable ko ek cell object mein wrap karta hai — ek shared container — jaise refcounting ka extension.
```

---

## How It Actually Works

### The LEGB rule — where Python looks for names

When Python sees a name inside a function, it searches four scopes in order:

```
L — Local       variables defined inside the current function
E — Enclosing   variables from any enclosing function (closest first)
G — Global      variables at module level
B — Built-in    names like print, len, range

Python stops at the first scope where it finds the name.
```

Inner functions can read outer variables because Python finds them in the **E (Enclosing)** scope. But if the inner function tries to *assign* to an outer variable without `nonlocal`, Python treats it as a new local variable instead:

```python
def outer():
    count = 0

    def inner():
        count += 1      # assignment! Python treats count as LOCAL to inner
        return count    # but it was never assigned first → UnboundLocalError

    inner()

outer()   # UnboundLocalError: local variable 'count' referenced before assignment
```

The fix is `nonlocal`. It tells Python: "I'm assigning to a variable, but look in the enclosing scope, not here."

```python
def make_counter():
    count = 0

    def increment():
        nonlocal count      # tells Python: 'count' lives in enclosing scope
        count += 1
        return count

    return increment

counter = make_counter()
print(counter())   # 1
print(counter())   # 2
print(counter())   # 3
# Each call increments the SAME 'count' cell object
```

### Inspecting the closure with `__closure__`

Every function that closes over variables has a `__closure__` tuple. Each element is a **cell object** with a `cell_contents` attribute. The order matches `func.__code__.co_freevars`:

```python
def make_adder(base, label):
    def add(x):
        return f"{label}: {base + x}"
    return add

add5 = make_adder(5, "result")

print(add5.__code__.co_freevars)             # ('base', 'label')
print(add5.__closure__[0].cell_contents)     # 5    (base)
print(add5.__closure__[1].cell_contents)     # 'result'  (label)
print(add5(10))                              # result: 15
```

A function with no closure has `__closure__ = None`:

```python
def simple(x):
    return x * 2

print(simple.__closure__)               # None
print(simple.__code__.co_freevars)      # ()
```

```narration
LEGB rule yaad karo — Local, Enclosing, Global, Built-in. Python name dhundne ke liye is order mein scope check karta hai. Enclosing scope ka matlab hai outer function. Agar inner function outer variable ko assign karne ki koshish kare bina nonlocal ke, toh Python us variable ko local maanta hai aur UnboundLocalError aata hai. nonlocal keyword explicitly bolata hai ki yeh variable enclosing scope ka cell object hai.
```

---

## The Rule

> **Closures capture the *variable* (the cell object), not the *value*. If the variable changes after the closure is created, the closure sees the new value — not a snapshot of the old one.**

> **Corollary:** All closures created in a loop that close over the loop variable share the *same cell*. After the loop ends, every closure sees the loop's final value.

```narration
Yeh rule bohot important hai — closure variable capture karta hai, value nahi. Cell object shared hota hai. Loop mein banaye gaye saare closures ek hi cell share karte hain, toh loop khatam hone ke baad sab same final value dekhte hain. Yeh ek classic interview question bhi hai.
```

---

## Production Story

A developer is building a config dashboard with 5 environment buttons. Each button should log which environment was clicked:

```python
# BUGGY: all handlers print the last value
environments = ["dev", "staging", "prod", "us-east", "eu-west"]
handlers = []

for env in environments:
    def on_click():
        print(f"Switching to: {env}")   # closes over 'env'
    handlers.append(on_click)

handlers[0]()   # Switching to: eu-west  ← WRONG (expected "dev")
handlers[1]()   # Switching to: eu-west  ← WRONG
handlers[4]()   # Switching to: eu-west  ← happens to be right
```

Every `on_click` closes over the **variable** `env` — the same cell. After the loop, `env` holds `"eu-west"`. All five closures share that one cell.

```
After loop ends:

handlers[0].__closure__[0] ──►  [ cell: env ]  ◄── handlers[1].__closure__[0]
                                      │         ◄── handlers[2].__closure__[0]
                                      ▼
                               [ str: "eu-west" ]  ← loop left env here

Five closures, ONE cell, ONE current value.
```

**Fix 1 — Default argument** (captures value at definition time, not call time):

```python
for env in environments:
    def on_click(e=env):          # e=env evaluates NOW — captures the current value
        print(f"Switching to: {e}")
    handlers.append(on_click)

handlers[0]()   # Switching to: dev   ✓
handlers[2]()   # Switching to: prod  ✓
```

**Fix 2 — `functools.partial`** (explicit, readable):

```python
from functools import partial

def on_click(env):
    print(f"Switching to: {env}")

handlers = [partial(on_click, env) for env in environments]
handlers[0]()   # Switching to: dev   ✓
```

`partial()` freezes the argument at creation time — no closure, no surprise.

```narration
Ek real production bug dekho — dashboard mein 5 buttons, har ek alag environment ke liye. Sab closures ek hi env cell share karte hain. Loop khatam hone ke baad, env ki value eu-west hai, toh saare handlers wahi print karte hain. Do fixes hain — default argument se value ko capture time par bind karo, ya functools.partial use karo jo argument explicitly freeze kar deta hai.
```

---

## Going Deeper

### Bytecode: LOAD_DEREF vs LOAD_FAST

CPython uses different opcodes depending on whether a variable is local or captured:

```python
import dis

def make_multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply

dis.dis(make_multiplier(3))
# LOAD_FAST   x       ← local variable, direct array index
# LOAD_DEREF  factor  ← from a cell object, one extra pointer hop
# BINARY_OP   *
# RETURN_VALUE
```

`LOAD_DEREF` is negligibly slower than `LOAD_FAST` (one extra pointer dereference), but knowing it exists explains what Python is doing when it resolves closure variables.

### Cell objects in CPython

A cell object (`PyCell_Type`) is a struct with a single pointer `ob_ref` to the contained object. Python marks variables as cell vs free in the code object:

```python
def outer():
    x = 10
    def inner():
        return x
    return inner

print(outer.__code__.co_cellvars)     # ('x',) — outer marks x as a cell var
inner_fn = outer()
print(inner_fn.__code__.co_freevars)  # ('x',) — inner sees it as a free var
```

### Closures vs classes

A closure is essentially a lightweight object with one callable entry point and private state:

```python
# Closure — clean for simple cases
def make_counter(start=0):
    count = [start]         # list trick: mutable container avoids nonlocal
    def increment():
        count[0] += 1
        return count[0]
    return increment

# Class — better when state grows or you need multiple methods
class Counter:
    def __init__(self, start=0):
        self.count = start
    def __call__(self):
        self.count += 1
        return self.count
    def reset(self):
        self.count = 0
```

Use closures when you need one callable with a bit of private state. Use a class when you need multiple methods, introspection, or the state is complex enough to deserve named fields.

### Lambda closures have the same behavior

```python
multipliers = [(lambda x, n=n: x * n) for n in range(1, 4)]
print(multipliers[0](5))   # 5  (×1)
print(multipliers[1](5))   # 10 (×2)
# n=n default arg is the same fix as in the production story
```

```narration
Thoda aur deep — CPython mein closure variables ke liye LOAD_DEREF opcode use hota hai, local variables ke liye LOAD_FAST. LOAD_DEREF ek extra pointer hop karta hai cell object tak, practically negligible difference hai. co_cellvars aur co_freevars code object ke attributes hain jo batate hain ki kaunse variables cells hain. Closure vs class — agar ek callable chahiye simple state ke saath, closure use karo. Complex state ya multiple methods ke liye class better hai.
```

---

## Connecting the Dots

Everything from Module 1 applies here. When `triple = make_multiplier(3)` runs, the function object's refcount increases (a name was bound to it). The cell object holding `factor` stays alive because `triple.__closure__` holds a reference to it — classic refcounting. If `triple` goes out of scope and no other references exist, the function object is freed, releasing the cell, releasing the integer 3.

The concept here — closures holding live references to variables — is the exact foundation of **Lesson 2: Decorators**. A decorator is a higher-order function that returns a closure. The `@` syntax is syntactic sugar for:

```python
# These two are identical:
@my_decorator
def my_func():
    ...

# is the same as:
def my_func():
    ...
my_func = my_decorator(my_func)   # decorator returns a closure wrapping my_func
```

---

## Practice

### Exercise 1 — Trace the Output

```python
def make_power(exp):
    def power(base):
        return base ** exp
    return power

square = make_power(2)
cube   = make_power(3)

print(square(4))                              # A: ?
print(cube(3))                                # B: ?
print(square is cube)                         # C: ?
print(square.__closure__[0].cell_contents)    # D: ?
print(cube.__closure__[0].cell_contents)      # E: ?
```

<details>
<summary>Answer</summary>

**A: `16`** — `square(4)` = `4**2` = 16. The closure holds `exp=2`.

**B: `27`** — `cube(3)` = `3**3` = 27. The closure holds `exp=3`.

**C: `False`** — `square` and `cube` are two *different* function objects, created by two separate calls to `make_power`. Each call creates a new closure with its own cell.

**D: `2`** — `square.__closure__[0]` is the cell holding `exp=2`.

**E: `3`** — `cube.__closure__[0]` is a *different* cell holding `exp=3`.

Key takeaway: each call to `make_power` creates an independent function object with its own closure and its own cell — no sharing between `square` and `cube`.

</details>

### Exercise 2 — Fix the Bug

```python
# BUGGY — UnboundLocalError
def make_accumulator():
    total = 0
    def add(amount):
        total = total + amount   # broken: Python sees assignment → treats total as local
        return total
    return add

acc = make_accumulator()
print(acc(10))   # should print 10
print(acc(5))    # should print 15
print(acc(3))    # should print 18
```

<details>
<summary>Solution</summary>

```python
def make_accumulator():
    total = 0
    def add(amount):
        nonlocal total          # declares: modify the enclosing scope's total
        total = total + amount  # now reads from cell, writes to cell
        return total
    return add
```

**Why it works:** `nonlocal total` tells Python to look in the enclosing scope's cell object for `total`, both when reading and writing. No new local variable is created.

**Alternative (pre-Python 3 style):** wrap in a list — `total = [0]` — and use `total[0] += amount`. This works because you're not assigning to `total` (which would trigger the local-variable rule), you're mutating the list it points to.

</details>

---

## Study Notes

**Q: How is Python's closure different from Java's lambda capturing?**
In Java, lambdas can only capture *effectively final* variables — the compiler rejects a lambda that closes over a variable that changes after capture. Python has no such restriction; closures capture the live cell object, so they always see the current value. This is more powerful but leads to the loop bug. Java's approach is safer: if the variable can't change, the snapshot vs. live-reference distinction doesn't matter.

**Q: Why does `nonlocal` exist if Python already has `global`?**
`global` makes a name refer to the module-level scope, bypassing everything in between. `nonlocal` makes a name refer to the *nearest enclosing function scope* that has that variable — not necessarily the module level. Without `nonlocal`, assigning to a variable inside a function always creates a new local variable, even if an enclosing scope has a variable with the same name. You need `nonlocal` for closures that need to mutate enclosing-scope state.

**Q: What is `functools.partial` and when should I use it over a closure?**
`partial(func, arg)` returns a new callable with `arg` pre-bound to `func`. It's equivalent to `lambda *args, **kw: func(arg, *args, **kw)` but more explicit and introspectable — `partial_obj.func` and `partial_obj.args` are readable. Use `partial` when you want to bind arguments at creation time and the intent is "fill in some arguments now, the rest later." Use a closure when the inner function needs to do more complex work with the captured variable, not just pass it as an argument.

**Q: Is the `list trick` (`count = [0]`) a good pattern or a code smell?**
It's a historical workaround for Python 2, which had no `nonlocal`. In Python 3, always use `nonlocal` — it's clearer, more readable, and signals intent. The list trick works because you're mutating the list (not reassigning `count`), so Python doesn't need a nonlocal declaration. But it hides the stateful intent and confuses readers. Only use it if you need Python 2 compatibility, which in 2026 you don't.

**Q: Does a function object get garbage collected when the closure that holds it goes out of scope?**
Yes — exactly. The closure's `__closure__` tuple holds a reference to each cell object. The cell holds a reference to the enclosed value. When the closure function object's refcount hits zero (no more names pointing to it), Python frees the function object, which releases the `__closure__` tuple, which releases the cell references, which may release the enclosed values if nothing else references them. The entire Module 1 refcounting model applies here.

