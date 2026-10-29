import { useEffect, useRef, useState, type FormEvent } from 'react'
import { ask, listDocuments, uploadDocument, type DocumentSummary, type Source } from './api'

type Message = { role: 'user' | 'assistant'; content: string; sources?: Source[] }

export default function App() {
  const [documents, setDocuments] = useState<DocumentSummary[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [question, setQuestion] = useState('')
  const [k, setK] = useState(5)
  const [uploading, setUploading] = useState(false)
  const [asking, setAsking] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInput = useRef<HTMLInputElement>(null)
  const bottom = useRef<HTMLDivElement>(null)

  const refreshDocuments = () => listDocuments().then(setDocuments).catch((e) => setError(e.message))

  useEffect(() => {
    refreshDocuments()
  }, [])

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, asking])

  async function handleUpload(file: File) {
    setUploading(true)
    setError(null)
    try {
      await uploadDocument(file)
      await refreshDocuments()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setUploading(false)
      if (fileInput.current) fileInput.current.value = ''
    }
  }

  async function handleAsk(event: FormEvent) {
    event.preventDefault()
    const text = question.trim()
    if (!text || asking) return
    setQuestion('')
    setError(null)
    setMessages((m) => [...m, { role: 'user', content: text }])
    setAsking(true)
    try {
      const result = await ask(text, k)
      setMessages((m) => [...m, { role: 'assistant', content: result.answer, sources: result.sources }])
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setAsking(false)
    }
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>DocChat</h1>
        <p className="muted">Ask questions about your PDFs. Answers cite their pages.</p>

        <label className="upload">
          {uploading ? 'Chunking and embedding…' : 'Upload a PDF'}
          <input
            ref={fileInput}
            type="file"
            accept="application/pdf"
            disabled={uploading}
            onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
          />
        </label>

        <h2>Documents</h2>
        {documents.length === 0 && <p className="muted">None yet.</p>}
        <ul className="documents">
          {documents.map((doc) => (
            <li key={doc.id}>
              <span>{doc.filename}</span>
              <span className="muted">{doc.chunks} chunks</span>
            </li>
          ))}
        </ul>

        <label className="slider">
          Chunks to retrieve (k): <strong>{k}</strong>
          <input type="range" min={1} max={10} value={k} onChange={(e) => setK(Number(e.target.value))} />
        </label>
      </aside>

      <main className="chat">
        <div className="messages">
          {messages.length === 0 && <p className="empty muted">Upload a PDF, then ask a question.</p>}
          {messages.map((message, i) => (
            <div key={i} className={`message ${message.role}`}>
              <p>{message.content}</p>
              {message.sources && (
                <div className="sources">
                  {message.sources.map((s, j) => (
                    <span key={j} className="source">
                      {s.filename} p.{s.page} · {s.similarity}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {asking && <div className="message assistant muted">Searching…</div>}
          {error && <div className="error">{error}</div>}
          <div ref={bottom} />
        </div>

        <form className="composer" onSubmit={handleAsk}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your documents"
          />
          <button type="submit" disabled={asking || !question.trim()}>
            Ask
          </button>
        </form>
      </main>
    </div>
  )
}
