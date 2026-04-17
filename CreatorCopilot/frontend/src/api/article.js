import http from './client'

const baseURL = import.meta.env.VITE_API_BASE || '/api/v1'

/**
 * POST /article/stream — SSE，使用 fetch（非 axios）
 */
export function streamArticle({ topic, imageSource = 'random', signal }) {
  const qs = new URLSearchParams({
    topic,
    image_source: imageSource,
  })
  return fetch(`${baseURL}/article/stream?${qs}`, {
    method: 'POST',
    signal,
    headers: { Accept: 'text/event-stream' },
  })
}

export function streamConfirmTitle({ taskId, selectedId, editedTitle, signal }) {
  const qs = new URLSearchParams({ task_id: taskId })
  if (selectedId != null) qs.set('selected_id', String(selectedId))
  if (editedTitle) qs.set('edited_title', editedTitle)
  return fetch(`${baseURL}/article/confirm-title?${qs}`, {
    method: 'POST',
    signal,
    headers: { Accept: 'text/event-stream' },
  })
}

export function streamConfirmOutline({ taskId, editedOutline, signal }) {
  const qs = new URLSearchParams({ task_id: taskId })
  const body =
    editedOutline != null ? { edited_outline: editedOutline } : {}
  return fetch(`${baseURL}/article/confirm-outline?${qs}`, {
    method: 'POST',
    signal,
    headers: {
      Accept: 'text/event-stream',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })
}

export const articleApi = {
  cancel: (taskId) => http.post('/article/cancel', {}, { params: { task_id: taskId } }),
  getTask: (taskId) => http.get(`/task/${taskId}`),
}
