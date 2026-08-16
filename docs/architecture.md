# Architecture — Package Damage Detection

TODO: draw the system diagram here (spec §45 workflow). Suggested Mermaid:

```mermaid
flowchart LR
    U[User] --> F[React Frontend :3000]
    U --> W[Open WebUI :8080]
    F -->|REST /api/v1| B[FastAPI :8000]
    W -->|Tool Calls| B
    B --> M[CV Model model.pt]
    B --> P[(PostgreSQL :5432)]
    B --> A[Agent Tools]
    A --> M
    A --> P
```

## Components
| Component | Tech | Role |
|---|---|---|
| Frontend | React + Vite (nginx) | upload, preview, results, history, dashboard |
| Backend | FastAPI + uvicorn | REST API, validation, error handling |
| Model service | PyTorch (torchvision) | load model once, preprocess, predict |
| Database | PostgreSQL 16 | persist predictions |
| Agent | LLM (tool calling) | answer questions with real data |
| Chat UI | Open WebUI | chat + (optional) voice |
| Orchestration | Docker Compose | multi-service runtime |
| Deployment | Dokploy | public production hosting |

## Key decisions to document (spec §50 prep)
- Model loaded once at startup, not per request.
- Containers use Docker service names (postgres:5432), never localhost.
- Backend image builds from repo root (pyproject.toml + uv.lock are at root).
- Predictions are written only after a successful inference.
