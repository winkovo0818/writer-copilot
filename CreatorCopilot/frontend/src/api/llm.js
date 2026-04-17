import http from './client'

export const llmApi = {
  /** GET /llm/monitoring — 监控面板聚合数据 */
  monitoring: () => http.get('/llm/monitoring'),
}
