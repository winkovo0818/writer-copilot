import http from './client'

export const knowledgeApi = {
  listArticles: (params) => http.get('/knowledge/articles', { params }),
  search: (params) => http.get('/knowledge/search', { params }),
  checkDuplication: (params) => http.get('/knowledge/check-duplication', { params }),
  /** 后端为 query 参数形式的 POST */
  importArticle: (params) => http.post('/knowledge/articles', {}, { params }),
}
