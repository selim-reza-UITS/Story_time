# Cyndi Story Telling Project

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
- **DevOps**: Docker & Docker Compose

---

## Quick Start Guide

### 1. Prerequisites
Ensure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 2. Environment Setup
The project uses a centralized `.env` file at the root.

1. Create a `.env` file from the provided template or ensure it contains the following keys:
   ```env
   # Django Backend
   DJANGO_SECRET_KEY=your_secret_key
   DATABASE_URL=postgres://cyndi_user:cyndi_password@db:5432/cyndi_db
   REDIS_URL=redis://redis:6379/1
   
   # AI Helper
   OPENAI_API_KEY=your_openai_api_key
   ```
   *Note: The project already comes with a base `.env` for development.*

### 3. Run with Docker Compose
To start the entire ecosystem (Backend, AI Helper, DB, Redis):
```bash
docker-compose up --build
```
This will start:
- **Backend API**: `http://localhost:9900`
- **AI Helper API**: `http://localhost:9901`

### 4. Database Seed
To populate the database with demo students, teachers, and stories:
```bash
docker exec -it cyndi_backend python manage.py seed_data
```

---

## API Endpoints Summary

### Authentication
- `POST /api/v1/auth/login/`: User login.

### Story Editor (Hierarchical)
- `GET /api/v1/stories/editor/<id>/`: Fetch full story content.
- `POST /api/v1/stories/editor/`: Create new story (supports images).
- `PATCH /api/v1/stories/editor/<id>/`: Update story (supports images).
- `DELETE /api/v1/stories/editor/<id>/`: Delete story (Student: own, Teacher/Admin: all).

### Owlbert AI
- `POST /api/v1/stories/chat/owlbert/`: Chat with Owlbert.
- `POST /api/v1/stories/ai/realtime-check/`: Grammar/Spelling check.

---

## Troubleshooting
- **Owlbert not responding?**: Check if `OPENAI_API_KEY` is valid in the root `.env`.
- **Images not loading?**: Ensure the backend container is running; media is served via `http://<host>:9900/media/`.

Happy Storytelling! 🦉✨
