'use client';

import { useState, useEffect } from 'react';
import BookTable from '@/components/BookTable';
import { booksAPI } from '@/lib/api';
import { Book } from '@/lib/types';

function SearchBar() {
  const [titleInput, setTitleInput] = useState('');
  const [authorInput, setAuthorInput] = useState('');
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Pagination state
  const [limit, setLimit] = useState(10);
  const [offset, setOffset] = useState(0);

  // Auto-search logic when pagination changes
  useEffect(() => {
    // Only fetch if we have some input OR if we want to show initial books
    // Usually a "search" should be explicit, but pagination is a change to current search
    if (books.length > 0) {
      handleSearch();
    }
  }, [offset, limit]);

  const handleSearch = async (isNewSearch = false) => {
    if (isNewSearch) {
      setOffset(0);
    }

    const params: any = {
      limit,
      offset: isNewSearch ? 0 : offset
    };

    if (titleInput.trim()) {
      params.title = titleInput.trim();
    }
    if (authorInput.trim()) {
      params.author = authorInput.trim();
    }

    setLoading(true);
    setError(null);

    try {
      const response = await booksAPI.getBooks(params);
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
          onClick={() => handleSearch(true)}
          className="search-button"
          disabled={loading}
        >
          {loading ? '⏳' : '🔍'}
        </button>
      </div>

      {error && <div className="error-message">Error: {error}</div>}

      {!loading && books.length > 0 && (
        <div className="flex flex-col items-center">
          <div className="results-info mb-4">
            Found records: {offset + 1} - {offset + books.length}
          </div>
          
          <BookTable books={books} />

          <div className="pagination-controls flex items-center justify-center gap-4 mt-8 mb-12">
             <div className="flex items-center gap-2">
                <button 
                  onClick={() => setOffset(Math.max(0, offset - limit))}
                  disabled={offset === 0 || loading}
                  className="px-6 py-2 bg-white text-[#7dd3e8] border-2 border-[#7dd3e8] hover:bg-[#7dd3e8] hover:text-white disabled:opacity-30 rounded-full transition-all text-sm disabled:cursor-not-allowed font-bold shadow-sm"
                >
                  Previous
                </button>
                <div className="px-6 py-2 bg-white border-2 border-gray-100 rounded-full text-sm min-w-[120px] text-center font-bold text-gray-700 shadow-sm">
                  Page {Math.floor(offset / limit) + 1}
                </div>
                <button 
                  onClick={() => setOffset(offset + limit)}
                  disabled={books.length < limit || loading}
                  className="px-6 py-2 bg-white text-[#7dd3e8] border-2 border-[#7dd3e8] hover:bg-[#7dd3e8] hover:text-white disabled:opacity-30 rounded-full transition-all text-sm disabled:cursor-not-allowed font-bold shadow-sm"
                >
                  Next
                </button>
              </div>

              <div className="ml-4 flex items-center gap-2">
                <span className="text-xs text-gray-500 font-medium whitespace-nowrap">View:</span>
                <select 
                  value={limit}
                  onChange={(e) => { setLimit(Number(e.target.value)); setOffset(0); }}
                  className="bg-white border-2 border-gray-100 text-xs rounded-full px-4 py-2 outline-none focus:border-[#7dd3e8] transition-colors cursor-pointer shadow-sm font-bold"
                >
                  {[10, 20, 50, 100].map(v => <option key={v} value={v}>{v}</option>)}
                </select>
              </div>
          </div>
        </div>
      )}

      {!loading && books.length === 0 && titleInput && authorInput && (
        <div className="no-books-message">No books matching your criteria</div>
      )}
    </>
  );
}

export default SearchBar;
