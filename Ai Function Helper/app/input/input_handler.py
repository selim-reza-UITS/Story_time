from app.models.schemas import ChatRequest

class InputHandler:
    @staticmethod
    def validate_request(data: dict) -> ChatRequest:
        """
        Validates input data and returns a ChatRequest model.
        FastAPI does this automatically if used as a router dependency,
        but this layer safeguards the entry point logic.
        """
        # Pydantic validation
        return ChatRequest(**data)
