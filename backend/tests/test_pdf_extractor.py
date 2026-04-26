import asyncio
import os
import sys

# Add the backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from core.pdf_extractor import extract_text_from_pdf

async def main():
    if len(sys.argv) > 1:
        pdf_url = sys.argv[1]
    else:
        if sys.stdin.isatty():
            pdf_url = input("Enter the PDF URL to extract text from: ")
        else:
            print("Error: No PDF URL provided and not in a TTY.")
            return

    if not pdf_url:
        print("No URL provided.")
        return

    print(f"\nExtracting text from: {pdf_url}...")
    
    try:
        text = await extract_text_from_pdf(pdf_url)
        print("\n--- Extracted Text Start ---")
        print(text if text else "[No text could be extracted from this PDF]")
        print("--- Extracted Text End ---")
        print(f"\nTotal characters: {len(text)}")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    asyncio.run(main())
