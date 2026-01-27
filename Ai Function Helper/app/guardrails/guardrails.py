class Guardrails:
    def validate_response(self, text: str) -> str:
        """
        Validates and sanitizes the LLM response.
        Enforces safety rules or formatting constraints.
        """
        if not text:
            return "Thinking..."
        
        # Example guardrail: Block restricted keywords (mock implementation)
        restricted_words = ["<unsafe_content>"]
        for word in restricted_words:
            if word in text:
                return "I cannot talk about that."
        
        return text
