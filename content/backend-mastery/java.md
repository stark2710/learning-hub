---
module: 21
name: JVM Internals
---
- l1 | JVM Architecture — Classloader, Runtime Data Areas | m21-l1-jvm-arch
- l2 | Bytecode & JIT — HotSpot C1/C2, Inlining, Escape Analysis | m21-l2-bytecode-jit
- l3 | Java Memory Model — Heap, Metaspace, GC Roots | m21-l3-java-memory
- l4 | GC Deep Dive — G1, ZGC, Shenandoah | m21-l4-gc

---
module: 22
name: Java Concurrency
---
- l1 | Java Memory Model — happens-before, volatile | m22-l1-jmm
- l2 | synchronized & Locks — ReentrantLock, StampedLock | m22-l2-locks
- l3 | ExecutorService & ThreadPoolExecutor Internals | m22-l3-executors
- l4 | CompletableFuture — Async Pipelines | m22-l4-completable-future
- l5 | Virtual Threads (Project Loom) — Java 21 | m22-l5-virtual-threads

---
module: 23
name: Collections Internals
---
- l1 | ArrayList & LinkedList — Memory Layout, Cache Locality | m23-l1-arraylist
- l2 | HashMap Internals — Hashing, Treeification, Resize | m23-l2-hashmap
- l3 | ConcurrentHashMap — Lock Striping, CAS Operations | m23-l3-concurrenthashmap
- l4 | Queue, Deque, PriorityQueue — Heap Internals | m23-l4-queues
- l5 | Java Streams — Lazy Evaluation, Spliterators, Parallel | m23-l5-streams

---
module: 24
name: Type System & OOP Deep Dive
---
- l1 | Generics — Type Erasure, Wildcards, Bounded Params | m24-l1-generics
- l2 | Interfaces — Default Methods, Sealed Interfaces | m24-l2-interfaces
- l3 | Reflection & Annotations — Runtime Metaprogramming | m24-l3-reflection
- l4 | Records & Sealed Classes — Modern Data Modeling | m24-l4-records
- l5 | Pattern Matching — instanceof & switch (Java 21) | m24-l5-pattern-matching

---
module: 25
name: Modern Java (8–21)
---
- l1 | Lambdas & Functional Interfaces — invokedynamic | m25-l1-lambdas
- l2 | Optional — Right Ways and Wrong Ways | m25-l2-optional
- l3 | Java Time API — Why it Replaced Date/Calendar | m25-l3-time-api
- l4 | JPMS — Java Modules & Strong Encapsulation | m25-l4-modules
- l5 | Java 15–21 Language Tour — Records, Sealed, Patterns | m25-l5-language-tour

---
module: 26
name: Spring Framework Internals
---
- l1 | IoC Container — BeanFactory, ApplicationContext, Lifecycle | m26-l1-ioc
- l2 | Dependency Injection — @Autowired Resolution, Circular Deps | m26-l2-di
- l3 | Spring AOP — JDK Proxy vs CGLIB, @Transactional | m26-l3-aop
- l4 | Spring Boot — Auto-configuration & Starter Anatomy | m26-l4-boot
- l5 | Spring Data JPA — N+1 Problem, Entity Lifecycle | m26-l5-jpa

---
module: 27
name: Java Performance & Production
---
- l1 | Profiling — async-profiler, Flame Graphs | m27-l1-profiling
- l2 | GC Tuning — Heap Sizing, GC Log Analysis | m27-l2-gc-tuning
- l3 | JMH — Benchmarking Without Lies | m27-l3-jmh
- l4 | Production JVM — Flags, Thread Dumps, OOM Diagnosis | m27-l4-production
