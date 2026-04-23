import os
import re
import tempfile
import requests
import logging
from typing import List, Dict
from pypdf import PdfReader

logger = logging.getLogger("recruitsight.pdf_tools")

def download_pdf(url: str) -> str:
    """Download a PDF from a URL to a temporary file and return the path."""
    logger.info(f"Downloading PDF from: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Create a temporary file
        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        with os.fdopen(fd, 'wb') as f:
            f.write(response.content)
            
        logger.info(f"PDF downloaded successfully to {temp_path}")
        return temp_path
    except Exception as e:
        logger.error(f"Failed to download PDF: {e}")
        raise

def extract_links_from_pdf(pdf_path: str) -> Dict[str, List[str]]:
    """
    Extract GitHub and LinkedIn links from a PDF file.
    Finds both hyperlinked annotations and raw text URLs.
    """
    logger.info(f"Extracting links from PDF: {pdf_path}")
    
    links = set()
    
    try:
        reader = PdfReader(pdf_path)
        
        # Regex for finding raw URLs in text
        url_pattern = re.compile(r'https?://(?:www\.)?(?:github\.com|linkedin\.com)[^\s\]\)"\']+')
        
        for page in reader.pages:
            # 1. Extract from Annotations (Clickable links)
            if "/Annots" in page:
                for annot in page["/Annots"]:
                    try:
                        obj = annot.get_object()
                        if "/A" in obj and "/URI" in obj["/A"]:
                            uri = obj["/A"]["/URI"]
                            if isinstance(uri, str):
                                links.add(uri)
                    except Exception:
                        pass
            
            # 2. Extract from raw text
            text = page.extract_text()
            if text:
                found_urls = url_pattern.findall(text)
                for url in found_urls:
                    links.add(url)
                    
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        
    # Categorize links
    github_links = []
    linkedin_links = []
    
    for link in links:
        link_lower = link.lower()
        if "github.com" in link_lower:
            github_links.append(link)
        elif "linkedin.com/in/" in link_lower:
            linkedin_links.append(link)
            
    logger.info(f"Found {len(github_links)} GitHub links and {len(linkedin_links)} LinkedIn links.")
    
    return {
        "github": github_links,
        "linkedin": linkedin_links
    }
