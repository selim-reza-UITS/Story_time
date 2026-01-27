from fastapi import FastAPI, HTTPException
from app.models.schemas import (
    ChatRequest, ChatResponse,
    LearnRequest, LearnResponse,
    GrammarRequest, GrammarResponse,
    AssistantConfig
)
from app.application.orchestrator import Orchestrator

app = FastAPI(title="Cindy - Voice Chat Assistant")

# Dependency Injection (Singleton for simplicity here)
orchestrator = Orchestrator()

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Chatbot endpoint. 
    Receives text message + history, returns conversational response (and optionally audio).
    """
    try:
        response = orchestrator.handle_chat_request(request)
        return response
    except Exception as e:
        print(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learn", response_model=LearnResponse)
def learn_endpoint(request: LearnRequest):
    """
    Pronunciation and Word Description endpoint.
    Receives a word, returns its description/definition and TTS pronunciation.
    """
    try:
        response = orchestrator.handle_learn_request(request)
        return response
    except Exception as e:
        print(f"Error processing learn request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/grammar", response_model=GrammarResponse)
def grammar_endpoint(request: GrammarRequest):
    """
    Grammar Correction endpoint.
    Receives text, returns the grammatically corrected version.
    """
    try:
        response = orchestrator.handle_grammar_request(request)
        return response
    except Exception as e:
        print(f"Error processing grammar request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# --- Settings Endpoints ---

@app.get("/settings/assistant", response_model=AssistantConfig)
async def get_assistant_settings():
    """
    Get current AI Assistant configuration.
    """
    try:
        return orchestrator.config_service.get_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/settings/assistant", response_model=AssistantConfig)
async def update_assistant_settings(config: AssistantConfig):
    """
    Update AI Assistant configuration.
    """
    try:
        orchestrator.config_service.save_config(config)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
