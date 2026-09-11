// Import packages that allow for CSS styling to be applied to React elements
import styled, { keyframes } from 'styled-components';

// Slide the notice up from the bottom edge so it does not appear abruptly
const slideIn = keyframes`
  from {
    opacity: 0;
    transform: translate(-50%, 1rem);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
`;

// Pulse the indicator dot to signal that work is still in progress
const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
`;

// Pin the notice to the bottom of the viewport, centred, above page content.
// Bottom keeps it clear of the header's search and account controls.
export const StyledWakeNotice = styled.div`
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;

  display: flex;
  align-items: center;
  gap: 0.6rem;

  padding: 0.7rem 1.1rem;
  border-radius: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.15);

  background: rgba(20, 20, 24, 0.92);
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);

  color: #f2f2f2;
  font-size: 0.85rem;
  line-height: 1.3;

  animation: ${slideIn} 0.25s ease-out;

  @media (max-width: 768px) {
    /* Keep clear of the viewport edges on small screens */
    width: calc(100% - 2rem);
    justify-content: center;
    text-align: center;
  }
`;

// Small animated dot standing in for a spinner
export const StyledIndicator = styled.span`
  flex-shrink: 0;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: #f5c518;
  animation: ${pulse} 1.2s ease-in-out infinite;
`;
