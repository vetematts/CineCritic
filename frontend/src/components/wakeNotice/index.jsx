// Track whether an API request has been pending long enough to explain
import { useEffect, useState } from 'react';

import { subscribeToWakeState } from '../../api/wakeState';

// Import the styling for the wake notice
import { StyledIndicator, StyledWakeNotice } from './style';

// Shows a brief banner while the demo API starts back up. The hosted API sleeps
// when idle, so an occasional first request waits for the container to boot.
// Without this the page just looks broken for the better part of a minute.
export function WakeNotice() {
  const [isWaking, setIsWaking] = useState(false);

  useEffect(() => subscribeToWakeState(setIsWaking), []);

  if (!isWaking) {
    return null;
  }

  return (
    <StyledWakeNotice role="status" aria-live="polite">
      <StyledIndicator />
      Waking the demo API — this can take up to a minute on first load.
    </StyledWakeNotice>
  );
}
