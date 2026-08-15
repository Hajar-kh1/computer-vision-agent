// API client — talks to the FastAPI backend (spec §15).
//
// Endpoints:
//   GET  /health
//   GET  /api/v1/model
//   POST /api/v1/predict          (multipart/form-data, image=<file>)
//   GET  /api/v1/predictions?limit=20
//   GET  /api/v1/predictions/{id}
//   GET  /api/v1/stats

// TODO (Student 4): implement and use these helpers in the views.

export async function health() {
  const res = await fetch('/health')
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`)
  return res.json()
}

export async function predict(imageFile) {
  const form = new FormData()
  form.append('image', imageFile)
  const res = await fetch('/api/v1/predict', { method: 'POST', body: form })
  if (!res.ok) throw new Error(`Prediction failed: ${res.status}`)
  return res.json()
}

export async function getPredictions(limit = 20) {
  const res = await fetch(`/api/v1/predictions?limit=${limit}`)
  if (!res.ok) throw new Error(`History failed: ${res.status}`)
  return res.json()
}

export async function getStats() {
  const res = await fetch('/api/v1/stats')
  if (!res.ok) throw new Error(`Stats failed: ${res.status}`)
  return res.json()
}

export async function getModelInfo() {
  const res = await fetch('/api/v1/model')
  if (!res.ok) throw new Error(`Model info failed: ${res.status}`)
  return res.json()
}

export async function chat(message) {
  const res = await fetch('/api/v1/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  })
  if (!res.ok) {
    let detail = `Chat failed: ${res.status}`
    try {
      const body = await res.json()
      if (body.detail) detail = body.detail
    } catch { /* keep default */ }
    throw new Error(detail)
  }
  return res.json()
}
