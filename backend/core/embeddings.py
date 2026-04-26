from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
load_dotenv()

def get_embeddings_model():
    return GoogleGenerativeAIEmbeddings( 
    model="models/gemini-embedding-001", 
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

async def generate_embedding(text: str) -> list[float]:
    """
    Generates a 768-dimensional embedding for the given text using Gemini via LangChain.
    Gemini-embedding-001 natively produces 3072 dimensions, so we truncate to 768.
    """
    model = get_embeddings_model()
    # LangChain's GoogleGenerativeAIEmbeddings might not support 'task_type' or 'output_dimensionality' 
    # directly in query methods yet, so we manually truncate to match DB schema.
    embedding = await model.aembed_query(text)
    # Ensure result is a standard list for JSON serialization
    return list(embedding[:768])
