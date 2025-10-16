import os
from groq import Groq
from dotenv import load_dotenv

# It's a good practice to load environment variables at the start
load_dotenv()

class LLMService:
    def __init__(self):
        """
        Initializes the Groq client using the API key from environment variables.
        """
        try:
            self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            if not self.client.api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables.")
        except Exception as e:
            print(f"Error initializing Groq client: {e}")
            self.client = None

    def generate_response(self, prompt: str, model: str = "llama-3.1-8b-instant"):
        """
        Sends a prompt to the Groq LLM and gets a complete response.
        """
        if not self.client:
            return "LLM service is not available."

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant for inventory management. Analyze the data provided and answer the user's question concisely."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"An error occurred while communicating with Groq API: {e}")
            return "Sorry, I encountered an error while processing your request."
    
    def generate_streaming_response(self, prompt: str, model: str = "llama-3.1-8b-instant"):
        """
        Generates a streaming response from the Groq LLM. [cite_start]This is useful for a real-time chat interface[cite: 360, 361].
        This function returns a generator.
        """
        if not self.client:
            yield "LLM service is not available."
            return

        try:
            stream = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant for inventory management. Analyze the data provided and answer the user's question concisely."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model,
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            print(f"An error occurred during streaming with Groq API: {e}")
            yield "Sorry, an error occurred during streaming."