from typing import List

class ConversationManager:
    def update_history(self, current_history: List[str], user_input: str, system_response: str) -> List[str]:
        """
        Updates the conversation history with the new exchange.
        """
        # Create a new list to avoid mutating the input directly if it matters
        updated_history = list(current_history)
        
        updated_history.append(f"User: {user_input}")
        updated_history.append(f"System: {system_response}")
        
        return updated_history
