import http from './client'

export const graphApi = {
  listConcepts: (params) => http.get('/graph/concepts', { params }),
  getContext: (params) => http.get('/graph/context', { params }),
  getGaps: (params) => http.get('/graph/gaps', { params }),
  getRecommendations: (params) => http.get('/graph/recommendations', { params }),
}
