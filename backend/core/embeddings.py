from langchain_google_genai import GoogleGenerativeAIEmbeddings
from core.config import settings
import os

def get_embeddings_model():
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in settings or environment")
        
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )

async def generate_embedding(text: str) -> list[float]:
    """
    Generates a 768-dimensional embedding for the given text using Gemini via LangChain.
    """
    model = get_embeddings_model()
    embedding = await model.aembed_query(text)
    return embedding
