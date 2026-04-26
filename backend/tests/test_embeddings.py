import asyncio
import os
import sys

# Add the backend directory to sys.path so we can import 'core'
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Now we can import from core
from core.embeddings import generate_embedding

async def main():
    test_string = '''Technical & Academic Requirements:
- Currently pursuing a Bachelor’s or Master’s degree in Computer 
  Science, Engineering, Mathematics, or a related technical field.
- Proficiency in at least one core language: Java, C++, Python, or 
  JavaScript/TypeScript.
- Strong understanding of Data Structures and Algorithms (time/space 
  complexity, trees, graphs, sorting).
- Familiarity with Object-Oriented Programming (OOP) principles and 
  design patterns.
- Basic knowledge of database systems (SQL or NoSQL) and Version 
  Control (Git).

Professional Competencies:
- Problem-Solving: Ability to break down complex, ambiguous problems 
  into manageable technical tasks.
- Communication: Capacity to explain technical concepts to non-technical 
  stakeholders.
- Adaptability: Eagerness to learn new technologies and financial 
  concepts in a high-pressure environment.
- Collaboration: Proven ability to work effectively within a 
  diverse global team.'''
      
    print(f"\nGenerating embedding for")
    
    try:
        embedding = await generate_embedding(test_string)
        print(f"\nEmbedding (first 10 dimensions): {embedding[:10]}...")
        print(f"Total dimensions: {len(embedding)}")
        print("\nFull embedding list:")
        print(embedding)
    except Exception as e:
        print(f"\nError generating embedding: {e}")

if __name__ == "__main__":
    asyncio.run(main())
