import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE || '/api/v1'

export const http = axios.create({
  baseURL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
})

http.interceptors.response.use(
  (res) => {
    const body = res.data
    if (body && typeof body.code === 'number' && body.code !== 0) {
      return Promise.reject(new Error(body.message || `错误码 ${body.code}`))
    }
    if (body && 'data' in body) {
      return { ...res, data: body.data }
    }
    return res
  },
  (err) => {
    const msg = err.response?.data?.message || err.message || '网络错误'
    return Promise.reject(new Error(msg))
  },
)

export default http
