import '../../css/Admin.css';
import { useState, useEffect } from 'react';
import { booksAPI } from '../../services/api';

function BookSection() {
  const [activeAction, setActiveAction] = useState(null);

  // Data state
  const [books, setBooks] = useState([]);

  // UI States
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

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
  }, []);

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
      const response = await booksAPI.getBooks();
      setBooks(response.data);
      setError(null);
    } catch (err) {
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
  const handleCreateBook = async (e) => {
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
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Update Book
  const handleUpdateBook = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const updateData = {};
      if (title) updateData.title = title;
      if (author) updateData.author = author;
      if (description) updateData.description = description;
      updateData.is_available = isAvailable;

      if (Object.keys(updateData).length === 0) {
        setError('Please provide at least one field to update');
        setLoading(false);
        return;
      }

      await booksAPI.updateBook(bookId, updateData);
      setSuccess('Book updated successfully!');
      resetForm();
      fetchBooks();
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Search Book By ID
  const handleSearchBookById = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await booksAPI.getBook(bookId);
      setBooks([response.data]);
      setSuccess('Book found!');
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Delete a book
  const handleDeleteBook = async (e) => {
    e.preventDefault();
    if (!window.confirm('Are you sure you want to delete this book?')) return;

    setLoading(true);
    try {
      await booksAPI.deleteBook(bookId);
      setSuccess('Book successfully deleted!');
      resetForm();
      fetchBooks();
    } catch (err) {
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
        <button onClick={fetchBooks}>Get Books</button>
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
        <h3>Books List ({books.length})</h3>
        {loading && !activeAction ? (
          <p className="loading-text">Loading Books...</p>
        ) : books.length === 0 ? (
          <p className="no-data-text">No Books Found</p>
        ) : (
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
        )}
      </div>
    </div>
  );
}

export default BookSection;
