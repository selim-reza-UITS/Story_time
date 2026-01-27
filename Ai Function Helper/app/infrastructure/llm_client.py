from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

class LLMClient:
    def __init__(self):
        # Initialize LangChain ChatOpenAI
        # Ensure OPENAI_API_KEY is in env
        self.chat = ChatOpenAI(
            model="gpt-4.1-nano",
            temperature=0.4
        )

    def generate_chat_response(self, system_prompt: str, user_message: str) -> str:
        """
        Generates a response from the LLM based on system and user prompts.
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        try:
            response = self.chat.invoke(messages)
            return response.content
        except Exception as e:
            # Basic error handling
            print(f"LLM Error: {e}")
            return "I'm sorry, I'm having trouble connecting to my brain right now."

    def generate_description(self, text: str) -> str:
        """
        Asks LLM to generate a short metadata description/explanation.
        """
        prompt = f"Provide a very brief (one sentence) categorization or description of this text: '{text}'"
        return self.generate_chat_response("You are a metadata assistant.", prompt)
