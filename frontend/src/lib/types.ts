// Book Types
export interface Book {
  id: number;
  title: string;
  author: string;
  isbn: string;
  description?: string;
  is_available: boolean;
  created_at: string;
  updated_at: string;
}

export interface BookCreate {
  title: string;
  author: string;
  isbn: string;
  description?: string;
}

export interface BookUpdate {
  title?: string;
  author?: string;
  description?: string;
  is_available: boolean;
}

// Member Types
export interface Member {
  id: number;
  name?: string;
  email: string;
  phone?: string;
  created_at: string;
  updated_at: string;
}

export interface MemberCreate {
  name?: string;
  email: string;
  phone?: string;
}

export interface MemberUpdate {
  name?: string;
  email?: string;
  phone?: string;
}

// Borrowing Types
export interface Borrowing {
  id: number;
  book_id: number;
  member_id: number;
  borrowed_date: string;
  due_date?: string;
  returned_date?: string;
  status: string;
  book?: Book;
  member?: Member;
}

export interface BorrowRequest {
  book_id: number;
  member_id: number;
  due_date?: string;
}

export interface ReturnRequest {
  book_id: number;
  member_id: number;
}

// Auth Types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}
