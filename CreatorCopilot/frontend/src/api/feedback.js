import http from './client'

export const feedbackApi = {
  dashboard: () => http.get('/feedback/dashboard'),
  patterns: () => http.get('/feedback/patterns'),
  insights: (articleId) => http.get(`/feedback/insights/${articleId}`),
  metrics: (articleId) => http.get(`/metrics/${articleId}`),
}
