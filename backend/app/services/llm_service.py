import google.generativeai as genai
from app.config import settings
import time
from typing import Generator

class LLMService:
    """Service for interacting with Google Gemini LLM"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-2.5-flash-lite"
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None
    
    def _build_prompt(self, query: str, context_chunks: list[str]) -> str:
        """Build the RAG prompt from query and context"""
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            context_parts.append(f"[Section {i}]:\n{chunk}")
        context_text = "\n\n".join(context_parts)
        
        return f"""Read the following text carefully and answer the question.

{context_text}

Question: {query}

Answer based on the text above:"""
            
    def generate_rag_response(self, query: str, context_chunks: list[str]) -> str:
        """Generate an answer using context chunks (non-streaming)"""
        if not self.model:
            return "Error: Gemini API Key is not configured."
            
        prompt = self._build_prompt(query, context_chunks)
        
        # Retry up to 3 times with backoff for rate limits
        for attempt in range(3):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                    )
                )
                return response.text
            except Exception as e:
                error_str = str(e)
                if "429" in error_str and attempt < 2:
                    wait_time = 10 * (attempt + 1)
                    time.sleep(wait_time)
                    continue
                return f"Error communicating with LLM: {error_str}"
    
    def generate_rag_response_stream(self, query: str, context_chunks: list[str]) -> Generator[str, None, None]:
        """Generate an answer using context chunks (streaming, yields text chunks)"""
        if not self.model:
            yield "Error: Gemini API Key is not configured."
            return
            
        prompt = self._build_prompt(query, context_chunks)
        
        for attempt in range(3):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                    ),
                    stream=True
                )
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                return  # Success, stop retrying
            except Exception as e:
                error_str = str(e)
                if "429" in error_str and attempt < 2:
                    wait_time = 10 * (attempt + 1)
                    time.sleep(wait_time)
                    continue
                yield f"Error communicating with LLM: {error_str}"
                return
