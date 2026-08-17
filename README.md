# AI Package Damage Detection Agent

An AI-powered package inspection system that combines Computer Vision, LLM Agents, Voice AI, and LLM Observability to detect package damage and allow users to interact with prediction data through natural language or voice commands.

The system provides a custom React dashboard for package inspection, prediction history, statistics, and an intelligent assistant capable of calling backend tools and retrieving real system data.

---

## Features

### Package Damage Detection

- Upload package images through the web interface.
- Computer Vision model automatically classifies the package condition.
- Displays the predicted class and confidence score.
- Stores prediction results in PostgreSQL.
- Provides prediction history and statistics.

### LLM Agent

The system includes an LLM-powered agent capable of understanding user requests and deciding when backend tools are required.

Example:

```text
User: What model is deployed?

Agent
 |
 v
get_model_info()
 |
 v
Backend API
 |
 v
Real model information
 |
 v
Agent Response
```

The agent uses an OpenAI-compatible API and is configured to work with Groq.

### Tool Calling

The agent can interact with real backend data instead of generating unsupported answers.

The available tools allow the agent to retrieve information such as:

- Deployed model information.
- Prediction history.
- Prediction statistics.
- Package inspection data.

Tool failures are returned explicitly to the agent to prevent fabricated results.

### Voice Agent

The assistant supports voice commands using Groq Whisper with the `whisper-large-v3-turbo` model.

Voice workflow:

```text
Microphone
 |
 v
Browser MediaRecorder
 |
 v
Audio Recording
 |
 v
FastAPI
 |
 v
Whisper Large V3 Turbo
 |
 v
Transcription
 |
 v
LLM Agent
 |
 v
Tool Calling
 |
 v
Response
```

Voice commands are automatically transcribed and sent directly to the agent.

The voice interface also supports multilingual speech input, including Arabic.

### LLM Monitoring with Langfuse

Langfuse is integrated for LLM observability and agent monitoring.

It provides tracing for:

- Agent executions.
- LLM generations.
- Tool calls.
- Agent inputs and outputs.
- Execution latency.
- Agent workflow debugging.

Example trace:

```text
package-damage-agent
|
|-- OpenAI-generation
|
|-- get_model_info [TOOL]
|
`-- OpenAI-generation
```

This makes it possible to inspect how the agent processes a request and which tools are used to generate the final response.

---

## System Architecture

```text
 User
 |
 +-----------+-----------+
 | |
 Text Input Voice Input
 | |
 | MediaRecorder
 | |
 | Groq Whisper
 | |
 +-----------+-----------+
 |
 v
 LLM Agent
 |
 Tool Selection
 |
 v
 FastAPI API
 / \
 / \
 CV Model PostgreSQL
 \ /
 \ /
 Response
 |
 v
 React UI

 Langfuse
 |
 Agent Observability
```

---

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS
- Browser MediaRecorder API

### Backend

- FastAPI
- Python
- Uvicorn

### Computer Vision

- MobileNetV3 Small
- keras

### LLM and Agent

- Groq
- OpenAI-compatible API
- Tool Calling

### Voice AI

- Groq Whisper
- `whisper-large-v3-turbo`
- Browser MediaRecorder

### Database

- PostgreSQL

### LLM Observability

- Langfuse

### Deployment

- Docker
- Docker Compose
- WSL

---

## Project Structure

```text
computer-vision-agent/
|
|-- agent/
| |-- agent.py
| |-- prompts.py
| `-- tools.py
|
|-- backend/
| `-- app/
| |-- main.py
| |-- models.py
| `-- ...
|
|-- frontend/
| |-- public/
| `-- src/
| |-- ChatPopup.jsx
| |-- api.js
| `-- ...
|
|-- compose.yaml
|-- pyproject.toml
|-- uv.lock
|-- .env.example
`-- README.md
```
## Running the Project

### Docker Compose

From the project root:

```bash
docker compose up -d --build
```

Check the running services:

```bash
docker compose ps
```

The application services are available locally through Docker.

Frontend:

```text
http://localhost:3000
```

Backend API:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

### Stop the Application

```bash
docker compose down
```

## Monitoring

Agent activity can be monitored through Langfuse.

A typical agent trace contains:

```text
package-damage-agent
|
|-- LLM Generation
| |
| `-- Tool decision
|
|-- Tool
| |
| `-- Backend result
|
`-- LLM Generation
 |
 `-- Final response
```

This provides visibility into the complete agent execution workflow.

---

## Security

- API keys are stored using environment variables.
- `.env` should never be committed to Git.
- Tool results are grounded in backend responses.
- Tool failures are returned explicitly instead of fabricating data.
- Langfuse is used to monitor and debug LLM execution.

---

## Local Deployment

The project supports local deployment using WSL and Docker Compose.

```bash
docker compose up -d
```

This starts the frontend, backend, and PostgreSQL services as Docker containers.

The complete application can then be accessed through:

```text
http://localhost:3000
```
