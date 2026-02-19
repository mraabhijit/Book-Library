import axios from 'axios';

const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:80/api';

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
        const token = typeof window !== 'undefined' ? localStorage.getItem('authToken') : null;
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
    getBook: (id: number) => {
        return api.get(`/books/${id}`);
    },

    // create book
    createBook: (bookData: any) => {
        return api.post('/books/', bookData);
    },

    // update a book
    updateBook: (id: number, bookData: any) => {
        return api.put(`/books/${id}`, bookData);
    },

    // delete a book
    deleteBook: (id: number) => {
        return api.delete(`/books/${id}`);
    }
};

// Authentication API
export const authAPI = {
    // Register new user
    register: (userData: any) => {
        return api.post("/auth/register", userData);
    },

    // Login user
    login: (credentials: { username: string; password: string }) => {
        // form data for oauth2
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
    getMember: (id: number) => {
        return api.get(`/members/${id}`);
    },

    // Create a member
    createMember: (memberData: any) => {
        return api.post('/members/', memberData);
    },

    // Update a member
    updateMember: (id: number, memberData: any) => {
        return api.put(`/members/${id}`, memberData);
    },

    // Delete a member
    deleteMember: (id: number) => {
        return api.delete(`/members/${id}`);
    }
};

// Borrowings API
export const borrowingsAPI = {
    // Get all borrowings
    getAllBorrowings: (params = {}) => {
        return api.get('/borrowings/history', { params });
    },

    // Get current borrowings
    getCurrentBorrowings: (params = {}) => {
        return api.get('/borrowings/', { params });
    },

    // Get borrowings by Member
    getBorrowingsByMember: (memberId: number, params = {}) => {
        return api.get(`/borrowings/members/${memberId}`, { params });
    },

    // Borrow a book
    borrowBook: (borrowData: any) => {
        return api.post('/borrowings/borrow', borrowData);
    },

    // Return a book
    returnBook: (returnData: any) => {
        return api.put('/borrowings/return', returnData);
    }
};
