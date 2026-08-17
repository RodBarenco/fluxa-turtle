# Bug report — growing a `dyn` after a window exists segfaults

**Repro:** [`repros/dyn_growth_with_window.flx`](dyn_growth_with_window.flx) ·
**Found in:** Fluxa Turtle, writing a call that takes a list of points ·
**Severity:** crashes the process, no error, no message

---

## The claim

Growing a `dyn` array past its end is documented (`FLUXA_GUIDE.md`: *"events[4] =
99 // auto-grows"*) and works. Doing it **after `graph.init` has created a
window** segfaults, at an unpredictable point, in an unpredictable fraction of
runs.

```fluxa
import std graph

dyn win = graph.init(400, 300, "repro")

dyn p = [0.0]
int k = 1
while k < 160 {
    p[k] = 1.0
    k = k + 1
}

print("survived, len = ", len(p))
graph.close(win)
```

Two of six runs survive. The **same two statements in the other order** — grow
first, open the window afterwards — survive six of six.

---

## Environment

| | |
|---|---|
| binary | `fluxa`, 2 117 296 bytes, built 2026-08-17 |
| backends | `raylib/6.0`, `miniaudio/0.11.25`, `minimp4 + minih264e` |
| GL | Mesa 25.1.5, Core Profile 4.6 |
| OS | Pop!_OS, kernel 7.0.11-76070011 |

---

## The stack

Under `gdb`, on the fault:

```
Thread 1 "fluxa" received signal SIGSEGV, Segmentation fault.
#0  value_release_data ()
#1  value_release_data ()      <- nested: a container releasing its elements
#2  eval ()
#3  eval ()
#4  eval ()
#5  runtime_exec_persist.part ()
#6  run_once ()
#7  main ()
```

**No raylib frame anywhere.** The fault is in the runtime's own value-release
path, reached from evaluating the assignment, and `value_release_data` is on the
stack twice — a container releasing what it holds.

---

## What changes it

Six runs each, one thing changed at a time.

| | |
|---|---|
| growth alone, no libs imported | **6/6 survive** |
| growth after two `image.new(1024, 1024)`, never discarded | **6/6** |
| a window, no growth (the same loop writing in place) | **6/6** |
| growth **first**, window opened afterwards | **6/6** |
| window **first**, then growth | **0/6** |

And the amount of growth changes the odds rather than the outcome — eight runs
each, window first:

| grown to | survives |
|---|---|
| 20 elements | 8/8 |
| 40 | 7/8 |
| 80 | 5/8 |
| 160 | 3/8 |

## What does not change it

| | |
|---|---|
| `prst dyn p` instead of `dyn p` | 1/6 survive |
| reading `p[0]` on every iteration | 0/6 |
| the anchor idiom (`guard[0] = k` before the write) | 2/6 |
| `gc_cap = 8192` | 0/6 |
| `gc_cap = 65536` | 1/6 |
| *(control)* | 2/6 |

So it is **not** the value being unrooted — `prst` does not save it — and it is
**not** the GC table filling: sixty-four times the capacity makes no difference.

## Where it dies

Printing the index after each write, five runs died after element **24**, **66**,
**80**, and twice reached the end. No particular growth step is the bad one.

---

## The hypothesis this all fits

**A pointer to a buffer that has already been handed back.**

The growth reallocates the array's storage. Something still holds the old
pointer — a copy of the value struct, a GC table entry, a cached slot — and
releases it later, by which time the allocator may have reused the block.

It explains every observation at once:

- **why the order matters** — a window is a large, immediate allocation, so the
  freed block is reused sooner and the stale pointer lands on live data;
- **why more growth is worse** — every growth is another chance;
- **why `prst` and anchoring do not help** — the *value* is rooted; the *buffer*
  is gone;
- **why `gc_cap` does not help** — nothing is being collected early;
- **why raylib is not on the stack** — it is not raylib's memory that is wrong;
- **why the death point moves** — it depends on what the allocator does next.

---

## What would confirm it in one line

Build the runtime with `-fsanitize=address` and run this repro. ASan will name
the block, the free site and the use site directly. The measurements above are
the best a black box can do; that build turns it into a fact.

## Where to look

- whatever implements assignment past the end of a `dyn` array — the realloc,
  and every place that holds a pointer or index into the old storage;
- `value_release_data` — the nested call suggests a container release walking
  elements that are already gone;
- `runtime_exec_persist` — this ran under it, which is where the statement loop
  lives.
