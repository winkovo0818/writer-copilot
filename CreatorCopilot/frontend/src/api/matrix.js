import http from './client'

export const matrixApi = {
  list: (params) => http.get('/matrix', { params }),
  get: (matrixId) => http.get(`/matrix/${matrixId}`),
  create: (params) => http.post('/matrix', {}, { params }),
  plan: (body) => http.post('/matrix/plan', body),
  schedule: (matrixId) => http.get(`/matrix/${matrixId}/schedule`),
}
