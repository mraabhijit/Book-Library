'use client';

import { Book } from '@/lib/types';

function BookTable({ books }: { books: Book[] }) {
  if (books.length === 0) {
    return (
      <div className="no-books-message">
        No Books found. Try searching for something!
      </div>
    );
  }

  return (
    <div className="table-container">
      <table className="books-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Author</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          {books.map((book: any) => (
            <tr key={book.id}>
              <td>{book.title}</td>
              <td>{book.author}</td>
              <td>{book.description || ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default BookTable;
