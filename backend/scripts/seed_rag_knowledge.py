import asyncio
import os
from pathlib import Path
from docling.document_converter import DocumentConverter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

# To allow script to run independently, we set up imports assuming it's executed from backend/
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import engine, AsyncSessionLocal
from core.embeddings import generate_embedding
from models.rag import DomainKnowledgeBase

DATA_DIR = Path(__file__).parent.parent / "data" / "rag_pdfs"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Define domains based on filename keywords (naive router for MVP)
DOMAIN_MAP = {
    "frontend": "Frontend",
    "web": "Frontend",
    "backend": "Backend",
    "data-intensive": "Backend",
    "algorithm": "DSA",
    "dsa": "DSA",
    "agent": "AI Agents",
    "llm": "AI Agents",
}

def determine_domain(filename: str) -> str:
    lower_name = filename.lower()
    for keyword, domain in DOMAIN_MAP.items():
        if keyword in lower_name:
            return domain
    return "General"

async def process_pdf(file_path: Path, session: AsyncSession):
    print(f"Processing {file_path.name}...")
    domain = determine_domain(file_path.name)
    
    # 1. Parse with Docling
    converter = DocumentConverter()
    result = converter.convert(str(file_path))
    markdown_text = result.document.export_to_markdown()

    # 2. Chunk the text
    # We use a relatively large chunk size to capture full scenarios/context
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_text(markdown_text)
    print(f"  -> Generated {len(chunks)} chunks.")

    # 3. Embed and Save
    # We do this in batches so we don't hit Gemini rate limits
    batch_size = 10
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        for chunk_text in batch:
            try:
                embedding = await generate_embedding(chunk_text)
                db_chunk = DomainKnowledgeBase(
                    domain=domain,
                    source_file=file_path.name,
                    content=chunk_text,
                    embedding=embedding
                )
                session.add(db_chunk)
            except Exception as e:
                print(f"Error generating embedding for chunk: {e}")
        
        await session.commit()
        print(f"  -> Saved batch {i//batch_size + 1}")
        await asyncio.sleep(2) # rate limit sleep

async def main():
    pdf_files = list(DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {DATA_DIR}. Please add some PDFs to ingest.")
        return

    async with AsyncSessionLocal() as session:
        for pdf_file in pdf_files:
            await process_pdf(pdf_file, session)
            
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(main())
