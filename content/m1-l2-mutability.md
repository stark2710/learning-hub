---
title: "Mutability & Its Consequences"
module: "Python Object Model"
domain: "Python Mastery"
lesson_id: "m1-l2-mutability"
prev: "m1-l1-object-model"
next: "m1-l3-memory-mgmt"
duration: "~28 min"
---

```system_prompt
You are a Python expert teaching an experienced Java/backend developer.
Always respond in plain English. Be concise and precise.
Relate Python concepts to Java equivalents when helpful.
Focus on the mutable vs immutable distinction and its production consequences.
Never use Hinglish or Hindi — only English.
```

## What You'll Learn

- Why `x += 1` and `lst += [1]` look identical but do something completely different under the hood
- The "immutable" tuple that contains a mutable list — and why `hash()` punishes you for it
- What "pass by object reference" really means — and how it differs from Java's pass-by-value-of-reference and C++'s pass-by-reference
- When `dict.copy()` is a footgun and you need `copy.deepcopy()` — illustrated with a real config-leakage bug

```narration
Is lesson mein hum mutability ka deep dive karenge. Dekhenge ki plus-equals operator list aur int par alag kaise behave karta hai, tuple ke andar mutable object ka trap, aur ek real production bug jo shallow copy ki wajah se 11 mahine tak chhupa raha.
```

---

## The Mental Model

There are exactly **two things** you can do with a name in Python:

1. **Rebind the name** — point the label at a different object. The old object is untouched.
2. **Mutate the object** — change the contents of the object the name points to. The name doesn't move.

In Java, `x = 5; x = 10` looks the same as Python — but it isn't. In Java, the box `x` *contains* `5`, then *contains* `10`. The container is mutated. In Python, two separate `int` objects exist; the name `x` slides from one to the other.

This split is invisible for **immutable** types — `int`, `str`, `tuple`, `frozenset`, `bytes` — because they offer no way to mutate themselves. Every operation on them produces a new object. So `x += 1` *must* rebind.

For **mutable** types — `list`, `dict`, `set`, custom classes — you have a choice. `lst.append(x)` mutates. `lst = lst + [x]` rebinds. `lst += [x]` mutates *and* rebinds to the same object. These are not interchangeable, and the difference is invisible until something breaks.

### Immutability is a property of the object, not the name

There is no `final` in Python. You cannot say "this name must always point to the same object." What you *can* say is "this object cannot be changed." Immutability lives in the type, not in the binding.

| | Java `final int x = 5` | Python `x = 5` (int) |
|---|---|---|
| Can name be reassigned? | No | Yes |
| Can object change? | n/a (primitives) | No (int is immutable) |
| Hashable? | n/a | Yes |

```narration
Do cheezein hoti hain Python mein — rebinding aur mutation. Immutable types jaise int aur str ke saath sirf rebinding possible hai, koi mutation nahi. Mutable types jaise list aur dict ke saath dono possible hain, aur dono alag dikhtay hain. Python mein koi `final` keyword nahi hai Java jaisa — immutability type ki property hai, name ki nahi.
```

---

## How It Actually Works

### 1. Rebinding with immutable types

```python
x = 100
print(id(x))   # e.g. 0x10c4a8
x += 1
print(id(x))   # DIFFERENT — int 101 is a new object
```

Internally Python calls `x.__add__(1)`, which returns a brand-new `int` object. The name `x` is then rebound to it. The original `int(100)` is now unreferenced and eligible for collection. There is no in-place version of `__iadd__` for `int` — there can't be.

### 2. Rebinding vs mutating with mutable types

```python
lst = [1, 2, 3]
print(id(lst))   # e.g. 0x7f3a

# Option A: rebind to a new list
lst = lst + [4]
print(id(lst))   # DIFFERENT — '+' on lists creates a new list

# Reset
lst = [1, 2, 3]

# Option B: mutate in place
lst += [4]
print(id(lst))   # SAME — '+=' on a list calls list.__iadd__, which extends in place
```

`lst + [4]` calls `list.__add__`, which builds a new list. `lst += [4]` calls `list.__iadd__`, which mutates `lst` and returns the same object.

This subtlety hits hardest when the list is shared:

```python
def append_in_place(seq):
    seq += [99]            # MUTATES the caller's list

def append_by_rebind(seq):
    seq = seq + [99]       # creates new local list; caller's list untouched

original = [1, 2, 3]
append_in_place(original)
print(original)            # [1, 2, 3, 99] — caller sees the mutation

original = [1, 2, 3]
append_by_rebind(original)
print(original)            # [1, 2, 3] — caller untouched
```

Two functions, one character of code different (`+=` vs `= +`), opposite behavior.

### 3. Pass by object reference — the precise answer

**C++ pass-by-reference** (`void f(int& x)`): the parameter is an *alias* for the caller's variable. `x = 10` inside `f` rebinds the caller's variable. You can swap two ints from inside a function.

**Java pass-by-value-of-reference** (`void f(List<Integer> x)`): Java copies the *reference value* (the pointer). The parameter and the argument point to the same object, so mutation is visible. But `x = new ArrayList<>()` inside the function does NOT change what the caller's variable points to.

**Python pass by object reference** (`def f(x): ...`): identical to Java's model for objects. The parameter is a new name in the function's local namespace, bound to the same object. Mutation is visible; rebinding inside `f` doesn't escape.

```python
def demo(x):
    print(id(x))        # same id as caller's
    x = [99]            # REBIND — does NOT affect caller
    print(id(x))        # different id now

a = [1, 2, 3]
demo(a)
print(a)                # [1, 2, 3] — still the same
```

So Python ≠ C++ pass-by-reference. Python = Java's object semantics.

### 4. The tuple-with-a-list trap

Tuples are immutable. But "immutable" means "the tuple's slots are fixed" — it doesn't mean the objects in those slots can't be mutated.

```python
t = (1, 2, [3, 4])

t[2] = [9, 9]            # TypeError: 'tuple' object does not support item assignment
t[2].append(5)           # WORKS — the list inside the tuple is mutable
print(t)                 # (1, 2, [3, 4, 5])

hash(t)                  # TypeError: unhashable type: 'list'
```

The tuple slot still points to the same list object. But the list has changed, so the tuple's *value* has. That's why `hash(t)` blows up — Python refuses to hash a tuple whose contents can change underneath it.

```narration
Ab dekho yeh practically kaise kaam karta hai. Integer ke liye plus-equals ek naya object banata hai aur rebind karta hai. List ke liye plus-equals in-place mutation karta hai. Yeh farq function parameters ke saath bahut important ho jaata hai — agar function plus-equals use kare list par, caller ka list change ho jaata hai. Java mein same behavior hai objects ke liye. Tuple trap bhi yaad rakhna — tuple immutable hai matlab tuple ke slots fixed hain, lekin andar jo mutable object hai woh change ho sakta hai, aur tab hash kaam nahi karta.
```

---

## The Rule

> **Immutability is a property of the type, not the name. A tuple is immutable, but it can hold mutable objects. A list is mutable forever, no matter how many times you rebind the name pointing to it.**

> **Corollary:** Mutable objects cannot be hashed. If something can change while it sits in a dict, the dict can't find it again. Use tuples, frozensets, or frozen dataclasses for keys.

```narration
Rule yaad kar lo — immutability type ki property hai, name ki nahi. Mutable objects ko hash nahi kar sakte, isliye dict key ya set element nahi ban sakte. Frozen dataclass ya tuple use karo keys ke liye.
```

---

## Production Story

### The bug that leaked beta-feature access to every user

A team runs a B2B SaaS. Each incoming request builds a per-user config from a global default:

```python
DEFAULT_CONFIG = {
    "timeout_seconds": 30,
    "max_retries": 3,
    "feature_flags": {
        "beta_dashboard": False,
        "new_search":     False,
    },
}

def build_user_config(user):
    cfg = DEFAULT_CONFIG.copy()           # ← the bug lives here
    if user.org.tier == "enterprise":
        cfg["timeout_seconds"] = 60
    if user.in_beta_program:
        cfg["feature_flags"]["beta_dashboard"] = True   # mutates SHARED inner dict
    return cfg
```

For 11 months no beta users existed, so the inner dict was never mutated. The day the first beta user logged in, every subsequent request got `beta_dashboard: True`.

**Root cause.** `dict.copy()` is **shallow**. It creates a new outer dict, but `cfg["feature_flags"]` is the same object as `DEFAULT_CONFIG["feature_flags"]`. Mutating `cfg["feature_flags"]` mutates the global.

```
DEFAULT_CONFIG ──► outer dict ──► feature_flags ──► {beta_dashboard: True}  ← ALL cfgs see this
cfg (any req.) ──► new dict ────► same feature_flags ──────────────────────/
```

**The fix:**

```python
from copy import deepcopy

def build_user_config(user):
    cfg = deepcopy(DEFAULT_CONFIG)    # completely independent copy
    ...
```

**A subtler fix** — make `DEFAULT_CONFIG` actually read-only with `MappingProxyType`:

```python
from types import MappingProxyType

DEFAULT_FLAGS = MappingProxyType({"beta_dashboard": False, "new_search": False})
DEFAULT_CONFIG = MappingProxyType({
    "timeout_seconds": 30,
    "max_retries": 3,
    "feature_flags": DEFAULT_FLAGS,
})
# Now any mutation attempt raises TypeError immediately
```

**Why this bug survived 11 months:** unit tests fresh-create `DEFAULT_CONFIG` each run and never catch it. The only reliable fix is making the default genuinely immutable.

```narration
Ab ek real production bug dekho. Ek SaaS product mein request-per-user config banta tha global default se shallow copy karke. Jab pehla beta user aaya, uske feature flag mutation ne global dict ko corrupt kar diya — aur saare users ko beta dashboard dikhne laga. 11 mahine tak koi pata nahi chala kyunki koi beta user tha hi nahi. Shallow copy bahut common trap hai. Fix hai deepcopy ya MappingProxyType se actually read-only banana.
```

---

## Going Deeper

### Hashability and the immutability contract

The Python data model requires: **if `a == b`, then `hash(a) == hash(b)`, for the lifetime of both objects.** If you mutate an object after putting it in a dict or set, you break this contract.

```python
hash([1, 2])              # TypeError: unhashable type: 'list'
hash({1, 2})              # TypeError: unhashable type: 'set'
hash((1, 2))              # OK
hash(frozenset({1, 2}))   # OK
```

Custom classes are hashable by default (using `id()`), but if you define `__eq__` you must also define `__hash__` — or Python sets `__hash__ = None` for you (making the class unhashable).

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class CacheKey:
    user_id: int
    tenant: str

k1 = CacheKey(1, "acme")
k2 = CacheKey(1, "acme")
print(k1 == k2)              # True
print(hash(k1) == hash(k2))  # True
k1.user_id = 99              # FrozenInstanceError
```

### `frozen=True` is shallow too

A `frozen=True` dataclass freezes the *fields*, not the objects those fields point to:

```python
@dataclass(frozen=True)
class Trap:
    items: list

t = Trap(items=[1, 2, 3])
t.items = []              # FrozenInstanceError — good
t.items.append(4)         # works — list inside is still mutable
hash(t)                   # TypeError: unhashable type: 'list'
```

Fix: use `tuple` or `frozenset` for fields you want truly immutable.

### `list.sort()` vs `sorted(list)`

A classic in-place-vs-rebind pair:

```python
nums = [3, 1, 2]
result = nums.sort()      # result is None; nums is now [1, 2, 3]

nums = [3, 1, 2]
result = sorted(nums)     # result is [1, 2, 3]; nums unchanged
```

Python's convention: in-place methods return `None` to make the mutation explicit. If you write `x = some_list.sort()`, `x` will be `None`.

### Strings are immutable for security as much as for correctness

Every API key, header name, file path, SQL identifier — all strings. Because strings are immutable, you can put them in dicts and trust them not to change underneath your authentication check. Immutability isn't just a perf optimization; it's part of Python's safety model.

```narration
Thoda aur deep — hashability contract samjho. Agar object mutable hai toh dict ya set mein use nahi kar sakte as key. Frozen dataclass is problem ko solve karta hai lekin dhyan raho — frozen sirf fields ko lock karta hai, andar ke mutable objects ko nahi. list.sort in-place karta hai aur None return karta hai, sorted() naya list return karta hai — ek common beginner trap hai. Strings immutable hain security ke liye bhi — auth checks mein use hone wali strings ko koi change nahi kar sakta.
```

---

## Connecting the Dots

- **Lesson 3 — Memory Management**: reference counting works because rebinding is observable. Every rebind decrements the old object's refcount and increments the new one's. Mutation doesn't touch refcounts.
- **Module 2 — Closures**: closures capture *names* bound to objects, not values. A closure over a mutable object will "see" later mutations.
- **Module 14 — Caching**: every cache key must be hashable, which means immutable. `tuple`, `frozenset`, `frozen=True` dataclasses are how production systems build cache keys.

---

## Practice

### Exercise 1 — Trace the output

```python
def grow(seq):
    seq += [4]
    print("inside grow:", seq, id(seq))

def replace(seq):
    seq = seq + [4]
    print("inside replace:", seq, id(seq))

a = [1, 2, 3]
print("before:", a, id(a))
grow(a)
print("after grow:", a, id(a))
replace(a)
print("after replace:", a, id(a))
```

<details>
<summary>Answer</summary>

```
before:          [1, 2, 3]       id_X
inside grow:     [1, 2, 3, 4]    id_X  ← same id as caller's a
after grow:      [1, 2, 3, 4]    id_X  ← caller sees the mutation
inside replace:  [1, 2, 3, 4, 4] id_Y  ← new object
after replace:   [1, 2, 3, 4]    id_X  ← caller's list untouched
```

`grow` uses `+=` → calls `list.__iadd__` → in-place mutation → caller sees it.
`replace` uses `= +` → calls `list.__add__` → new list → local rebind → caller untouched.

</details>

### Exercise 2 — Fix the bug

This function should return a fresh per-request settings dict. Find and fix both bugs.

```python
APP_DEFAULTS = {
    "timeout": 30,
    "headers": {"X-App": "core", "X-Trace": None},
}

def settings_for(trace_id, extras={}):
    s = APP_DEFAULTS.copy()
    s["headers"]["X-Trace"] = trace_id
    s.update(extras)
    extras["consumed"] = True
    return s

s1 = settings_for("trace-1")
s2 = settings_for("trace-2")
print(s1["headers"]["X-Trace"])   # expected "trace-1" — what do you actually get?
```

<details>
<summary>Solution</summary>

**Bug 1 — shallow copy.** `s["headers"]` is still `APP_DEFAULTS["headers"]`. Setting `X-Trace` mutates the global. After `s2 = settings_for("trace-2")`, `s1["headers"]["X-Trace"]` is `"trace-2"`.

**Bug 2 — mutable default argument.** `extras={}` is created once. `extras["consumed"] = True` accumulates across calls.

```python
from copy import deepcopy

def settings_for(trace_id, extras=None):
    if extras is None:
        extras = {}
    s = deepcopy(APP_DEFAULTS)
    s["headers"]["X-Trace"] = trace_id
    s.update(extras)
    extras["consumed"] = True
    return s
```

</details>

---

## Study Notes

**Q: Is Java pass-by-value or pass-by-reference?**
Java is strictly pass-by-value — but what gets passed for objects is the *value of the reference* (i.e., the pointer). So for primitive types (`int`, `double`), the function receives a copy of the value and cannot affect the caller's variable. For object types, the function receives a copy of the reference — it can mutate the object (caller sees it), but it cannot make the caller's variable point to a different object. Python works exactly the same way for objects. The confusion arises because people conflate "the function can mutate the object" with "pass-by-reference" — they're not the same thing. True pass-by-reference (like C++) means the function can even reassign the caller's variable.

**Q: When should I use `dict.copy()` vs `copy.deepcopy()`?**
Use `dict.copy()` (shallow copy) only when you're sure none of the values are mutable objects you intend to modify independently. Use `deepcopy` when the dict contains nested mutable structures (other dicts, lists) that callers might modify. The production rule: if a config/defaults dict is shared across requests, always deepcopy it, or better — make it read-only with `MappingProxyType`.

**Q: Why does `list.sort()` return `None` instead of the sorted list?**
Python's design principle: methods that mutate in place return `None` to make the mutation visible and prevent chaining that looks like it creates a new object but doesn't. If `sort()` returned `self`, you could write `sorted_data = data.sort()` and be surprised that `sorted_data` is the same object as `data`. `None` is the signal: "this mutated, don't treat the return value as a new thing."

**Q: What's the practical difference between `frozen=True` dataclass and a regular dataclass?**
`frozen=True` makes the dataclass fields immutable (raises `FrozenInstanceError` on assignment) and auto-generates `__hash__`. This makes it usable as a dict key or set element. But "frozen" only locks the field bindings — if a field holds a mutable object (like a list), that object is still mutable. For true hashability, all fields must themselves be hashable (so use `tuple`, `int`, `str`, not `list` or `dict`).

