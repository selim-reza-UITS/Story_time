from app.infrastructure.llm_client import LLMClient

class GrammarService:
    def __init__(self, llm_client: LLMClient = None):
        # We allow passing llm_client to avoid re-initializing it if shared, 
        # though Orchestrator passes it.
        self.llm_client = llm_client or LLMClient()

    def correct_grammar(self, text: str) -> str:
        """
        Corrects grammar using the LLM.
        """
        system_prompt = (
            "You are a helpful grammar assistant. "
            "Your sole task is to correct the grammar of the user's input. "
            "Return ONLY the corrected text. "
            "Do not add explanations, quotes, or conversational filler. "
            "If the text is already correct, return it as is."
        )
        
        try:
            # Reusing the chat generation method
            corrected_text = self.llm_client.generate_chat_response(system_prompt, text)
            return corrected_text.strip()
        except Exception as e:
            print(f"Grammar correction failed: {e}")
            # Fallback to original text if LLM fails
            return text
