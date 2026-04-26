import asyncio
import os
import sys
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from core.config import settings
from models.interview import InterviewSession, InterviewQuestion
from pipeline.interview_graph import interview_app

async def run_mock_interview():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        stmt = select(InterviewSession).where(InterviewSession.status == "pending").limit(1)
        res = await db.execute(stmt)
        session = res.scalar_one_or_none()
        
        if not session:
            stmt = select(InterviewSession).where(InterviewSession.status == "ongoing").limit(1)
            res = await db.execute(stmt)
            session = res.scalar_one_or_none()

        if not session:
            print("❌ No interview sessions found. Run a recruitment pipeline first.")
            return

        session_id = session.id
        print(f"\n🚀 STARTING MOCK INTERVIEW (BATCH EVALUATION MODE)")
        print(f"Session ID: {session_id}")
        print("="*40)
        
        config = {"configurable": {"thread_id": str(session_id), "db": db}}

        # 1. Start the interview
        print("\n[SYSTEM] Initializing interview...")
        await interview_app.ainvoke(
            {"session_id": session_id, "current_q_idx": 0, "logs": [], "status": "init"},
            config=config
        )

        # 2. Loop through 5 questions
        for i in range(5):
            q_stmt = select(InterviewQuestion).where(and_(InterviewQuestion.session_id == session_id, InterviewQuestion.order_index == i))
            q_res = await db.execute(q_stmt)
            question = q_res.scalar_one()

            print(f"\n--- QUESTION {i+1} OF 5 ---")
            print(f"AI: {question.question_text}")
            print("-" * 20)
            
            user_input = input("YOUR ANSWER: ")

            print(f"\n[SYSTEM] Saving response...")
            await interview_app.ainvoke(
                {
                    "session_id": session_id, 
                    "current_q_idx": i, 
                    "last_answer_text": user_input,
                    "is_timeout": not user_input,
                    "status": "saving" 
                },
                config=config
            )
            print("✅ Saved.")

        # 3. Finalize (Perform BATCH EVALUATION)
        print("\n" + "="*40)
        print("[SYSTEM] Performing Batch Evaluation with Gemini-3...")
        await interview_app.ainvoke(
            {"session_id": session_id, "status": "finalizing"},
            config=config
        )

        await db.refresh(session)
        
        # Print individual scores
        print("\n--- INDIVIDUAL SCORES ---")
        q_stmt = select(InterviewQuestion).where(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.order_index)
        q_res = await db.execute(q_stmt)
        for q in q_res.scalars().all():
            print(f"Q{q.order_index+1}: {q.score}/20 - {q.feedback}")

        print("\n=== FINAL RECRUITMENT REPORT ===")
        print(f"TOTAL SCORE: {session.total_score}/100")
        print(f"SUMMARY: {session.report_summary}")
        print("="*40)
        print("\n✅ Mock interview completed!")

if __name__ == "__main__":
    asyncio.run(run_mock_interview())
