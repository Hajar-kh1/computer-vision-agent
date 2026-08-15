// TEMP frontend — for end-to-end testing only.
// Replace with Student 4's real implementation when delivered.
// Three views (spec §22): Classify, History, Dashboard + backend status pill.

import { useEffect, useState } from 'react'
import { health, predict, getPredictions, getStats } from './api.js'
import ChatPopup from './ChatPopup.jsx'

const pct = (x) => (x * 100).toFixed(1) + '%'
const fmtTime = (iso) => new Date(iso).toLocaleString()

// ---------------------------------------------------------------- status pill
function StatusPill() {
  const [status, setStatus] = useState('checking')
  const [label, setLabel] = useState('Checking backend…')

  useEffect(() => {
    let alive = true
    const check = async () => {
      try {
        const h = await health()
        if (!alive) return
        const ok = h.database === 'healthy' && h.model === 'loaded'
        setStatus(ok ? 'ok' : 'degraded')
        setLabel(ok ? 'Backend online' : `Backend: db=${h.database}, model=${h.model}`)
      } catch {
        if (!alive) return
        setStatus('down')
        setLabel('Backend offline')
      }
    }
    check()
    const timer = setInterval(check, 15000)
    return () => { alive = false; clearInterval(timer) }
  }, [])

  return <span className={`pill pill-${status}`}>{label}</span>
}

// --------------------------------------------------------------- ClassifyView
function ClassifyView() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const onPick = (e) => {
    const f = e.target.files && e.target.files[0]
    setFile(f || null)
    setResult(null)
    setError(null)
    if (f) setPreview(URL.createObjectURL(f))
  }

  const run = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      setResult(await predict(file))
    } catch (err) {
      setError(err.message || 'Prediction failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="view">
      <h2>Classify a package image</h2>
      <input type="file" accept="image/*" onChange={onPick} data-testid="file-input" />
      {preview && <img src={preview} alt="preview" className="preview" />}
      <button onClick={run} disabled={!file || loading}>
        {loading ? 'Classifying…' : 'Classify'}
      </button>
      {error && <p className="error">Error: {error}</p>}
      {result && (
        <div className="card">
          <p className="big">{result.predicted_class}</p>
          <p>Confidence: <strong>{pct(result.confidence)}</strong></p>
          <ul>
            {result.top_predictions.map((t) => (
              <li key={t.class_name}>{t.class_name}: {pct(t.probability)}</li>
            ))}
          </ul>
          <p className="muted">Latency {result.inference_ms} ms · model v{result.model_version}</p>
        </div>
      )}
    </section>
  )
}

// ---------------------------------------------------------------- HistoryView
function HistoryView() {
  const [rows, setRows] = useState(null)
  const [error, setError] = useState(null)

  const load = async () => {
    setError(null)
    try {
      setRows(await getPredictions(20))
    } catch (err) {
      setError(err.message || 'Could not load history')
    }
  }

  useEffect(() => { load() }, [])

  return (
    <section className="view">
      <h2>Prediction history</h2>
      <button onClick={load}>Refresh</button>
      {error && <p className="error">Error: {error}</p>}
      {rows && rows.items.length === 0 && <p>No predictions yet — classify an image first.</p>}
      {rows && rows.items.length > 0 && (
        <table>
          <thead>
            <tr><th>ID</th><th>Image</th><th>Class</th><th>Confidence</th><th>When</th></tr>
          </thead>
          <tbody>
            {rows.items.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.image_name}</td>
                <td>{r.predicted_class}</td>
                <td>{pct(r.confidence)}</td>
                <td>{fmtTime(r.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}

// ------------------------------------------------------------- DashboardView
function DashboardView() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)

  const load = async () => {
    setError(null)
    try {
      setStats(await getStats())
    } catch (err) {
      setError(err.message || 'Could not load stats')
    }
  }

  useEffect(() => { load() }, [])

  const dist = stats ? stats.class_distribution : {}
  const total = stats ? stats.total_predictions : 0
  const max = Math.max(1, ...Object.values(dist))

  return (
    <section className="view">
      <h2>Dashboard</h2>
      <button onClick={load}>Refresh</button>
      {error && <p className="error">Error: {error}</p>}
      {stats && total === 0 && <p>No predictions yet — classify an image first.</p>}
      {stats && total > 0 && (
        <>
          <div className="cards">
            <div className="stat"><span className="stat-num">{total}</span> total predictions</div>
            <div className="stat"><span className="stat-num">{stats.avg_confidence != null ? pct(stats.avg_confidence) : '—'}</span> avg confidence</div>
            <div className="stat"><span className="stat-num">{stats.avg_inference_ms != null ? stats.avg_inference_ms + ' ms' : '—'}</span> avg latency</div>
          </div>
          <h3>Class distribution</h3>
          {Object.entries(dist).map(([cls, count]) => (
            <div key={cls} className="bar-row">
              <span className="bar-label">{cls}</span>
              <div className="bar"><div className="bar-fill" style={{ width: `${(count / max) * 100}%` }} /></div>
              <span className="bar-count">{count}</span>
            </div>
          ))}
        </>
      )}
    </section>
  )
}

// ---------------------------------------------------------------------- App
export default function App() {
  const [view, setView] = useState('classify')

  return (
    <div className="app">
      <header>
        <h1>Package Damage Detection</h1>
        <StatusPill />
      </header>
      <nav>
        <button className={view === 'classify' ? 'active' : ''} onClick={() => setView('classify')}>Classify</button>
        <button className={view === 'history' ? 'active' : ''} onClick={() => setView('history')}>History</button>
        <button className={view === 'dashboard' ? 'active' : ''} onClick={() => setView('dashboard')}>Dashboard</button>
      </nav>
      {view === 'classify' && <ClassifyView />}
      {view === 'history' && <HistoryView />}
      {view === 'dashboard' && <DashboardView />}
      <ChatPopup />
    </div>
  )
}
