import http from './client'

export const styleApi = {
  snapshot: (articleId) => http.get(`/style/snapshot/${articleId}`),
  report: (period) => http.get('/style/report', { params: { period } }),
  driftAlerts: () => http.get('/style/drift-alerts'),
  baseline: (body) => http.post('/style/baseline', body),
}
