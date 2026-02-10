'use client';

import { useState, useEffect } from 'react';
import { borrowingsAPI } from '@/lib/api';

function BorrowingSection() {
  const [activeAction, setActiveAction] = useState<string | null>(null);

  // Data state
  const [borrowings, setBorrowings] = useState<any[]>([]);

  // UI States
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form data - Borrowings
  const [bookId, setBookId] = useState('');
  const [memberId, setMemberId] = useState('');

  // Fetch current borrowings on mount
  useEffect(() => {
    fetchCurrentBorrowings();
  }, []);

  // Clear success message after 2 seconds
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 2000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  // Fetch all borrowing history
  const fetchAllBorrowings = async () => {
    setLoading(true);
    try {
      const response = await borrowingsAPI.getAllBorrowings();
      setBorrowings(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch current borrowings (not returned yet)
  const fetchCurrentBorrowings = async () => {
    setLoading(true);
    try {
      const response = await borrowingsAPI.getCurrentBorrowings();
      setBorrowings(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Reset form
  const resetForm = () => {
    setActiveAction(null);
    setBookId('');
    setMemberId('');
    setError(null);
  };

  // Borrow a book
  const handleBorrowBook = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    try {
      await borrowingsAPI.borrowBook({
        book_id: parseInt(bookId),
        member_id: parseInt(memberId),
      });
      setSuccess('Book borrowed successfully!');
      resetForm();
      fetchCurrentBorrowings();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Return a book
  const handleReturnBook = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    try {
      await borrowingsAPI.returnBook({
        book_id: parseInt(bookId),
        member_id: parseInt(memberId),
      });
      setSuccess('Book returned successfully!');
      resetForm();
      fetchCurrentBorrowings();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Search borrowings by member ID
  const handleSearchByMember = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await borrowingsAPI.getBorrowingsByMember(
        parseInt(memberId),
      );
      setBorrowings(response.data);
      setSuccess('Borrowing records found!');
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Format date for display
  const formatDate = (dateString: string | null | undefined): string => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="section-content">
      <h2 className="section-title">Borrowings Management</h2>

      {error && <div className="message error-message">{error}</div>}
      {success && <div className="message success-message">{success}</div>}

      <div className="action-buttons">
        <button onClick={fetchCurrentBorrowings}>Current Borrowings</button>
        <button onClick={fetchAllBorrowings}>All History</button>
        <button onClick={() => setActiveAction('borrowBook')}>
          Borrow Book
        </button>
        <button onClick={() => setActiveAction('returnBook')}>
          Return Book
        </button>
        <button onClick={() => setActiveAction('searchByMember')}>
          Search by Member
        </button>
      </div>

      {activeAction === 'borrowBook' && (
        <form onSubmit={handleBorrowBook} className="action-form">
          <input
            type="number"
            placeholder="Book ID *"
            value={bookId}
            onChange={(e) => setBookId(e.target.value)}
            required
          />
          <input
            type="number"
            placeholder="Member ID *"
            value={memberId}
            onChange={(e) => setMemberId(e.target.value)}
            required
          />
          <div className="form-buttons">
            <button type="submit" disabled={loading}>
              {loading ? 'Borrowing...' : 'Borrow Book'}
            </button>
            <button type="button" onClick={resetForm}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {activeAction === 'returnBook' && (
        <form onSubmit={handleReturnBook} className="action-form">
          <input
            type="number"
            placeholder="Book ID *"
            value={bookId}
            onChange={(e) => setBookId(e.target.value)}
            required
          />
          <input
            type="number"
            placeholder="Member ID *"
            value={memberId}
            onChange={(e) => setMemberId(e.target.value)}
            required
          />
          <div className="form-buttons">
            <button type="submit" disabled={loading}>
              {loading ? 'Returning...' : 'Return Book'}
            </button>
            <button type="button" onClick={resetForm}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {activeAction === 'searchByMember' && (
        <form onSubmit={handleSearchByMember} className="action-form">
          <input
            type="number"
            placeholder="Member ID *"
            value={memberId}
            onChange={(e) => setMemberId(e.target.value)}
            required
          />
          <div className="form-buttons">
            <button type="submit" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </button>
            <button type="button" onClick={resetForm}>
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="data-table">
        <h3>Borrowings List ({borrowings.length})</h3>
        {loading && !activeAction ? (
          <p className="loading-text">Loading Borrowings...</p>
        ) : borrowings.length === 0 ? (
          <p className="no-data-text">No Borrowing Records Found</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Book Title</th>
                <th>Member Name</th>
                <th>Member Email</th>
                <th>Borrowed Date</th>
                <th>Due Date</th>
                <th>Returned Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {borrowings.map((borrowing) => (
                <tr key={borrowing.id}>
                  <td>{borrowing.id}</td>
                  <td>{borrowing.book?.title || '-'}</td>
                  <td>{borrowing.member?.name || '-'}</td>
                  <td>{borrowing.member?.email || '-'}</td>
                  <td>{formatDate(borrowing.borrowed_date)}</td>
                  <td>{formatDate(borrowing.due_date)}</td>
                  <td>{formatDate(borrowing.returned_date)}</td>
                  <td>
                    <span
                      className={
                        borrowing.returned_date
                          ? 'status-returned'
                          : 'status-borrowed'
                      }
                    >
                      {borrowing.returned_date ? 'Returned' : 'Borrowed'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default BorrowingSection;
