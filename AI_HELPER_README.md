# Cindy - Voice Chat Assistant

Cindy is a modular voice-enabled chat application designed with a layered architecture.

## API Endpoints

The application provides three distinct API endpoints as per the requirements:

### 1. Chat (`/chat`)
- **Purpose**: General conversational interface.
- **Input**: User message, conversation history, optional context.
- **Output**: Text response and optional audio speech of the response.
- **Method**: `POST`

### 2. Learn (`/learn`)
- **Purpose**: Pronunciation and Word Description.
- **Input**: A specific word.
- **Output**: Description/definition of the word and TTS audio pronunciation.
- **Method**: `POST`

### 3. Grammar Correction (`/grammar`)
- **Purpose**: Grammar checking and correction.
- **Input**: Text block.
- **Output**: Grammatically corrected text.
- **Method**: `POST`

## Project Structure
- `app/`: Main application code.
- `app/domain/`: Business logic and core domain services.
- `app/infrastructure/`: External service clients (LLM, TTS).
- `app/application/`: Orchestration and application flow.
- `app/models/`: Data transfer objects (Pydantic schemas).
- `app/output/`: Response formatting. (Legacy/Utility).

## Running the App
```bash
uvicorn app.main:app --reload
```
