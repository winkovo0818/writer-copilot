/**
 * 解析 fetch 返回的 text/event-stream 响应体
 * @param {ReadableStream<Uint8Array>} body
 * @param {(event: string, data: unknown) => void} onEvent
 */
export async function readEventStream(body, onEvent) {
  const reader = body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const chunks = buffer.split('\n\n')
    buffer = chunks.pop() ?? ''
    for (const chunk of chunks) {
      if (!chunk.trim()) continue
      let eventName = 'message'
      const dataLines = []
      for (const line of chunk.split('\n')) {
        if (line.startsWith('event:')) {
          eventName = line.slice(6).trim()
        } else if (line.startsWith('data:')) {
          dataLines.push(line.slice(5).trimStart())
        }
      }
      const raw = dataLines.join('\n')
      if (!raw) continue
      let parsed
      try {
        parsed = JSON.parse(raw)
      } catch {
        parsed = raw
      }
      onEvent(eventName, parsed)
    }
  }
}
