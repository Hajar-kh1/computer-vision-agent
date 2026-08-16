# Package Damage Detection
## Computer Vision Agent

A production-oriented AI application for package image classification.

## Overview

The application allows users to upload package images and receive classification results through a web interface.

Prediction results are stored in PostgreSQL and can later be viewed through the prediction history and dashboard.

The system also includes an AI assistant through Open WebUI, enabling natural-language interaction with application capabilities and stored prediction data.

### Main Features

- Image upload and preview
- Package image classification
- Prediction confidence scores
- Top predictions
- Inference latency
- Prediction history
- Prediction statistics dashboard
- PostgreSQL persistence
- FastAPI REST API
- React web frontend
- AI assistant integration
- Open WebUI
- Docker containerization
- Docker Compose orchestration

---

## System Architecture

```text
                       User
                        │
          ┌─────────────┴─────────────┐
          │                           │
          ▼                           ▼
   React Frontend                Open WebUI
          │                           │
          │ REST API                 │ AI Assistant
          │                           │ Tool Calls
          └─────────────┬─────────────┘
                        │
                        ▼
                    FastAPI
                   Application
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
       Computer Vision         PostgreSQL
           Model               Database
```

The frontend communicates with the FastAPI backend through REST endpoints.

FastAPI handles model inference, application logic, database access, and tool functionality used by the AI assistant.

---

## Technology Stack

| Component | Technology |
|---|---|
| Computer Vision | PyTorch / Image Processing |
| Backend | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Frontend | React + Vite |
| AI Assistant | Tool-calling LLM |
| Chat Interface | Open WebUI |
| Python Environment | uv |
| API Documentation | Swagger / OpenAPI |
| Containerization | Docker |
| Orchestration | Docker Compose |
| Version Control | Git + GitHub |

---

## Repository Structure

```text
computer-vision-agent/
│
├── agent/
│   └── AI agent logic and tools
│
├── backend/
│   └── FastAPI application and database integration
│
├── data/
│   └── Dataset files and documentation
│
├── deployment/
│   └── Deployment configuration
│
├── docs/
│   └── Architecture and API documentation
│
├── frontend/
│   └── React + Vite web application
│
├── models/
│   └── Trained model artifacts
│
├── openwebui/
│   └── Open WebUI integration
│
├── reports/
│   └── Model metrics and evaluation outputs
│
├── tests/
│   └── Application tests
│
├── training/
│   └── Model training and evaluation pipeline
│
├── compose.yaml
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
```

---

## Application Workflow

```text
Image Upload
     ↓
Frontend
     ↓
FastAPI
     ↓
Image Validation & Preprocessing
     ↓
Computer Vision Model
     ↓
Prediction
     ↓
PostgreSQL
     ↓
Frontend Result / History / Dashboard
```

The prediction response includes information such as:

- Predicted class
- Confidence
- Top predictions
- Inference latency
- Model version

---

## API

The backend exposes REST endpoints through FastAPI.

### Main Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check system health |
| POST | `/api/v1/predict` | Classify an image |
| GET | `/api/v1/predictions` | Retrieve prediction history |
| GET | `/api/v1/predictions/{id}` | Retrieve a specific prediction |
| GET | `/api/v1/stats` | Retrieve prediction statistics |
| GET | `/api/v1/model` | Retrieve deployed model information |
| POST | `/api/v1/chat` | AI assistant endpoint |

Swagger documentation is available when the backend is running:

```text
http://localhost:8000/docs
```

---

## Frontend

The React frontend provides three main views.

### Classify

Upload and preview an image, run classification, and view the prediction result.

### History

View previous predictions stored in PostgreSQL.

### Dashboard

View prediction statistics including total predictions, average confidence, and class distribution.

---

## AI Assistant

The project includes an AI assistant capable of interacting with the deployed system.

Instead of relying only on language-model knowledge, the assistant can use application tools to retrieve real system data.

Example requests:

```text
What is the average prediction confidence?
```

Open WebUI provides the conversational interface for this functionality.

---

## Open WebUI

Open WebUI runs as part of the Docker Compose stack and provides the chat interface for the AI assistant.

Local address:

```text
http://localhost:8080
```

LLM credentials and provider configuration are supplied through environment variables.

API keys and other secrets should never be committed to Git.

---

## Local Setup

### Requirements

Install:

- Python
- uv
- Node.js
- Docker Desktop
- Git

Clone the repository:

```bash
git clone <repository-url>
cd computer-vision-agent
```

Install Python dependencies:

```bash
uv sync
```

---

## Running the Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

The development frontend is available at:

```text
http://localhost:5173
```

---

## Running with Docker Compose

Build and start the complete application:

```bash
docker compose up --build
```

Or run it in the background:

```bash
docker compose up -d
```

Check running services:

```bash
docker compose ps
```

Stop the application:

```bash
docker compose down
```

### Local Services

| Service | Address |
|---|---|
| Frontend | `http://localhost:3000` |
| Backend | `http://localhost:8000` |
| Swagger | `http://localhost:8000/docs` |
| Open WebUI | `http://localhost:8080` |
| PostgreSQL | Docker service |

---

## Environment Configuration

Copy the environment template:

```bash
cp .env.example .env
```

Environment variables are used for:

- PostgreSQL configuration
- Database connection
- Model configuration
- LLM provider configuration
- Application settings


---

## Database Persistence

Prediction history is stored using PostgreSQL with a persistent Docker volume.

The containers can be restarted without removing stored prediction records:

```bash
docker compose down
docker compose up -d
```

Avoid using:

```bash
docker compose down -v
```

unless the database volume should intentionally be deleted.

---

## Testing

The project contains automated tests for the main application components.

Tests cover areas such as:

- Health checks
- Model loading
- Prediction requests
- Invalid image handling
- Database insertion
- Prediction history
- Agent functionality

Run tests using:

```bash
uv run pytest
```

---

## Docker Services

The production stack contains the main services:

```text
frontend
backend
postgres
open-webui
```

The services communicate through the Docker Compose network.

---

The application follows basic production practices:

- Secrets are stored outside Git
- Uploaded files are validated
- Environment variables are used for configuration
- PostgreSQL data is persisted using Docker volumes
- API errors are handled by the backend
- Production credentials should be different from development credentials

## Team Collaboration

The project is divided across four engineering areas:

| Role | Responsibility |
|---|---|
| Computer Vision | Dataset, training, evaluation, model |
| Backend & Database | FastAPI, PostgreSQL, APIs |
| Agentic AI | LLM, tools, Open WebUI |
| Frontend & DevOps | React, Docker, Compose, deployment |

Feature branches are used to support parallel development and integration.

---

## Project Goal

The project demonstrates the complete AI engineering workflow:

```text
Data
 ↓
Model
 ↓
Inference
 ↓
FastAPI
 ↓
PostgreSQL
 ↓
Agent Tools
 ↓
Open WebUI
 ↓
Frontend
 ↓
Docker
 ↓
Deployment
```
