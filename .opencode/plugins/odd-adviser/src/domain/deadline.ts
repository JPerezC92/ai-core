// Domain port for one evaluation's time bound. It names the schedule and cancel contract
// without reading a clock or owning a timer: composition supplies the real timer, and a
// test supplies a manually triggered double. This module performs no IO.

export type Deadline = {
  schedule(timeoutMs: number, onElapsed: () => void): () => void;
};
