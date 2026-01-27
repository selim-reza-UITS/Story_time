# Cyndi Story Telling Project 🦉✨

Cyndi is an interactive story-telling platform designed for students. It features an AI-powered "Owlbert" assistant that helps students write, correct grammar, and learn new words.

## Features
- **AI Owlbert Chat**: Real-time conversational AI for students.
- **Story Editor**: Hierarchy-based editing (Students edit their own, Teachers/Admins edit any).
- **Grammar Helper**: Instant grammar checking and suggestions.
- **Vocabulary Builder**: Learn and save new words with TTS pronunciation.
- **Absolute Media URLs**: Seamless frontend integration for images and audio.

---

## Technical Stack
- **Backend**: Django (REST Framework)
- **AI Helper**: FastAPI + LangChain + OpenAI
- **Text-to-Speech**: Pocket TTS
- **Database**: PostgreSQL
- **Cache**: Redis
- **DevOps**: Docker & Makefile

---

## Quick Start Guide

### 1. Prerequisites
Ensure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- **Make** (standard on Linux/Mac)

### 2. Environment Setup
The project uses a centralized `.env` file at the root.

1. Ensure the root `.env` exists and contains your `OPENAI_API_KEY`.
   ```env
   # Root .env
   OPENAI_API_KEY=your_openai_api_key
   ```

### 3. Launch the Project
Run the following commands to get everything up and running:

```bash
# 1. Build and start all services (Backend, AI, DB, Redis)
make up

# 2. Populate the database with demo students, teachers, and stories
make seed
```

Once running, you can access:
- **Backend API**: `http://localhost:9900`
- **AI Helper API**: `http://localhost:9901`

---

## Common Development Commands

The project includes a comprehensive `Makefile` to simplify all common tasks:

| Command | Description |
| :--- | :--- |
| `make up` | Start all services in the background |
| `make down` | Stop all services |
| `make seed` | Populate DB with demo data (Students, Teachers, Stories) |
| `make logs` | View live logs from all containers |
| `make build` | Rebuild Docker images |
| `make migrate` | Run Django migrations manually |
| `make shell` | Open Django interactive shell |
| `make status` | Check service health and port mappings |
| `make clean-all` | Full cleanup of containers, volumes, and images |

Run `make help` to see a full list of available commands.

---

## API Documentation
Detailed API endpoints and request/response structures can be found in:
- [API_ENDPOINTS.md](file:///home/reza/Code/Cyndi_Story_Telling/API_ENDPOINTS.md)
- [FRONTEND_API_FLOW.md](file:///home/reza/Code/Cyndi_Story_Telling/FRONTEND_API_FLOW.md)

Happy Storytelling! 🦉✨
