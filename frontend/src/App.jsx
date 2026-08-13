// Frontend root component — three required views (spec §22).
//
// View 1 — Classify: drag-and-drop / file upload, image preview, Classify
//                    button, loading indicator, predicted class, confidence,
//                    top-K predictions, inference latency.
// View 2 — History:  prediction id, image name, predicted class, confidence,
//                    date/time (from GET /api/v1/predictions).
// View 3 — Dashboard: total predictions, class distribution, average
//                     confidence (from GET /api/v1/stats).
//
// Required UX (spec §23): loading states, readable errors, responsive layout,
// clear confidence values, image preview, backend status indicator.

import { useState } from 'react'

// TODO (Student 4): implement the three views. Suggested structure:
//   - <ClassifyView />  -> upload + result card
//   - <HistoryView />   -> table of predictions
//   - <DashboardView /> -> stats cards + class distribution
//   - simple tab navigation between the three
//   - a small "backend status" pill fed by GET /health
export default function App() {
  const [view, setView] = useState('classify')

  return (
    <div>
      <h1>Package Damage Detection</h1>
      <nav>
        <button onClick={() => setView('classify')}>Classify</button>
        <button onClick={() => setView('history')}>History</button>
        <button onClick={() => setView('dashboard')}>Dashboard</button>
      </nav>
      {/* TODO: render the active view */}
      <p>Select a view. (Stub — implement in src/components/*)</p>
    </div>
  )
}
