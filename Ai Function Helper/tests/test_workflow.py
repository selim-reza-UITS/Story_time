import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock external dependencies to allow tests to run without installing them
sys.modules["langchain_openai"] = MagicMock()
sys.modules["langchain_core.messages"] = MagicMock()
sys.modules["dotenv"] = MagicMock()
sys.modules["pocket_tts"] = MagicMock()
sys.modules["scipy"] = MagicMock()
sys.modules["scipy.io"] = MagicMock()
sys.modules["scipy.io.wavfile"] = MagicMock()
sys.modules["torch"] = MagicMock()

from app.models.schemas import ChatRequest, ChatResponse
from app.application.orchestrator import Orchestrator

# Mock the external services to avoid actual API calls during tests
# We must patch where the class is USED, not where it is defined, 
# because Orchestrator imports it directly.
@patch("app.application.orchestrator.LLMClient")
@patch("app.application.orchestrator.TTSClient")
def test_full_workflow(MockTTS, MockLLM):
    # Setup Mocks
    mock_llm_instance = MockLLM.return_value
    mock_llm_instance.generate_chat_response.return_value = "Hello user!"
    mock_llm_instance.generate_description.return_value = "A greeting."
    
    mock_tts_instance = MockTTS.return_value
    mock_tts_instance.text_to_speech.return_value = b"fake_audio_bytes"

    # Initialize Orchestrator (it will use the mocked classes because of patch)
    orchestrator = Orchestrator()
    
    # Define Request
    request = ChatRequest(
        word="Hello",
        conversation_history=["User: Hi"]
    )
    
    # Execute Flow
    response = orchestrator.process_request(request)
    
    # Verify Orchestrator Logic
    assert isinstance(response, ChatResponse)
    assert response.chat_response == "Hello user!"
    assert response.description == "A greeting."
    assert response.speech_output == b"fake_audio_bytes"
    
    # Verify Infrastructure interactions
    mock_llm_instance.generate_chat_response.assert_called_once()
    mock_tts_instance.text_to_speech.assert_called_once_with("Hello user!")
    mock_llm_instance.generate_description.assert_called_once()     
