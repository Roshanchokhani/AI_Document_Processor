"""
AI Service - Groq Integration for Document Q&A

This is the CORE service that handles:
1. Connecting to Groq API (FREE and FAST!)
2. Sending document context + question
3. Getting AI-generated answers
4. GROUNDING - ensuring answers come ONLY from the document

WHY GROQ?
=========
- FREE tier: 30 requests per minute
- VERY FAST: Uses custom LPU chips
- No credit card required
- Great quality with Llama models
- Easy to set up
"""

from groq import Groq
from app.config import settings


class AIService:
    """
    Service for AI-powered question answering using Groq.

    Uses Groq's API with Llama models and careful prompt
    engineering to ensure grounded responses.
    """

    def __init__(self):
        """Initialize Groq client."""
        self._client = None
        self.model_name = settings.GROQ_MODEL

    @property
    def client(self):
        """Lazy initialization of Groq client."""
        if self._client is None and settings.GROQ_API_KEY:
            self._client = Groq(api_key=settings.GROQ_API_KEY)
        return self._client

    def answer_question(self, document_content: str, question: str) -> str:
        """
        Answer a question based ONLY on the provided document content.

        Args:
            document_content: The full text content of the document
            question: User's question about the document

        Returns:
            AI-generated answer grounded in the document

        Raises:
            Exception: If API call fails
        """
        # Validate inputs
        if not document_content or not document_content.strip():
            raise ValueError("Document content is empty")

        if not question or not question.strip():
            raise ValueError("Question is empty")

        # Check if question is too long (prevent issues)
        if len(question) > 1000:
            raise ValueError("Question is too long. Maximum 1000 characters allowed.")

        # Build the messages
        messages = self._build_messages(document_content, question)

        try:
            # Make API call to Groq
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=1024,
                temperature=0.1,  # Low = focused, less creative (prevents hallucination)
            )

            # Extract the answer
            answer = response.choices[0].message.content.strip()
            return answer

        except Exception as e:
            # Handle API errors - show actual error for debugging
            error_message = str(e)
            raise Exception(f"Groq API error: {error_message}")

    def _build_messages(self, document_content: str, question: str) -> list:
        """
        Build the message list for Groq Chat API.

        This is where PROMPT ENGINEERING happens.

        Returns:
            List of message dictionaries for the API
        """
        # SYSTEM PROMPT - This is the most important part!
        system_prompt = """You are a precise document analysis assistant. Your ONLY job is to answer questions based strictly on the provided document content.

CRITICAL RULES YOU MUST FOLLOW:
1. ONLY use information that is explicitly stated in the document
2. DO NOT use any external knowledge or make assumptions
3. DO NOT infer or guess information that isn't clearly written
4. If the document does not contain the answer, you MUST respond with exactly: "The document does not contain this information."
5. Quote or paraphrase directly from the document when possible
6. Be concise and accurate

Remember: It's better to say you don't know than to make up information."""

        # USER PROMPT - Contains the document and question
        user_prompt = f"""DOCUMENT CONTENT:
---
{document_content}
---

QUESTION: {question}

Based ONLY on the document content above, please answer the question. If the answer cannot be found in the document, respond with "The document does not contain this information." """

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def validate_api_key(self) -> bool:
        """
        Check if the Groq API key is configured.

        Returns:
            True if API key exists, False otherwise
        """
        return bool(settings.GROQ_API_KEY and
                    settings.GROQ_API_KEY.strip() and
                    settings.GROQ_API_KEY != "your_groq_api_key_here")


# Create singleton instance
ai_service = AIService()
