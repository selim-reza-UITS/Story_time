from app.models.schemas import ChatResponse
from typing import Optional

class ResponseFormatter:
    def format_response(self, text: str, description: str, audio: Optional[bytes]) -> ChatResponse:
        """
        Constructs the final ChatResponse object.
        """
        return ChatResponse(
            chat_response=text,
            description=description,
            speech_output=audio
        )
