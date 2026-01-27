from typing import List, Optional

class PromptBuilder:
    @staticmethod
    def build_system_prompt(behavior_settings: str, context: Optional[str] = None) -> str:
        """
        Constructs the system prompt using dynamic behavior settings.
        """
        base_prompt = behavior_settings
        
        if context:
            base_prompt += f"\n\nContext provided: {context}"
            
        return base_prompt

    @staticmethod
    def format_conversation_history(history: List[str]) -> str:
        """
        Formats the list of previous messages into a string block for the LLM.
        """
        if not history:
            return ""
        
        # Take last 5 messages to keep context window manageable
        recent_history = history[-5:]
        formatted = "\n".join([f"- {msg}" for msg in recent_history])
        return f"\n\nConversation History:\n{formatted}"
