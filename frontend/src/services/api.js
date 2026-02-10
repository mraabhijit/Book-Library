import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

console.log('API Base URL:', baseURL);

const api = axios.create({
    baseURL: baseURL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    }
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            console.error('Unauthorized access');
        }
        return Promise.reject(error);
    }
);

// Books API

export const booksAPI = {
    // get all books with optional filters
    getBooks: (params = {}) => {
        return api.get('/books/', { params });
    },

    // get single book by ID
    getBook: (id) => {
        return api.get(`/books/${id}`);
    },

    // create book
    createBook: (bookData) => {
        return api.post('/books/', bookData);
    },

    // update a book
    updateBook: (id, bookData) => {
        return api.put(`/books/${id}`, bookData);
    },

    // delete a book
    deleteBook: (id) => {
        return api.delete(`/books/${id}`);
    }
};

// Authentication API

export const authAPI = {
    // Register new user
    register: (userData) => {
        return api.post("/auth/register", userData);
    },

    // Login user
    login: (credentials) => {
        // form data for auth2
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);

        return axios.post(`${baseURL}/auth/login`, formData);
    },

    // Get current user
    getCurrentUser: () => {
        return api.get('/auth/me');
    } 
};

// Members API

export const membersAPI = {
    // Get all members
    getMembers: (params = {}) => {
        return api.get('/members/', { params });
    },

    // Get member by ID
    getMember: (id) => {
        return api.get(`/members/${id}`);
    },

    // Create a member
    createMember: (memberData) => {
        return api.post('/members/', memberData);
    },

    // Update a member
    updateMember: (id, memberData) => {
        return api.put(`/members/${id}`, memberData);
    },

    // Delete a member
    deleteMember: (id) => {
        return api.delete(`/members/${id}`);
    }
};

// Borrowings API

export const borrowingsAPI = {
    // Get all borrowings
    getAllBorrowings: () => {
        return api.get('/borrowings/history');
    },

    // Get current borrowings
    getCurrentBorrowings: () => {
        return api.get('/borrowings/');
    },

    // Get borrowings by Member
    getBorrowingsByMember: (memberId) => {
        return api.get(`/borrowings/members/${memberId}`);
    },

    // Borrow a book
    borrowBook: (borrowData) => {
        return api.post('/borrowings/borrow', borrowData);
    },

    // Return a book
    returnBook: (returnData) => {
        return api.put('/borrowings/return', returnData);
    }
};