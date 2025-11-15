import axios from 'axios'

// Use environment variable for API base URL, fallback to localhost for development
const API_BASE_URL = (import.meta as any).env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Increased timeout for serverless functions
})

// Request interceptor
api.interceptors.request.use(
  (config: any) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.baseURL}${config.url}`)
    
    // Add API prefix for Netlify functions
    if (API_BASE_URL.includes('netlify')) {
      config.url = `/api${config.url}`
    }
    
    return config
  },
  (error: any) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response: any) => {
    console.log('API Response:', response.status, response.data)
    return response
  },
  (error: any) => {
    console.error('API Error:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
      url: error.config?.url
    })
    return Promise.reject(error)
  }
)

// Brand API
export const brandApi = {
  getAll: () => api.get('/brands/'),
  getById: (id: number) => api.get(`/brands/${id}`),
  create: (brand: { name: string; keywords?: string[]; alert_threshold?: number; sentiment_threshold?: number }) =>
    api.post('/brands/add', brand),
  update: (id: number, brand: any) => api.put(`/brands/${id}`, brand),
  delete: (id: number) => api.delete(`/brands/${id}`),
  getStats: (id: number) => api.get(`/brands/${id}/stats`),
}

// Mentions API
export const mentionsApi = {
  getByBrand: (brandId: number, params?: { limit?: number; offset?: number; source?: string; sentiment?: string; hours?: number }) =>
    api.get(`/mentions/${brandId}`, { params }),
  getTimeline: (brandId: number, params?: { hours?: number; interval?: string }) =>
    api.get(`/mentions/${brandId}/timeline`, { params }),
  getSources: (brandId: number, params?: { hours?: number }) =>
    api.get(`/mentions/${brandId}/sources`, { params }),
  getTrending: (brandId: number, params?: { limit?: number; hours?: number }) =>
    api.get(`/mentions/${brandId}/trending`, { params }),
}

// Sentiment API
export const sentimentApi = {
  getAnalysis: (brandId: number, params?: { hours?: number }) =>
    api.get(`/sentiment/${brandId}/analysis`, { params }),
  getNegative: (brandId: number, params?: { limit?: number; hours?: number; threshold?: number }) =>
    api.get(`/sentiment/${brandId}/negative`, { params }),
  getComparison: (brandId: number, params?: { current_hours?: number; previous_hours?: number }) =>
    api.get(`/sentiment/${brandId}/comparison`, { params }),
}

// Alerts API
export const alertsApi = {
  getByBrand: (brandId: number, params?: { limit?: number; severity?: string; unread_only?: boolean }) =>
    api.get(`/alerts/${brandId}`, { params }),
  markRead: (alertId: number) => api.put(`/alerts/${alertId}/read`),
  resolve: (alertId: number) => api.put(`/alerts/${alertId}/resolve`),
  getSummary: (brandId: number) => api.get(`/alerts/${brandId}/summary`),
  createTest: (brandId: number) => api.post(`/alerts/${brandId}/test`),
}

export default api