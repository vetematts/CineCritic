// The demo API runs on a free tier that spins down when idle, so the first
// request after a quiet period can block for the better part of a minute while
// the container starts. Requests still succeed, they are just slow, so this
// module tracks in-flight requests and reports when one has been waiting long
// enough to be worth explaining to the user.

// How long a request must be pending before it counts as a cold start.
const SLOW_REQUEST_MS = 2500;

const listeners = new Set();

let pendingCount = 0;
let slowTimer = null;
let isWaking = false;

const notify = () => {
  listeners.forEach((listener) => listener(isWaking));
};

const setWaking = (value) => {
  if (isWaking === value) {
    return;
  }

  isWaking = value;
  notify();
};

// Called when a request starts. The first pending request arms the timer.
export const requestStarted = () => {
  pendingCount += 1;

  if (slowTimer === null) {
    slowTimer = setTimeout(() => setWaking(true), SLOW_REQUEST_MS);
  }
};

// Called when a request settles, whether it resolved or rejected.
export const requestFinished = () => {
  pendingCount = Math.max(0, pendingCount - 1);

  if (pendingCount > 0) {
    return;
  }

  // Nothing is in flight, so the backend is awake (or has failed outright).
  if (slowTimer !== null) {
    clearTimeout(slowTimer);
    slowTimer = null;
  }

  setWaking(false);
};

// Subscribe to waking-state changes. Returns an unsubscribe function.
export const subscribeToWakeState = (listener) => {
  listeners.add(listener);
  listener(isWaking);

  return () => listeners.delete(listener);
};

export const getWakeState = () => isWaking;
