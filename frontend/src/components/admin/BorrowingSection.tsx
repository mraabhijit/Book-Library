'use client';

import { useState, useEffect } from 'react';
import { borrowingsAPI } from '@/lib/api';

function BorrowingSection() {
  const [activeAction, setActiveAction] = useState<string | null>(null);
  const [view, setView] = useState<'current' | 'history' | 'member'>('current');

  // Data state
  const [borrowings, setBorrowings] = useState<any[]>([]);
  const [limit, setLimit] = useState(10);
  const [offset, setOffset] = useState(0);

  // UI States
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form data - Borrowings
  const [bookId, setBookId] = useState('');
  const [memberId, setMemberId] = useState('');

  // Auto-fetch data when pagination or view changes
  useEffect(() => {
    if (view === 'current') {
      fetchCurrentBorrowings();
    } else if (view === 'history') {
      fetchAllBorrowings();
    } else if (view === 'member' && memberId) {
      // For member search, we only auto-fetch if we already have a memberId
      fetchBorrowingsByMember();
    }
  }, [offset, limit, view]);

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
      const response = await borrowingsAPI.getAllBorrowings({ limit, offset });
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
      const response = await borrowingsAPI.getCurrentBorrowings({ limit, offset });
      setBorrowings(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch borrowings by member ID
  const fetchBorrowingsByMember = async () => {
    if (!memberId) return;
    setLoading(true);
    try {
      const response = await borrowingsAPI.getBorrowingsByMember(parseInt(memberId), { limit, offset });
      setBorrowings(response.data);
      setSuccess('Borrowing records found!');
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
      setView('current');
      setOffset(0);
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
      setView('current');
      setOffset(0);
      fetchCurrentBorrowings();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  // Search borrowings by member ID (Manual trigger)
  const handleSearchByMember = (e: any) => {
    e.preventDefault();
    setOffset(0);
    setView('member');
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
        <button 
          className={view === 'current' ? 'active' : ''} 
          onClick={() => { setView('current'); setOffset(0); }}
        >
          Current Borrowings
        </button>
        <button 
          className={view === 'history' ? 'active' : ''} 
          onClick={() => { setView('history'); setOffset(0); }}
        >
          All History
        </button>
        <button onClick={() => setActiveAction('borrowBook')}>Borrow Book</button>
        <button onClick={() => setActiveAction('returnBook')}>Return Book</button>
        <button 
          className={view === 'member' ? 'active' : ''} 
          onClick={() => setActiveAction('searchByMember')}
        >
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
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">
            {view === 'current' ? 'Current Borrowings' : view === 'history' ? 'Borrowing History' : `Member ${memberId} Records`} 
            {borrowings.length > 0 ? ` (${offset + 1} - ${offset + borrowings.length})` : ' (Empty)'}
          </h3>
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
          <p className="loading-text">Loading Borrowings...</p>
        ) : borrowings.length === 0 ? (
          <p className="no-data-text">No borrowing records found</p>
        ) : (
          <>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Book Title</th>
                  <th>Member Name</th>
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
                    <td>{formatDate(borrowing.borrowed_date)}</td>
                    <td>{formatDate(borrowing.due_date)}</td>
                    <td>{formatDate(borrowing.returned_date)}</td>
                    <td>
                      <span className={borrowing.returned_date ? 'status-returned' : 'status-borrowed'}>
                        {borrowing.returned_date ? 'Returned' : 'Borrowed'}
                      </span>
                    </td>
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
                  disabled={borrowings.length < limit || loading}
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

export default BorrowingSection;
