import { act, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { WakeNotice } from '../src/components/wakeNotice';
import { requestFinished, requestStarted } from '../src/api/wakeState';

// The wake state is module-level and updates outside React's event system,
// so every transition is wrapped in act() to flush the resulting render.
const startRequest = () => act(() => requestStarted());
const finishRequest = () => act(() => requestFinished());
const waitMs = (ms) => act(() => vi.advanceTimersByTime(ms));

describe('WakeNotice', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    // Drain any request still counted as pending so state does not leak
    // between tests, then restore real timers.
    finishRequest();
    vi.useRealTimers();
  });

  const noticeText = /waking the demo api/i;

  it('stays hidden when no request is in flight', () => {
    render(<WakeNotice />);

    expect(screen.queryByText(noticeText)).not.toBeInTheDocument();
  });

  it('stays hidden while a request is still fast', () => {
    render(<WakeNotice />);

    startRequest();
    waitMs(1000);

    expect(screen.queryByText(noticeText)).not.toBeInTheDocument();
  });

  it('appears once a request has been pending past the slow threshold', () => {
    render(<WakeNotice />);

    startRequest();
    waitMs(3000);

    expect(screen.getByText(noticeText)).toBeInTheDocument();
  });

  it('disappears once the slow request settles', () => {
    render(<WakeNotice />);

    startRequest();
    waitMs(3000);
    expect(screen.getByText(noticeText)).toBeInTheDocument();

    finishRequest();

    expect(screen.queryByText(noticeText)).not.toBeInTheDocument();
  });

  it('keeps the notice up until every pending request settles', () => {
    render(<WakeNotice />);

    startRequest();
    startRequest();
    waitMs(3000);

    finishRequest();
    expect(screen.getByText(noticeText)).toBeInTheDocument();

    finishRequest();
    expect(screen.queryByText(noticeText)).not.toBeInTheDocument();
  });
});
