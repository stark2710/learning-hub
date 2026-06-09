---
title: "REST API Design Principles"
module: "Backend Engineering"
domain: "Python Mastery"
lesson_id: "m4-l1-rest-api"
prev: "m3-l4-asyncio"
next: "m4-l2-db-indexing"
duration: "~50 min"
---

```system_prompt
You are a senior backend engineer and API architect with 15+ years of experience designing REST APIs at scale — systems handling millions of requests per day across fintech, SaaS, and platform engineering teams. The student has 4+ years of backend development (3 years Java with Spring MVC/JAX-RS, 1+ year Python), understands HTTP at a surface level, and has just completed deep dives into Python internals and concurrency models.

For this lesson on REST API Design Principles:
- Connect to their Java background (Spring @GetMapping, JAX-RS @Path, ResponseEntity) where it deepens understanding
- Emphasize design decisions over syntax — *why* something is right, not just *what* is right
- Be honest about real-world tradeoffs: versioning debates, when to break REST rules, GraphQL vs REST
- Relate idempotency and HTTP semantics to real production failure scenarios
- When asked about FastAPI or Django REST Framework, ground the answer in REST principles first, then show the framework expression

Always respond in plain English.
```

## What You'll Learn

- What REST actually means beyond "it uses HTTP" — the 6 architectural constraints Fielding defined
- How to design resource-centric URLs and why CRUD-named endpoints are an anti-pattern
- The precise semantics of HTTP methods: idempotency, safety, and how they shape retry logic
- Status codes that communicate intent to callers — and the costly misuses you'll see in every legacy codebase

```narration
Yaar, ab hum backend engineering ke sabse important topic pe aa gaye hain — REST API design. Python aur concurrency toh bahut achha seekha tumne, but ab hum real-world backend engineering mein jaayenge. REST sirf "HTTP pe kaam karta hai" nahi hai — iske andar ek poori philosophy hai. Aaj hum woh philosophy samjhenge, taaki tum APIs design karo jo 5 saal baad bhi maintainable rahen.
```

---

## The Mental Model

### REST Is an Architectural Style, Not a Protocol

In 2000, Roy Fielding published his PhD dissertation. Chapter 5 described **Representational State Transfer** — a set of constraints that, if followed, produce web systems with specific desirable properties: scalability, visibility, reliability, and evolvability.

REST is not a specification. There is no RFC. There is no "REST protocol." REST is a **set of 6 constraints** — and whether your API is "RESTful" is a matter of how many you follow.

```
┌─────────────────────────────────────────────────────────────────┐
│                   THE 6 REST CONSTRAINTS                        │
├────────────────────────┬────────────────────────────────────────┤
│ 1. Client-Server       │ UI concerns ≠ data storage concerns.   │
│                        │ They evolve independently.             │
├────────────────────────┼────────────────────────────────────────┤
│ 2. Stateless           │ Each request contains ALL context.     │
│                        │ Server stores no client session state. │
├────────────────────────┼────────────────────────────────────────┤
│ 3. Cacheable           │ Responses must declare cacheability.   │
│                        │ Enables HTTP caching infrastructure.   │
├────────────────────────┼────────────────────────────────────────┤
│ 4. Uniform Interface   │ Resources, representations, self-      │
│                        │ descriptive messages, HATEOAS.         │
├────────────────────────┼────────────────────────────────────────┤
│ 5. Layered System      │ Client doesn't know if it's talking    │
│                        │ to origin server or a CDN proxy.       │
├────────────────────────┼────────────────────────────────────────┤
│ 6. Code on Demand      │ (Optional) Server can send executable  │
│    (optional)          │ code to client (e.g., JavaScript).     │
└────────────────────────┴────────────────────────────────────────┘
```

The one most APIs violate? **Stateless.** The moment you store "current user's wizard step" in a server-side session, you've broken REST. Auth tokens (JWT, OAuth) are the correct solution — they push state back to the client.

### The Richardson Maturity Model

Leonard Richardson gave us a practical way to measure how "REST-like" an API is:

```
Level 0 ─── One endpoint, POST everything
             POST /api  {"action": "getUser", "id": 42}

Level 1 ─── Resources exist as URLs
             POST /users/42  {"action": "get"}

Level 2 ─── HTTP Verbs used correctly  ← Most "REST APIs" live here
             GET /users/42
             DELETE /users/42

Level 3 ─── HATEOAS: responses include links to next actions
             GET /users/42
             → {"id": 42, "_links": {"orders": "/users/42/orders"}}
```

Most production APIs target **Level 2**. Level 3 (HATEOAS) is theoretically pure but operationally complex — you'll rarely see it in practice outside of hypertext-heavy systems.

```narration
Dekho, Richardson Maturity Model bahut helpful hai mentally. Jab tumhara team debate kare ki "kya yeh REST hai?", toh yeh model use karo. Level 2 pe rehna practical hai — Level 3 ki philosophy samjho but har jagah implement karna jaruri nahi. Most companies Level 2 pe hi comfortable hain aur woh sahi bhi hai.
```

---

## How It Actually Works

### Resource Naming: Think Nouns, Not Verbs

The single most common REST mistake is verb-based URLs. Resources are **nouns**. HTTP methods are your **verbs**.

```
❌ ANTI-PATTERN — Verb-based URLs
GET  /getUser?id=42
POST /createOrder
POST /deleteProduct/5
POST /updateUserEmail
GET  /fetchAllActiveOrders

✅ REST-CORRECT — Resource-based URLs
GET    /users/42
POST   /orders
DELETE /products/5
PATCH  /users/42
GET    /orders?status=active
```

**Hierarchy in URLs** reflects containment relationships:

```
/users                        → collection of all users
/users/42                     → specific user
/users/42/orders              → orders belonging to user 42
/users/42/orders/789          → specific order for user 42
/users/42/orders/789/items    → line items of that order
```

> **Rule:** If your URL contains a verb like `/getUser`, `/createOrder`, `/deleteProduct`, your URL is a **Remote Procedure Call (RPC)**, not a REST resource. RPC is valid (gRPC, SOAP), but don't call it REST.

```python
# FastAPI example — resource-centric routing
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class UserUpdate(BaseModel):
    email: str | None = None
    name: str | None = None

# Collection resource
@app.get("/users")                          # List all users
async def list_users(active: bool = True):
    ...

@app.post("/users", status_code=201)        # Create a user
async def create_user(user: UserCreate):
    ...

# Item resource
@app.get("/users/{user_id}")               # Get one user
async def get_user(user_id: int):
    ...

@app.patch("/users/{user_id}")             # Partial update
async def update_user(user_id: int, updates: UserUpdate):
    ...

@app.delete("/users/{user_id}", status_code=204)  # Delete
async def delete_user(user_id: int):
    ...
```

### HTTP Methods — The Semantics That Matter

Every method has a precise contract. Violating it breaks **caching, proxies, retry logic, and client assumptions**.

```
┌──────────┬──────────┬─────────────┬─────────────────────────────┐
│ Method   │ Safe?    │ Idempotent? │ Typical Use                 │
├──────────┼──────────┼─────────────┼─────────────────────────────┤
│ GET      │ YES      │ YES         │ Read a resource              │
│ HEAD     │ YES      │ YES         │ Read headers only            │
│ OPTIONS  │ YES      │ YES         │ Discover allowed methods     │
├──────────┼──────────┼─────────────┼─────────────────────────────┤
│ PUT      │ NO       │ YES         │ Full replacement of resource │
│ DELETE   │ NO       │ YES         │ Remove resource              │
├──────────┼──────────┼─────────────┼─────────────────────────────┤
│ POST     │ NO       │ NO          │ Create / trigger action      │
│ PATCH    │ NO       │ NO*         │ Partial update               │
└──────────┴──────────┴─────────────┴─────────────────────────────┘

Safe      = Has no side effects. Browser can pre-fetch. Crawlers can call.
Idempotent = Calling N times = calling once. Network retry is safe.
* PATCH CAN be designed idempotently but isn't by default.
```

**Why idempotency matters in production:**

When a network call fails, clients must decide: retry or not? If the method is idempotent, retrying is safe. If not, you might create duplicate records.

```python
import httpx
import time

# Safe to retry — PUT is idempotent
def update_user_email_safe(user_id: int, email: str) -> dict:
    for attempt in range(3):
        try:
            # PUT replaces the full resource — calling twice is same as once
            response = httpx.put(
                f"/users/{user_id}",
                json={"email": email, "name": "Bharat"}  # full representation
            )
            response.raise_for_status()
            return response.json()
        except httpx.NetworkError:
            time.sleep(2 ** attempt)  # exponential backoff — safe because PUT is idempotent
    raise RuntimeError("Failed after 3 attempts")


# DANGEROUS to retry blindly — POST is NOT idempotent
def create_order_dangerous(user_id: int, items: list) -> dict:
    for attempt in range(3):
        try:
            response = httpx.post(
                f"/users/{user_id}/orders",
                json={"items": items}
            )
            response.raise_for_status()
            return response.json()
        except httpx.NetworkError:
            time.sleep(2 ** attempt)
            # ⚠️ If server received the first request but response was lost,
            # retrying creates a DUPLICATE ORDER.

# Correct pattern for non-idempotent POST: Idempotency Key
def create_order_safe(user_id: int, items: list, idempotency_key: str) -> dict:
    response = httpx.post(
        f"/users/{user_id}/orders",
        json={"items": items},
        headers={"Idempotency-Key": idempotency_key}  # Stripe uses this pattern
    )
    # Server caches response keyed on idempotency_key
    # Duplicate calls return cached response, not a new order
    return response.json()
```

```narration
Idempotency yaar, yeh interview mein aur production dono mein bahut important hai. Socho — tumhara payment API call kiya, network timeout ho gaya, retry kiya — aur customer ke do payments charge ho gaye! Stripe, Razorpay — sab Idempotency-Key header use karte hain exactly is problem ke liye. GET aur PUT retry karo freely, POST mein sochke karo.
```

### PUT vs PATCH — The Difference That Bites

```python
# Scenario: User has {id: 42, name: "Bharat", email: "b@b.com", role: "admin"}

# PUT — FULL replacement. Missing fields are NULLED or REMOVED.
PUT /users/42
{"name": "Bharat Malviya"}
# Result: {id: 42, name: "Bharat Malviya", email: null, role: null}
# ⚠️ You just wiped the email and role!

# PATCH — Partial update. Only send what changes.
PATCH /users/42
{"name": "Bharat Malviya"}
# Result: {id: 42, name: "Bharat Malviya", email: "b@b.com", role: "admin"}
# ✅ Only name was changed.
```

This is where Java developers often get confused coming from Spring — `@PutMapping` sounds right for "update," but semantically it means **replace everything**. For partial updates, always use PATCH.

### HTTP Status Codes — Communicate Intent, Not Just Success/Failure

The most common mistake in REST APIs: returning `200 OK` for everything and hiding errors in the response body.

```python
# ❌ ANTI-PATTERN — JSON error disguised as HTTP 200
@app.get("/users/{user_id}")
async def get_user_bad(user_id: int):
    user = db.find(user_id)
    if not user:
        return {"success": False, "error": "User not found"}  # Still HTTP 200!
    return {"success": True, "data": user}
# Problem: Client must parse body to know if it succeeded.
# Proxies/caches treat it as a successful response.
# Monitoring sees 0 errors even when everything is broken.


# ✅ CORRECT — Use HTTP semantics
from fastapi import HTTPException, status

@app.get("/users/{user_id}")
async def get_user_correct(user_id: int):
    user = db.find(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return user  # HTTP 200 implicitly
```

**The status codes you must know cold:**

```
2xx — SUCCESS
200 OK            → GET, PUT, PATCH succeeded with a body
201 Created       → POST created a resource (include Location header!)
204 No Content    → DELETE succeeded, nothing to return

3xx — REDIRECTION
301 Moved Permanently → Resource URL changed forever (update your bookmarks)
304 Not Modified      → Cache is still valid (ETag/Last-Modified match)

4xx — CLIENT ERRORS (caller's fault)
400 Bad Request   → Malformed JSON, invalid field, validation failed
401 Unauthorized  → No/invalid auth token (not logged in)
403 Forbidden     → Valid token, but insufficient permissions
404 Not Found     → Resource doesn't exist
405 Method Not Allowed → GET on a POST-only endpoint
409 Conflict      → Duplicate create, optimistic lock failure
422 Unprocessable → Syntactically valid but semantically wrong (FastAPI default)
429 Too Many Requests → Rate limit exceeded

5xx — SERVER ERRORS (your fault)
500 Internal Server Error → Unhandled exception — fix immediately
502 Bad Gateway           → Upstream service returned garbage
503 Service Unavailable   → Server overloaded / in maintenance
```

> **Warning:** Never return `500` for invalid user input. `500` means your code crashed. `400/422` means the user sent bad data. Confusing these makes oncall debugging a nightmare — your dashboards will look like your server is broken when users are just sending bad requests.

```narration
Status codes yaar — inka sahi use karna ek sign hai ki developer mature hai. Jab main code review karta hoon aur dekhta hoon ki har error pe 200 return ho raha hai, toh main immediately samajh jaata hoon ki developer ne REST properly nahi seekha. 404, 401, 403 ka fark yaad rakhna — 401 matlab "tu kaun hai", 403 matlab "tu kaun hai yeh pata hai, but tu yeh nahi kar sakta."
```

### API Versioning Strategies

Every API changes. How you version determines how painful those changes are.

```
Strategy 1: URL Path Versioning  ← Most common, easiest to understand
/v1/users/42
/v2/users/42

Strategy 2: Query Parameter
/users/42?version=2

Strategy 3: Header Versioning  ← Clean URLs, harder to test in browser
GET /users/42
Accept: application/vnd.myapp.v2+json

Strategy 4: Subdomain
v1.api.myapp.com/users/42
v2.api.myapp.com/users/42
```

**Industry reality:** URL path versioning (`/v1/`, `/v2/`) wins on developer experience. Always start with `/v1/`. When you make a breaking change (remove a field, change a response structure), bump to `/v2/`.

Non-breaking changes (adding optional fields, new endpoints) don't require version bumps.

```python
from fastapi import FastAPI, APIRouter

app = FastAPI()

# Version 1 router
v1 = APIRouter(prefix="/v1")

@v1.get("/users/{user_id}")
async def get_user_v1(user_id: int):
    return {"id": user_id, "name": "Bharat"}  # v1 response shape

# Version 2 router — adds profile_picture, removes legacy field
v2 = APIRouter(prefix="/v2")

@v2.get("/users/{user_id}")
async def get_user_v2(user_id: int):
    return {
        "id": user_id,
        "name": "Bharat",
        "profile_picture": "https://cdn.example.com/bharat.jpg"
    }

app.include_router(v1)
app.include_router(v2)
```

---

## The Rule

> **Rule:** URLs identify **resources** (nouns). HTTP methods express **actions** (verbs). Status codes communicate **outcome semantics**. If you put verbs in your URL, actions in your response body, or outcomes in `200 OK`, you're not building REST — you're building RPC over HTTP.

> **Rule:** Make everything that CAN be idempotent, idempotent. For operations that can't be (POST creates), give callers an Idempotency-Key mechanism. Retries are a fact of distributed systems life — design for them.

---

## Production Story

### The Billing Disaster That Cost ₹2 Lakhs

A fintech startup's payment service had this endpoint:

```python
# The buggy endpoint — simplified
@app.post("/process-payment")
async def process_payment(amount: float, user_id: int):
    # Charge the user
    charge = stripe.charge(amount, user_id)
    if charge.status == "success":
        db.record_payment(user_id, amount)
        return {"status": "success", "charge_id": charge.id}
    else:
        return {"status": "failed", "error": charge.error}
        # ⚠️ Still returns HTTP 200!
```

The mobile client had a network retry wrapper:

```python
# Mobile client retry logic
def call_with_retry(url, payload, max_retries=3):
    for i in range(max_retries):
        response = requests.post(url, json=payload)
        if response.status_code == 200:  # ← Checks HTTP status only
            data = response.json()
            return data
        time.sleep(1)
    raise Exception("Payment failed")
```

**What happened:** User clicked "Pay ₹5000". Request reached server, Stripe charged the card, DB write succeeded, but the TCP response packet was lost. Client saw no `200`, retried. Server charged again. User got double-charged ₹10,000.

**The fix — two parts:**

```python
# Fix Part 1: Return proper HTTP error codes
@app.post("/payments", status_code=status.HTTP_201_CREATED)
async def process_payment(
    amount: float,
    user_id: int,
    idempotency_key: str = Header(...)  # Required header
):
    # Check if we already processed this request
    existing = cache.get(f"idem:{idempotency_key}")
    if existing:
        return JSONResponse(status_code=200, content=existing)  # Return cached result

    try:
        charge = stripe.charge(amount, user_id)
    except stripe.CardError as e:
        raise HTTPException(status_code=402, detail=str(e))  # 402 Payment Required
    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail="Payment processor error")

    result = {
        "charge_id": charge.id,
        "amount": amount,
        "status": "succeeded"
    }

    # Cache for 24 hours under idempotency key
    cache.set(f"idem:{idempotency_key}", result, ex=86400)

    return result


# Fix Part 2: Client respects HTTP semantics
def call_payment(url, payload, idempotency_key):
    headers = {"Idempotency-Key": idempotency_key}
    for attempt in range(3):
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in (200, 201):  # Success — idempotency key handles dedup
            return response.json()
        elif response.status_code in (400, 402, 422):
            raise ValueError(f"Client error: {response.json()}")  # Don't retry 4xx
        elif response.status_code >= 500:
            time.sleep(2 ** attempt)  # Retry 5xx with backoff
            continue
    raise RuntimeError("Payment service unavailable")
```

> **Warning:** Never retry `4xx` errors — they mean the client sent bad data. Retrying won't help and could hammer your server. Only retry `5xx` or network timeouts, and always with exponential backoff.

```narration
Yeh wala production story sach mein ek common disaster hai. Maine personally ek company mein yeh dekhа hai jahan payment gateway ke sath retry loop ne duplicate charges create kar diye the. Idempotency key — Stripe ne isko famous kiya — is ek pattern hai jo har payment aur order creation API mein hona chahiye. Aur 4xx pe retry mat karo yaar, woh toh tumhara hi galti hai — retry se fix nahi hoga.
```

---

## Going Deeper

### Request and Response Design Best Practices

**Consistent error response shape** — your API consumers will thank you:

```python
# Define a standard error response model
from pydantic import BaseModel
from fastapi import Request
from fastapi.responses import JSONResponse

class ErrorResponse(BaseModel):
    error: str          # Machine-readable error code: "USER_NOT_FOUND"
    message: str        # Human-readable: "User with id 42 does not exist"
    request_id: str     # For support tickets / log correlation
    docs_url: str | None = None  # Link to API docs for this error

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.headers.get("X-Error-Code", "UNKNOWN_ERROR"),
            "message": exc.detail,
            "request_id": request.headers.get("X-Request-ID", ""),
            "docs_url": f"https://docs.myapi.com/errors#{exc.status_code}"
        }
    )
```

**Pagination — never return unbounded collections:**

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    has_next: bool

@app.get("/users", response_model=PaginatedResponse[UserOut])
async def list_users(page: int = 1, page_size: int = 20):
    if page_size > 100:
        raise HTTPException(400, "page_size cannot exceed 100")

    offset = (page - 1) * page_size
    users = db.query(User).offset(offset).limit(page_size + 1).all()

    has_next = len(users) > page_size
    return PaginatedResponse(
        items=users[:page_size],
        total=db.query(User).count(),
        page=page,
        page_size=page_size,
        has_next=has_next
    )
```

### Content Negotiation and Headers You Should Know

```
# Request headers that REST clients should set
Content-Type: application/json        # What format am I sending
Accept: application/json             # What format I want back
Authorization: Bearer <token>        # Auth
X-Request-ID: uuid4()               # Correlation ID for distributed tracing
Idempotency-Key: uuid4()            # For non-idempotent operations

# Response headers your API should set
Content-Type: application/json
X-Request-ID: <echo back the request id>
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1718012400
Location: /v1/users/42              # On 201 Created — where is the new resource?
ETag: "d41d8cd98f00b204e9800998ecf8427e"  # For caching
```

### HATEOAS — The Level 3 Ideal

```python
# Level 3 REST: responses include links to related actions
# Client doesn't need to know URL structure — follows links

# Response for GET /orders/789
{
    "id": 789,
    "status": "pending",
    "amount": 5000,
    "_links": {
        "self":    {"href": "/v1/orders/789",        "method": "GET"},
        "cancel":  {"href": "/v1/orders/789/cancel", "method": "POST"},
        "payment": {"href": "/v1/orders/789/payment","method": "POST"},
        "user":    {"href": "/v1/users/42",          "method": "GET"}
    }
}
# Client logic: "Can I cancel this?" → check if "cancel" link exists
# No hardcoded URLs in client. Server controls the workflow.
```

HATEOAS is beautiful in theory. In practice, most teams skip it because:
- Every client ignores the links and hardcodes URLs anyway
- Generates a lot of boilerplate
- Hard to keep links accurate as the API evolves

Know it for interviews. Apply it selectively.

```narration
HATEOAS — yeh Level 3 wala concept bahut clean hai theory mein. But main seedha bolunga — industry mein bahut kam log implement karte hain. GitHub REST API aur Stripe iske kuch elements use karte hain, but mostly teams Level 2 pe hi ruke hain. Interviews mein isko discuss kar sako toh impressive lagta hai, but production mein pragmatic rehna.
```

---

## Connecting the Dots

**From what you've learned:**
- **Asyncio (m3-l4):** Your FastAPI routes should be `async def` — they run on the event loop. Blocking DB calls inside async routes need `run_in_executor`. Everything from Module 3 applies here.
- **Decorators (m2-l2):** FastAPI's `@app.get()`, `@app.post()` are decorators. The routing system is built on the decorator pattern you studied.
- **Generators (m2-l3):** Streaming large API responses (Server-Sent Events, chunked responses) use Python generators under the hood.

**Where this leads:**
- **m4-l2 (DB Indexing):** REST endpoints that are slow usually have unindexed queries behind them. You'll see exactly how API response time connects to query execution plans.
- **m4-l3 (Caching):** `GET` endpoints are cacheable. You'll implement Redis-backed response caching using the `ETag` and `Cache-Control` headers introduced today.
- **m5 (System Design):** API gateway patterns, rate limiting, circuit breakers — all build directly on REST's stateless constraint.

---

## Practice

### Exercise 1: URL Design Audit

Here's a real API from a legacy codebase. Identify every REST violation and write the corrected version:

```
POST  /api/getAllUsers
POST  /api/createNewUser
POST  /api/updateUserById?id=42
GET   /api/deleteUser?id=42
POST  /api/getUserOrders?userId=42
POST  /api/markOrderComplete?orderId=789
```

<details>
<summary>Answer</summary>

```
# Violations:
# 1. POST for read operations (getAllUsers, getUserOrders)
# 2. Verbs in URLs (getAllUsers, createNewUser, updateUserById, deleteUser)
# 3. GET for a DELETE operation (deleteUser) — browsers pre-fetch GET URLs!
# 4. Query params for IDs that should be path params
# 5. "markOrderComplete" is an action verb — needs resource modeling

# Corrected:
GET    /v1/users                    # List all users (with ?page=1&page_size=20)
POST   /v1/users                    # Create user
GET    /v1/users/42                 # Get user 42
PUT    /v1/users/42                 # Full update
PATCH  /v1/users/42                 # Partial update
DELETE /v1/users/42                 # Delete user

GET    /v1/users/42/orders          # Get user 42's orders

# "markOrderComplete" → the action changes order STATUS → use PATCH
PATCH  /v1/orders/789
Body: {"status": "completed"}
# Or if it's a significant state transition, use a sub-resource:
POST   /v1/orders/789/completion    # Action noun
```

</details>

---

### Exercise 2: Idempotency Bug Hunt

This endpoint is supposed to be idempotent (PUT), but it has a bug that makes it non-idempotent. Find it and fix it:

```python
@app.put("/users/{user_id}/settings")
async def update_settings(user_id: int, settings: dict):
    existing = db.get_settings(user_id)

    # Merge new settings with existing
    merged = {**existing, **settings}

    # Append to audit log
    db.append_audit_log(user_id, f"Settings updated at {datetime.now()}")

    db.save_settings(user_id, merged)
    return {"status": "saved", "settings": merged}
```

<details>
<summary>Answer</summary>

```python
# BUG: db.append_audit_log() is called every time the endpoint is hit.
# If you call PUT /users/42/settings three times with the same body,
# you get THREE audit log entries — the side effect is not idempotent
# even if the resource state is.

# Also bug: merging ({**existing, **settings}) means you can never
# REMOVE a setting — PUT should REPLACE, not merge.
# That's PATCH behavior. PUT means: replace the entire settings object.

# Fixed:
@app.put("/users/{user_id}/settings")
async def update_settings(user_id: int, settings: dict):
    existing = db.get_settings(user_id)

    # PUT = full replacement, not merge
    # If they send {"theme": "dark"}, that's the ENTIRE new settings
    new_settings = settings  # no merge

    # Audit log should only record CHANGES, not the fact of the call
    if new_settings != existing:
        db.append_audit_log(
            user_id,
            f"Settings changed from {existing} to {new_settings}"
        )

    db.save_settings(user_id, new_settings)
    return {"status": "saved", "settings": new_settings}

# Now: calling PUT 3 times with same body = same state, 1 audit entry
# That's idempotent behavior.
```

</details>

---

## Study Notes

**Q: What's the real difference between 401 and 403?**
`401 Unauthorized` means the request has no valid authentication — the server doesn't know who you are. Your client should redirect to login. `403 Forbidden` means the server knows exactly who you are (valid token), but you don't have permission to access that resource. Don't confuse these — 401 triggers auth refresh, 403 should surface a "you don't have access" message to the user.

**Q: When should I use POST vs PUT for creating a resource?**
Use POST when the server generates the ID (`POST /users` → server creates user 42). Use PUT when the client specifies the ID (`PUT /users/42` → client is saying "user 42 should have this state"). POST is non-idempotent (creates a new resource each time). PUT is idempotent (setting user 42 to this state is safe to repeat). In practice, POST for creation is far more common since servers control ID generation.

**Q: Can I use GET with a request body for complex searches?**
Technically, HTTP/1.1 doesn't prohibit it, but most clients, proxies, and servers discard GET bodies — it's undefined behavior. The correct approach: simple filters go in query params (`GET /orders?status=active&user_id=42`). Complex search queries use `POST /search` with a JSON body, or a dedicated `POST /orders/search` endpoint. Elasticsearch uses `POST /_search` with a JSON body for this reason.

**Q: A Java developer asks: Spring's @PutMapping feels like "update" — is that wrong?**
Yes, that's a common mental shortcut that causes bugs. In Spring (and every framework), `@PutMapping` means "handle HTTP PUT method" — the framework doesn't enforce REST semantics. The developer must ensure the handler replaces the full resource, not partially updates it. If your Spring PUT handler calls `entity.setName(request.getName())` and leaves other fields unchanged, you've implemented PATCH semantics with PUT's URL — that's incorrect REST. Use `@PatchMapping` with partial update logic, or `@PutMapping` with full replacement logic.

**Q: How do I handle soft deletes in REST? DELETE feels permanent.**
The `DELETE /resource/{id}` endpoint is the correct REST verb. What happens internally (hard delete vs. setting `deleted_at`) is your implementation detail. However, if the "deleted" resource should still be queryable (`GET /users/42` returns `410 Gone` instead of `404 Not Found`), use `410` to distinguish "never existed" from "existed but was deleted." For soft-delete recovery, use a sub-resource: `POST /users/42/restoration`.
