// Import packages that allow us to track which page we're on
import { Outlet } from 'react-router-dom';

// Plugin the top level components that will exist on all the pages
import { Header } from '../../components/header';
import { Footer } from '../../components/footer';
import { WakeNotice } from '../../components/wakeNotice';

// Import the CSS styling for the home page and page layouts
import { StyledMain } from './style';

// Create a templated layout for the webpage
export function PageLayout({ currentPage }) {
  return (
    <>
      {/* Explains the free-tier cold start on whichever page triggers it */}
      <WakeNotice />
      {/* Only show the header when we're
                not on the main/front page */}
      {currentPage !== '/' && <Header />}
      <StyledMain>
        <Outlet />
      </StyledMain>
      <Footer />
    </>
  );
}
