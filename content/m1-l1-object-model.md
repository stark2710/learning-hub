---
title: "Names, Objects & Memory"
module: "Python Object Model"
domain: "Python Mastery"
lesson_id: "m1-l1-object-model"
prev: ""
next: "m1-l2-mutability"
duration: "~25 min"
---

```system_prompt
You are a Python expert teaching an experienced Java/backend developer.
Always respond in plain English. Be concise and precise.
Relate Python concepts to Java equivalents when helpful.
When explaining memory, use the "name tag vs box" mental model.
Never use Hinglish or Hindi — only English.
```

## What You'll Learn

- Why Python variables are fundamentally different from Java variables
- What actually happens in memory when you write `x = 5`
- Why `is` and `==` are not the same thing and when each one lies to you
- What integer interning is and why it causes mysterious bugs in production

```narration
Is lesson mein hum Python ka object model samjhenge — yani ki jab tum likhte ho x equals 5, Python memory mein kya karta hai exactly. Java se compare karein toh bahut bada difference hai. Chalte hain.
```

---

## The Mental Model

In Java, a variable is a **box**. You declare `int x = 5` and Java creates a box labelled `x` that holds the value `5` directly inside it.

Python works completely differently. In Python, a variable is a **name tag** — a sticky label you attach to an object. The object lives somewhere in memory, and your variable is just a reference pointing to it.

```
Java:
  x [ 5 ]          ← the box holds the value

Python:
  x ──→ [ 5 ]      ← the name points to an object
```

This single difference explains almost every "weird" Python behaviour you'll encounter.

When you write:
```python
x = 5
```

Python does three things:
1. Creates an integer object with value `5` somewhere in memory
2. Creates a name `x` in the current **namespace** (the current scope's `__dict__`)
3. Binds the name `x` to point at that object

The object has a **reference count** — how many names are pointing at it. When the count hits zero, the garbage collector reclaims the memory.

### Assignment is always rebinding, never mutation

```python
x = 5
x = 10
```

`x` didn't change from 5 to 10. The object `5` still exists (until nothing points to it). You just moved the label `x` from one object to another.

```
Before x = 10:     After x = 10:
  x ──→ [5]          [5]   (refcount → 0, will be collected)
                     x ──→ [10]
```

```narration
Toh suno — Python mein variable ek box nahi hai jaise Java mein hota hai. Yahan variable ek name tag hai jo kisi object ko point karta hai. Jab tum likhte ho x equals 5, Python ek integer object banata hai memory mein, phir x ko us object se bind kar deta hai. Names stored hote hain namespace mein — basically ek dictionary — aur objects memory heap pe hote hain. Jab tum x equals 10 likhte ho, x ka label ek naye object pe move ho jata hai, purana object wahi rehta hai jab tak koi aur point kar raha ho.
```

---

## How It Actually Works

```python
a = [1, 2, 3]   # create a list object, bind name 'a' to it
b = a            # bind name 'b' to the SAME object — not a copy
b.append(4)      # mutate the object through name 'b'
print(a)         # [1, 2, 3, 4] — 'a' sees the change too
```

Both `a` and `b` point at the same list object in memory. Mutating through `b` is mutating the object itself — `a` still points there, so it sees the change.

```
a ──→ [1, 2, 3]
b ──/
```

After `b = a`, both names share one arrow to one object.

### id() — the memory address oracle

`id(obj)` returns the memory address of an object (in CPython). It is similar to a pointer value in C — it uniquely identifies the object in memory for its lifetime. Two names pointing to the same object will have the same `id`.

```python
a = [1, 2, 3]
b = a
print(id(a) == id(b))   # True — same object
print(a is b)           # True — 'is' checks identity (same id)
print(a == b)           # True — '==' checks equality (same value)

c = [1, 2, 3]           # a NEW list object with same contents
print(a is c)           # False — different objects
print(a == c)           # True — same value
```

> **Rule:** `is` checks identity (same memory address). `==` checks equality (same value). Never use `is` to compare values — use it only for `x is None` or `x is True`.

```narration
Ab dekho kya hota hai jab tum b equals a likhte ho list ke saath. Koi copy nahi banta — dono names ek hi object ko point karte hain. Toh jab b se append karte ho, a ko bhi dikhai deta hai, kyunki dono ek hi list par point kar rahe hain. id() function se tum object ka memory address dekh sakte ho — exactly jaise C mein pointer hota hai. is operator identity check karta hai same address ke liye, double equals value check karta hai.
```

---

## The Rule

> **A Python variable is a name bound to an object, not a container holding a value. Assignment always rebinds the name. It never copies the object.**

```narration
Yeh rule yaad kar lo — Python mein assignment matlab rebinding, copying nahi. Yeh ek line samjh aaye toh bahut saari "weird" Python behaviours automatically samajh aa jaayengi.
```

---

## Production Story

**The Bug: Mutable Default Argument**

A developer writes a helper to collect items:

```python
def add_item(item, collection=[]):   # BUG: default is evaluated once
    collection.append(item)
    return collection

print(add_item("apple"))    # ['apple']
print(add_item("banana"))   # ['apple', 'banana']  ← unexpected!
print(add_item("cherry"))   # ['apple', 'banana', 'cherry']  ← bug
```

**Why it happens:** Default argument values are evaluated **once** when the function is defined, not on each call. The list `[]` is created once and the same object is reused across all calls. Each call mutates the same list.

**The fix:**

```python
def add_item(item, collection=None):
    if collection is None:
        collection = []          # fresh list on every call
    collection.append(item)
    return collection
```

This is one of the most common Python bugs in production codebases. It happens in Django model methods, Flask route handlers, data pipeline functions — anywhere a dev reaches for a default mutable argument as a convenience.

> **Warning:** `pylint` and `ruff` both warn on mutable default arguments. This also appears in virtually every Python interview.

```narration
Ab ek real production bug dekho. Tumne function banaya collection equals empty list as default. Pehli baar sab theek lagta hai, lekin dusri call mein surprise — list already bhari hui hai! Kyunki default argument ek baar evaluate hota hai jab function define hota hai, har call pe nahi. Toh har call usi ek list object ko mutate kar rahi hai. Fix simple hai — None use karo sentinel ke roop mein aur andar fresh list banao. Yeh Python interviews mein bahut commonly poocha jaata hai.
```

---

## Going Deeper

### Integer Interning

CPython pre-creates integer objects for small integers (typically -5 to 256) and reuses them. This is an implementation detail, not a language guarantee.

```python
a = 256
b = 256
print(a is b)   # True — CPython reuses the same object

a = 257
b = 257
print(a is b)   # False — new object created each time
```

**Why this bites you in production:** Code that uses `is` to compare integers works fine in testing (small values) and silently breaks with large values.

### String Interning

Python interns string literals that look like identifiers (no spaces, alphanumeric). Other strings may or may not be interned depending on CPython internals.

```python
a = "hello"
b = "hello"
print(a is b)        # True — interned

a = "hello world"
b = "hello world"
print(a is b)        # False in most cases — not interned
```

Same rule: use `==` for string comparison, always.

### Pass by Object Reference

Python is neither pass-by-value (like C primitives) nor pass-by-reference (like C++ references). It is **pass-by-object-reference** — the function receives a reference to the same object.

```python
def mutate(lst):
    lst.append(99)      # mutates the object — caller sees this

def rebind(lst):
    lst = [1, 2, 3]    # rebinds the local name — caller does NOT see this

data = [10, 20]
mutate(data)
print(data)   # [10, 20, 99]  ← mutation visible

rebind(data)
print(data)   # [10, 20, 99]  ← rebinding not visible
```

In Java, object references work the same way — you can mutate the object through the reference, but you cannot make the caller's variable point to a new object.

### The `__slots__` Optimisation

By default, Python objects store their attributes in a `__dict__` — a hash map. This is flexible but wastes memory. `__slots__` tells Python to use a fixed layout instead:

```python
class Point:
    __slots__ = ['x', 'y']   # no __dict__, fixed memory layout
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

For objects you create millions of, this can halve memory usage.

```narration
Thoda aur deep chalte hain. CPython ek optimization karta hai small integers ke liye — minus 5 se 256 tak ke integers pre-create hote hain aur reuse hote hain. Toh 256 ke liye is True aayega, lekin 257 ke liye False. Isi liye kabhi bhi integers compare karne ke liye is mat use karo. Pass by object reference concept bhi samjho — function ko same object ka reference milta hai, toh mutation visible hoti hai, lekin rebinding nahi. Yeh Java ke object references jaisa hi hai.
```

---

## Connecting the Dots

This lesson is the foundation for everything in Module 1. In **Lesson 2 (Mutability)**, you'll see why the name-vs-object model means mutable objects like lists and dicts behave very differently from immutable ones like strings and tuples — and why this matters every time you pass arguments to a function.

In **Lesson 3 (Memory Management)**, you'll see how Python's reference counting uses exactly this model to decide when to free memory.

```narration
Yeh lesson poora module ka foundation hai. Agle lesson mein mutability dekhenge — mutable aur immutable objects ka difference aur yeh function arguments mein kyun matter karta hai. Aur lesson 3 mein dekhenge ki reference counting is model ka use karke memory kaise free karta hai.
```

---

## Practice

### Exercise 1 — Trace the Output

What does this print? Trace through it before running.

```python
x = [1, 2, 3]
y = x
y += [4]
print(x)
print(y)
print(x is y)
```

<details>
<summary>Answer</summary>

```
[1, 2, 3, 4]
[1, 2, 3, 4]
True
```

`y = x` binds both names to the same list. `y += [4]` calls `y.__iadd__([4])` which mutates the list **in place** (unlike `y = y + [4]` which would create a new list). So `x` and `y` still point to the same object.

Compare with: `y = y + [4]` — creates a new list, rebinds `y`, and `x` would still be `[1, 2, 3]`.

</details>

### Exercise 2 — Fix the Bug

This function is broken. Why? Fix it.

```python
def make_user(name, tags=[]):
    tags.append("new_user")
    return {"name": name, "tags": tags}

u1 = make_user("Alice")
u2 = make_user("Bob")
print(u2["tags"])   # should be ['new_user'] but isn't
```

<details>
<summary>Solution</summary>

```python
def make_user(name, tags=None):
    if tags is None:
        tags = []
    tags.append("new_user")
    return {"name": name, "tags": tags}
```

The default list `[]` is created once when the function is defined. Every call that doesn't pass `tags` shares the same list object. Using `None` as sentinel and creating a fresh `[]` inside the function fixes it.

</details>

---

## Study Notes

**Q: Where are variable names like `x` and `y` actually stored in memory?**
Names are stored in the namespace of the current scope — which is a Python dictionary (`__dict__`). For module-level code, that's `globals()`. For function-local code, it's `locals()` (optimised to a C array internally). The objects they point to live on the heap.

**Q: Is `id()` the same as a pointer value in C?**
Essentially yes, in CPython. `id(obj)` returns the memory address of the object. The difference: C pointers are first-class values you can do arithmetic on; Python's `id()` is just an oracle you query. Also, once the object is garbage-collected, a new object can reuse that address, so two calls to `id()` on different-lifetime objects can coincidentally return the same number.

**Q: What is a mutable default argument and why is it a bug?**
A mutable default argument is any mutable object (list, dict, set) used as a default parameter value. The bug: default values are evaluated once at function definition time, not per call. So `def f(x=[])` creates exactly one list object. Every call that doesn't pass `x` mutates that same shared list. The fix: use `None` as default and create a fresh mutable inside the function body.

**Q: What's the difference between pass-by-reference (C++) and pass-by-object-reference (Python)?**
In C++ pass-by-reference, the function receives an alias to the caller's variable — it can reassign the caller's variable to point to something else. In Python, the function receives a copy of the reference (the name tag), not an alias to the caller's name. So you can mutate the object the reference points to (and the caller sees it), but you cannot make the caller's variable point to a new object — local rebinding stays local.

**Q: What does `defaults={}` vs `defaults=None` mean as a function parameter?**
`defaults={}` has the mutable default argument bug — all callers share one dict object. `defaults=None` is the safe pattern: the function checks `if defaults is None: defaults = {}` and creates a fresh dict per call. Always use `None` (or another immutable sentinel) as default when the parameter is mutable.

