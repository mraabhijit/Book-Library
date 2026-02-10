'use client';

import { useState } from 'react';
import BookTable from '@/components/BookTable';
import { booksAPI } from '@/lib/api';
import { Book } from '@/lib/types';

function SearchBar() {
  const [titleInput, setTitleInput] = useState('');
  const [authorInput, setAuthorInput] = useState('');
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    // Build the query parameters
    const params: any = {};

    if (titleInput.trim()) {
      params.title = titleInput.trim();
    }
    if (authorInput.trim()) {
      params.author = authorInput.trim();
    }

    // Set loading state
    setLoading(true);
    setError(null);

    try {
      const response = await booksAPI.getBooks(params);

      console.log('search results:', response.data);
      setBooks(response.data);
    } catch (err: any) {
      console.error('Error fetching books:', err);
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="search-container">
        <input
          type="text"
          placeholder="Book Title"
          value={titleInput}
          onChange={(e) => setTitleInput(e.target.value)}
          className="search-input"
        />

        <input
          type="text"
          placeholder="Book Author"
          value={authorInput}
          onChange={(e) => setAuthorInput(e.target.value)}
          className="search-input"
        />

        <button
          onClick={handleSearch}
          className="search-button"
          disabled={loading} // Disable btn while loading
        >
          {loading ? '⏳' : '🔍'}
        </button>
      </div>

      {/* Display error if any */}
      {error && <div className="error-message">Error: {error}</div>}

      {/* Display results count */}
      {!loading && books.length > 0 && (
        <div className="results-info">Found {books.length} book(s)</div>
      )}

      {/* Display the books table */}
      <BookTable books={books} />
    </>
  );
}

export default SearchBar;
