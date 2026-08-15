# 0001 — Persistent state at program level only

**Status:** accepted

## Context

The whole product depends on state surviving the hot reload: that is what makes
finished steps not repeat. The question was where to keep that state.

The natural route would be `prst` on a Block field, which the language
documentation allows. We measured it, with parameterless methods so as not to
contaminate the test:

```
RUN 1 | instance c1.n= 1 | singleton C.n= 1 | runs= 1
RUN 2 | instance c1.n= 1 | singleton C.n= 1 | runs= 2
RUN 3 | instance c1.n= 1 | singleton C.n= 1 | runs= 3
```

A Block's `prst` field is reinitialised on every reload — both for a `typeof`
instance and for the singleton, both in `main.flx` and in a module. Only the
program-level `prst` variable (`runs`) accumulates.

A program-level `prst arr` with a literal initializer (`= 0`) also resets: the
fill is applied again on reload.

There is one more trap: a function does not see an outer-scope `prst`, and it
fails **silently**. An ordinary variable gives a clean error
(`undefined variable`); `prst` gives no error at all, and the name even ends up
aliasing a parameter.

## Decision

All state that needs to survive a save lives in program-level `prst` variables,
declared in `main.flx`, and is passed explicitly as an argument. There are
exactly four:

```fluxa
prst dyn win    = graph.init(800, 600, "Fluxa Turtle")
prst dyn canvas = image.new(800, 600)
prst dyn bg     = image.new(1, 1)
prst int done   = 0
```

`done` returns to `main.flx` through `play`'s return value, because an `int` is
passed by value.

## Consequences

- `main.flx` owns the state. The modules are pure logic over what they receive.
- Only four values cross the reload. Everything else is rebuilt — which led
  straight to decision [0002](0002-the-code-is-the-source-of-truth.md).
- No function ever references an outer `prst`. It is a style rule that cannot be
  relaxed: breaking it does not show up as an error.
