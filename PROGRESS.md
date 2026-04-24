# HireLoop Project Progress Report

## 1. Backend Foundation
- **Framework**: FastAPI with SQLModel (SQLAlchemy + Pydantic).
- **Database**: PostgreSQL (Supabase) with `asyncpg` for asynchronous operations.
- **Environment**: Configured `.env` and `config.py` for secure credential management.

## 2. Authentication System
- **Signup Logic**: Created a unified auth service in `backend/services/auth_service.py`.
- **Endpoints**:
  - `POST /auth/signup/candidate`: Registers a user and creates a candidate profile.
  - `POST /auth/signup/company`: Registers a user and creates a company profile.
- **Security**: Implemented password hashing using `passlib` and `bcrypt`.

## 3. Cloudinary Integration
- **Storage**: Configured Cloudinary (Cloud Name: `ddr4nbahy`) for file hosting.
- **Folders**: 
  - `HireLoop/Resume`: For candidate resumes.
  - `HireLoop/CompanyLogo`: For company branding.
- **Utility**: Created `backend/core/cloudinary.py` to handle asynchronous file uploads.

## 4. Profile & Data Management
- **Candidate Updates**: `PATCH /candidates/{user_id}/update` handles partial profile updates and resume uploads.
- **Company Updates**: `PATCH /companies/{user_id}/update` handles partial profile updates and logo uploads.
- **Schemas**: Created specialized Pydantic models for data validation and response consistency.

## 5. Job Posting System
- **Model Enhancements**: Reviewed and fixed the `Job` model with `job_posted_at` (auto-now) and `application_deadline` (optional).
- **Creation**: `POST /jobs/` allows companies to post new job openings.
- **Validation**: Service logic ensures only users with a valid `Company` profile can create jobs.

## 6. Job Application Logic
- **Endpoint**: `POST /applications/` allows candidates to apply for jobs.
- **Status Check**: Built-in validation to ensure applications are only accepted if the job status is **"open"**.
- **Integrity**: 
  - Prevents duplicate applications from the same candidate for the same job.
  - Verifies that only candidates (not companies) can apply.

## 7. Current Project Structure
- `backend/routers/`: Auth, Candidates, Companies, Jobs, Applications.
- `backend/services/`: Business logic for all modules.
- `backend/schemas/`: Pydantic models for request/response.
- `backend/models/`: SQLModel database definitions.
- `backend/core/`: Database, Cloudinary, and Config setups.
