export type DocumentSummary = {
  id: number
  filename: string
  created_at: string
  chunks: number
}

export type Source = {
  filename: string
  page: number
  similarity: number
}

export type AskResponse = {
  answer: string
  sources: Source[]
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, init)
  if (!response.ok) throw new Error(await response.text())
  return response.json()
}

export const listDocuments = () => request<DocumentSummary[]>('/documents')

export function uploadDocument(file: File) {
  const body = new FormData()
  body.append('file', file)
  return request<{ document_id: number }>('/documents', { method: 'POST', body })
}

export const ask = (question: string, k: number) =>
  request<AskResponse>('/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, k }),
  })
