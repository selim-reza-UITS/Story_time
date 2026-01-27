from pydantic import BaseModel, Field
from typing import Optional, List

# --- Chat Models ---
class ChatRequest(BaseModel):
    message: str = Field(..., description="User input message for the chatbot")
    conversation_history: List[str] = Field(default_factory=list, description="List of previous messages")
    context: Optional[str] = Field(None, description="Optional conversation context")

class ChatResponse(BaseModel):
    chat_response: str = Field(..., description="The text response from the chatbot")
    # Chat might still optionally return audio if it's a voice assistant, 
    # but based on the request separation, we'll keep it simple or strictly follow the split.
    # We will keep speech_output optional here for the 'Voice Chat' aspect, 
    # but the distinct pronunciation API will be separate.
    speech_output: Optional[str] = Field(None, description="Base64 encoded audio of the response")

# --- Learn Models (Pronunciation + Description) ---
class LearnRequest(BaseModel):
    word: str = Field(..., description="Word to describe and pronounce")

class LearnResponse(BaseModel):
    description: str = Field(..., description="Explanation/Definition of the word")
    pronunciation_audio: Optional[str] = Field(None, description="Base64 encoded audio pronunciation of the word")

# --- Grammar Models ---
class GrammarRequest(BaseModel):
    text: str = Field(..., description="Text to check/correct")

class GrammarResponse(BaseModel):
    corrected_text: str = Field(..., description="Grammatically corrected text")

# --- Configuration Models ---
class AssistantConfig(BaseModel):
    name: str = Field(..., description="Name of the AI Assistant")
    behavior_settings: str = Field(..., description="System prompt or behavior description")
