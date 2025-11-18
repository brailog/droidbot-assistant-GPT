# gemini_api/client.py

import os
import google.generativeai as genai
from typing import List, Dict, Optional

# --- Configuration ---
# The API key is configured using the GOOGLE_API_KEY environment variable.
# You can also pass it directly to genai.configure(api_key="...")
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("ERROR: The GOOGLE_API_KEY environment variable is not set.")
    print("Please get your key from https://aistudio.google.com/app/apikey and set the variable.")
    # You might want to raise an exception here instead of just printing.
    # raise EnvironmentError("GOOGLE_API_KEY not found.")

class GeminiClient:
    """
    A client for interacting with the Google Gemini API.

    This class provides a simplified interface for generating content
    using Gemini models, designed to be analogous to an OpenAI client.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Initializes the Gemini client.

        Args:
            model_name (str): The name of the Gemini model to use.
                              Defaults to "gemini-2.5-flash".
        """
        self.model_name = model_name
        self.model = genai.GenerativeModel(self.model_name)
        print(f"GeminiClient initialized with model: {self.model_name}")

    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_output_tokens: Optional[int] = None,
        code_markdown_remove: bool = False,
        response_mime_type: str = "text/plain"
    ) -> str:
        """
        Generates text content from a single string prompt.

        This is similar to OpenAI's legacy `Completion` API.

        Args:
            prompt (str): The text prompt to send to the model.
            temperature (float): Controls the randomness of the output.
            max_output_tokens (Optional[int]): The maximum number of tokens to generate.
            code_markdown_remove (bool): Remove the markdown from code response. Default False

        Returns:
            str: The generated text content.
        """
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type=response_mime_type,
        )

        try:
            response_text = self.model.generate_content(
                prompt,
                generation_config=generation_config
            ).text
            if code_markdown_remove:
                response_text = response_text.replace("```json", "").replace("```python", "").replace("```", "")
            return response_text
        except Exception as e:
            print(f"An error occurred while generating text: {e}")
            # Depending on your needs, you might want to return an empty string or re-raise
            return f"Error: {e}"

    def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.6,
        max_output_tokens: Optional[int] = None
    ) -> str:
        """
        Generates a response for a chat-like conversation.

        This is analogous to OpenAI's `ChatCompletion` API.

        Args:
            messages (List[Dict[str, str]]): A list of message dictionaries,
                e.g., [{"role": "user", "parts": ["Hello!"]}]
                Note: Gemini uses 'parts' instead of 'content'.
            temperature (float): Controls the randomness of the output.
            max_output_tokens (Optional[int]): The maximum number of tokens to generate.

        Returns:
            str: The model's response message.
        """
        # The Gemini API expects a slightly different message format than OpenAI.
        # OpenAI: {"role": "user", "content": "Hello"}
        # Gemini: {"role": "user", "parts": ["Hello"]}
        # This method assumes the input `messages` list is already in the Gemini format.
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

        # For chat, we start a session to maintain context
        chat_session = self.model.start_chat(
            history=messages[:-1] # History is all messages except the last one
        )
        
        last_message = messages[-1]['parts'][0] # Get the content of the last message

        try:
            response = chat_session.send_message(
                last_message,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            print(f"An error occurred during chat completion: {e}")
            return f"Error: {e}"


if __name__ == '__main__':
    print("--- Running Gemini API Client Examples ---")
    
    # Check if the API key is available before proceeding
    if "GOOGLE_API_KEY" not in os.environ:
        print("\nSkipping examples because GOOGLE_API_KEY is not set.")
    else:
        client = GeminiClient()

        # 1. Simple text generation example
        print("\n--- Example 1: Simple Text Generation ---")
        prompt = "Explain the difference between a compiler and an interpreter in one paragraph."
        print(f"Prompt: {prompt}")
        response_text = client.generate_text(prompt, temperature=0.5)
        print(f"Gemini Response:\n{response_text}")

        # 2. Chat completion example
        print("\n--- Example 2: Chat Completion ---")
        chat_messages = [
            {"role": "user", "parts": ["Hello, I'm building a chatbot."]},
            {"role": "model", "parts": ["Great! I can help with that. What is your first question?"]},
            {"role": "user", "parts": ["What is the first step to consider when designing a conversation flow?"]}
        ]
        print(f"Chat History Sent: {chat_messages}")
        chat_response = client.create_chat_completion(chat_messages, temperature=0.8)
        print(f"Gemini Response:\n{chat_response}")
