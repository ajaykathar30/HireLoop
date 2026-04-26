# pip install pypdf httpx
import httpx
from pypdf import PdfReader

from io import BytesIO

async def extract_text_from_pdf(pdf_url: str) -> str:
    """
    Downloads a PDF from a URL and extracts all text.
    """
    
    async with httpx.AsyncClient() as client:
        response = await client.get(pdf_url)
        if response.status_code != 200:
            raise Exception(f"Failed to download PDF from {pdf_url}")
        
        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        return text.strip()
