'use client';

import React, { useState, useEffect } from 'react';
import { booksAPI } from '@/lib/api';

function BookSection() {
  const [activeAction, setActiveAction] = useState<string | null>(null);

  // Data state
  const [books, setBooks] = useState<any[]>([]);
  const [limit, setLimit] = useState(10);
  const [offset, setOffset] = useState(0);

  // UI States
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form data - Books
  const [bookId, setBookId] = useState('');
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [isbn, setIsbn] = useState('');
  const [description, setDescription] = useState('');
  const [isAvailable, setIsAvailable] = useState(true);

  // Fetch books
  useEffect(() => {
    fetchBooks();
  }, [offset, limit]);

  // Clear success message after 2 seconds
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 2000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  // Fetch all books
  const fetchBooks = async () => {
    setLoading(true);
    try {
      const response = await booksAPI.getBooks({ limit, offset });
      setBooks(response.data);
      setError(null);
    } catch (err : any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Reset form
  const resetForm = () => {
    setActiveAction(null);
    setBookId('');
    setTitle('');
    setAuthor('');
    setIsbn('');
    setDescription('');
    setError(null);
  };

  // Create book
  const handleCreateBook = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    try {
      await booksAPI.createBook({
        title,
        author,
        isbn,
        description,
      });
      setSuccess('Book created successfully!');
      resetForm();
      fetchBooks();
    } catch (err : any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Update Book
  const handleUpdateBook = async (e : any) => {
    e.preventDefault();
    setLoading(true);
    try {
      const updateData: any = {};
      if (title) updateData.title = title;
      if (author) updateData.author = author;
      if (description) updateData.description = description;
      updateData.is_available = isAvailable;

      if (Object.keys(updateData).length === 0) {
        setError('Please provide at least one field to update');
        setLoading(false);
        return;
      }

      await booksAPI.updateBook(parseInt(bookId), updateData);
      setSuccess('Book updated successfully!');
      resetForm();
      fetchBooks();
    } catch (err : any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Search Book By ID
  const handleSearchBookById = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await booksAPI.getBook(parseInt(bookId));
      setBooks([response.data]);
      setSuccess('Book found!');
      setError(null);
    } catch (err : any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Delete a book
  const handleDeleteBook = async (e: any) => {
    e.preventDefault();
    if (!window.confirm('Are you sure you want to delete this book?')) return;

    setLoading(true);
    try {
      await booksAPI.deleteBook(parseInt(bookId));
      setSuccess('Book successfully deleted!');
      resetForm();
      fetchBooks();
    } catch (err : any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="section-content">
      <h2 className="section-title">Books Management</h2>

      {error && <div className="message error-message">{error}</div>}
      {success && <div className="message success-message">{success}</div>}

      <div className="action-buttons">
        <button onClick={() => { if(offset === 0) fetchBooks(); else setOffset(0); }}>Get Books</button>
        <button onClick={() => setActiveAction('createBook')}>Add Book</button>
        <button onClick={() => setActiveAction('updateBook')}>Edit Book</button>
        <button onClick={() => setActiveAction('searchBook')}>
          Search Book
        </button>
        <button onClick={() => setActiveAction('deleteBook')}>
          Delete Book
        </button>
      </div>

      {activeAction === 'createBook' && (
        <form onSubmit={handleCreateBook} className="action-form">
          <input
            type="text"
            placeholder="Title *"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Author *"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="ISBN *"
            value={isbn}
            onChange={(e) => setIsbn(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Description *"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <div className="form-buttons">
            <button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Book'}
            </button>
            <button type="button" onClick={resetForm}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {activeAction === 'updateBook' && (
        <form onSubmit={handleUpdateBook} className="action-form">
          <input
            type="number"
            placeholder="Book ID *"
            value={bookId}
            onChange={(e) => setBookId(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <input
            type="text"
            placeholder="Author"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
          />
          <input
            type="text"
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={isAvailable}
              onChange={(e) => setIsAvailable(e.target.checked)}
            />
            <span>Available</span>
          </label>
          <div className="form-buttons">
            <button type="submit" disabled={loading}>
              {loading ? 'Updating...' : 'Update Book'}
            </button>
            <button type="button" onClick={resetForm}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {activeAction === 'searchBook' && (
        <form onSubmit={handleSearchBookById} className="action-form">
          <input
            type="number"
            placeholder="Book ID *"
            value={bookId}
            onChange={(e) => setBookId(e.target.value)}
            required
          />
          <div className="form-buttons">
            <button type="submit" disabled={loading}>
              {loading ? 'Searching...' : 'Search Book'}
            </button>
            <button type="button" onClick={resetForm}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {activeAction === 'deleteBook' && (
        <form onSubmit={handleDeleteBook} className="action-form">
          <input
            type="number"
            placeholder="Book ID *"
            value={bookId}
            onChange={(e) => setBookId(e.target.value)}
            required
          />
          <div className="form-buttons">
            <button type="submit" disabled={loading}>
              {loading ? 'Deleting...' : 'Delete Book'}
            </button>
            <button type="button" onClick={resetForm}>
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="data-table">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Books List {books.length > 0 ? `(${offset + 1} - ${offset + books.length})` : '(Empty)'}</h3>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 font-medium">Rows per page:</span>
            <select 
              value={limit}
              onChange={(e) => { setLimit(Number(e.target.value)); setOffset(0); }}
              className="bg-white border-2 border-gray-200 text-xs rounded-md px-2 py-1 outline-none focus:border-[#7dd3e8] transition-colors cursor-pointer"
            >
              {[10, 20, 50, 100].map(v => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>
        </div>
        {loading && !activeAction ? (
          <p className="loading-text">Loading Books...</p>
        ) : books.length === 0 ? (
          <p className="no-data-text">No Books Found</p>
        ) : (
          <>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Author</th>
                  <th>ISBN</th>
                  <th>Description</th>
                  <th>Available</th>
                </tr>
              </thead>
              <tbody>
                {books.map((book) => (
                  <tr key={book.id}>
                    <td>{book.id}</td>
                    <td>{book.title}</td>
                    <td>{book.author}</td>
                    <td>{book.isbn}</td>
                    <td>{book.description || '-'}</td>
                    <td>{book.is_available ? 'Yes' : 'No'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="pagination-controls flex items-center justify-end gap-4 mt-6 py-4 border-t border-gray-100">
              <div className="flex items-center gap-2">
                <button 
                  onClick={() => setOffset(Math.max(0, offset - limit))}
                  disabled={offset === 0 || loading}
                  className="px-4 py-2 bg-white text-[#7dd3e8] border-2 border-[#7dd3e8] hover:bg-[#7dd3e8] hover:text-white disabled:opacity-30 rounded-lg transition-all text-sm disabled:cursor-not-allowed font-bold"
                >
                  Previous
                </button>
                <div className="px-4 py-2 bg-gray-50 border-2 border-gray-100 rounded-lg text-sm min-w-[100px] text-center font-bold text-gray-700">
                  Page {Math.floor(offset / limit) + 1}
                </div>
                <button 
                  onClick={() => setOffset(offset + limit)}
                  disabled={books.length < limit || loading}
                  className="px-4 py-2 bg-white text-[#7dd3e8] border-2 border-[#7dd3e8] hover:bg-[#7dd3e8] hover:text-white disabled:opacity-30 rounded-lg transition-all text-sm disabled:cursor-not-allowed font-bold"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default BookSection;
