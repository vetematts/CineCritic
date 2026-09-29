import { expect, test, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { MovieDetailPage } from '../src/pages/movieDetailPage';
import { get } from '../src/api/api';

vi.mock('../src/api/api', () => ({
  get: vi.fn(),
}));

vi.mock('../src/contexts/AuthContext', () => ({
  useAuth: () => ({ user: null }),
}));

test('renders movie detail and reviews', async () => {
  get
    .mockResolvedValueOnce({ title: 'Alien', release_date: '1979-05-25' })
    .mockResolvedValueOnce([{ id: 1, content: 'Great movie', rating: 5 }]);

  render(
    <MemoryRouter initialEntries={['/movies/123']}>
      <Routes>
        <Route path="/movies/:id" element={<MovieDetailPage />} />
      </Routes>
    </MemoryRouter>
  );

  await waitFor(() => {
    expect(get).toHaveBeenCalledWith('/api/movies/123');
  });

  expect(screen.getByText('Alien')).toBeInTheDocument();
  expect(screen.getByText(/May 25, 1979/i)).toBeInTheDocument();
  expect(screen.getByText('Great movie')).toBeInTheDocument();
});

test('renders movie poster when poster_path is provided', async () => {
  get
    .mockResolvedValueOnce({
      title: 'Alien',
      poster_path: '/alien-poster.jpg',
      release_date: '1979-05-25',
    })
    .mockResolvedValueOnce([]);

  render(
    <MemoryRouter initialEntries={['/movies/123']}>
      <Routes>
        <Route path="/movies/:id" element={<MovieDetailPage />} />
      </Routes>
    </MemoryRouter>
  );

  await waitFor(() => {
    const poster = screen.getByAltText('Alien poster');
    expect(poster).toBeInTheDocument();
    expect(poster).toHaveAttribute('src', 'https://image.tmdb.org/t/p/w500/alien-poster.jpg');
  });
});

test('renders placeholder when poster_path is missing', async () => {
  get
    .mockResolvedValueOnce({ title: 'Alien', release_date: '1979-05-25' })
    .mockResolvedValueOnce([]);

  render(
    <MemoryRouter initialEntries={['/movies/123']}>
      <Routes>
        <Route path="/movies/:id" element={<MovieDetailPage />} />
      </Routes>
    </MemoryRouter>
  );

  await waitFor(() => {
    expect(screen.getByText('No poster available')).toBeInTheDocument();
  });
  expect(screen.queryByAltText('')).not.toBeInTheDocument();
});

test('removes a failed backdrop while keeping the movie details and poster', async () => {
  get
    .mockResolvedValueOnce({
      title: 'Alien',
      poster_path: '/alien-poster.jpg',
      backdrop_path: '/alien-backdrop.jpg',
    })
    .mockResolvedValueOnce([]);

  render(
    <MemoryRouter initialEntries={['/movies/123']}>
      <Routes>
        <Route path="/movies/:id" element={<MovieDetailPage />} />
      </Routes>
    </MemoryRouter>
  );

  const backdrop = await screen.findByAltText('');
  expect(backdrop).toHaveAttribute('src', 'https://image.tmdb.org/t/p/w1280/alien-backdrop.jpg');
  fireEvent.error(backdrop);

  expect(screen.queryByAltText('')).not.toBeInTheDocument();
  expect(screen.getByRole('heading', { name: 'Alien' })).toBeInTheDocument();
  expect(screen.getByAltText('Alien poster')).toBeInTheDocument();
});

test('handles posterUrl (full URL) from backend', async () => {
  get
    .mockResolvedValueOnce({
      title: 'Alien',
      posterUrl: 'https://image.tmdb.org/t/p/w500/custom-alien.jpg',
      release_date: '1979-05-25',
    })
    .mockResolvedValueOnce([]);

  render(
    <MemoryRouter initialEntries={['/movies/123']}>
      <Routes>
        <Route path="/movies/:id" element={<MovieDetailPage />} />
      </Routes>
    </MemoryRouter>
  );

  await waitFor(() => {
    const poster = screen.getByAltText('Alien poster');
    expect(poster).toHaveAttribute('src', 'https://image.tmdb.org/t/p/w500/custom-alien.jpg');
  });
});
