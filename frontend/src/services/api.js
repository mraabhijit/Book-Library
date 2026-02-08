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
        // const token = localStorage.getItem('token');
        // if (token) {
        //     config.headers.Authorization = `Bearer ${token}`
        // }
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