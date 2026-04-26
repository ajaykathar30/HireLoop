# HireLoop - AI-Powered Job Portal & Recruitment Platform

HireLoop is a modern, intelligent recruitment platform designed to connect top talent with great companies. By leveraging advanced AI and machine learning pipelines, HireLoop automates the tedious parts of the hiring process—specifically candidate ranking, resume shortlisting, and automated, audio-based AI interviews.

## 🚀 Features

- **For Candidates:** Apply to jobs seamlessly, manage applications, and take interactive AI-driven audio interviews directly in the browser.
- **For Companies:** Post jobs, view a dashboard of applicants, and trigger the AI screening pipeline to automatically rank and evaluate candidates.
- **AI Screening:** Automatic resume parsing, embedding generation, and LLM-based fit scoring.
- **AI Audio Interviews:** Dynamic, context-aware interview questions generated based on the candidate's resume and job description, with audio transcription and instant feedback scoring.

---

## 💻 Tech Stack

### Frontend
- **Framework:** React 19 + Vite
- **Routing:** React Router DOM
- **State Management:** Redux Toolkit + Redux Persist
- **Styling:** TailwindCSS v4
- **UI Components:** Shadcn/UI (Radix UI), Lucide React (Icons)
- **Data Fetching:** Axios

### Backend
- **Framework:** FastAPI (Python 3.13+)
- **Database:** PostgreSQL with `pgvector` for vector embeddings
- **ORM:** SQLModel & Alembic for migrations
- **Authentication:** JWT, bcrypt, passlib
- **Storage:** Cloudinary (for media/resumes)
- **AI & Orchestration:** 
  - LangChain & LangGraph (Pipeline Orchestration)
  - Google Generative AI (Gemini) for LLM logic
  - Google Generative AI (`gemini-embedding-001`) for text embeddings
  - Sarvam API for highly accurate Speech-to-Text (STT) transcription
  - PyPDF for parsing resumes

---

## 🧠 AI Pipelines (LangGraph)

HireLoop operates on two core LangGraph state-machine pipelines located in `backend/pipeline/`.

### 1. Resume Shortlisting Pipeline (`recruitment_graph.py`)
Triggered by companies to evaluate their applicants.
1. **Fetch:** Retrieves all pending applications for a job.
2. **Parse:** Extracts raw text from candidate PDF resumes using PyPDF.
3. **Rank:** Generates vector embeddings for the job description and the resumes using `gemini-embedding-001` model, calculating similarity via `pgvector` in PostgreSQL.
4. **Score:** Passes the extracted data to Google Gemini to calculate a comprehensive `fit_score` based on skills and experience matching.
5. **Finalize:** Updates the application statuses to `shortlisted` or `rejected` in the database.

### 2. AI Interview Pipeline (`interview_graph.py`)
Triggered when a shortlisted candidate starts their interview.
1. **Init (`init_interview_node`):** Gemini analyzes the Job Description and the Candidate's Resume to dynamically generate 5 highly contextual interview questions.
2. **Ask (`ask_question_node`):** Presents the current question to the candidate and physically interrupts the LangGraph execution, waiting for audio input.
3. **Save (`save_answer_node`):** Receives the candidate's audio recording, transcribes it using Sarvam AI, and asks Gemini to score the answer (out of 20) while providing constructive feedback.
4. **Finalize (`finalize_interview_node`):** Aggregates the scores of all 5 questions into a `total_score` and generates an Executive AI Report Summary for the company to review.

---

## ⚙️ Environment Variables Structure

Create a `.env` file in the `backend/` directory with the following structure:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>

# JWT Authentication
JWT_SECRET_KEY=your_super_secret_jwt_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# Cloudinary Storage (For Resumes & Avatars)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# AI APIs
GOOGLE_API_KEY=your_gemini_api_key
HF_API_KEY=your_huggingface_api_key
SARVAM_API_KEY=your_sarvam_stt_api_key
```

---

## 🛠️ Setup & Installation

### Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Install dependencies (using UV or pip): `uv pip install -r requirements.txt` *(or equivalent from pyproject.toml)*
3. Run Alembic migrations: `alembic upgrade head`
4. Start the FastAPI server: `uv run uvicorn main:app --reload`

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the Vite development server: `npm run dev`
