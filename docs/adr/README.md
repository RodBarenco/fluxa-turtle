# Design decisions

A record of the decisions that shaped Fluxa Turtle, with the reason for each
and what it cost. What is here is what is not obvious from the code — usually
because it came out of a runtime constraint measured in practice.

| # | Decision |
|---|---|
| [0001](0001-persistent-state-at-program-level-only.md) | Persistent state at program level only |
| [0002](0002-the-code-is-the-source-of-truth.md) | The code is the source of truth, not the drawing |
| [0003](0003-path-baked-into-a-texture.md) | The path lives in a texture, it is not redrawn |
| [0004](0004-occupancy-grid-in-the-timeline.md) | An occupancy grid instead of scanning the queue |
| [0005](0005-turtle-as-a-typeof-instance.md) | Turtle as a `typeof` instance, state in singleton pools |
| [0006](0006-deterministic-render-by-frame-index.md) | Deterministic render by frame index |
| [0007](0007-export-as-a-png-sequence.md) | Export as a PNG sequence |
| [0008](0008-opacity-by-mixing-with-the-background.md) | Opacity by mixing with the background |
| [0009](0009-appearance-is-a-timeline-event.md) | An appearance change is a timeline event |
| [0010](0010-the-video-is-a-second-pass-over-the-frames.md) | The video is a second pass over the frames |
| [0011](0011-the-artwork-file-declares.md) | The artwork file declares, the runner executes |
