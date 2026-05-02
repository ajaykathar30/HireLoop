from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime


class QuestionReport(BaseModel):
    """Schema for an individual interview question's evaluation."""
    question: str
    answer: Optional[str] = None
    score: Optional[int] = None
    feedback: Optional[str] = None


class CandidateReport(BaseModel):
    """Schema for a single candidate's interview report."""
    candidate_id: uuid.UUID
    candidate_name: str
    application_id: uuid.UUID
    session_id: uuid.UUID
    status: str
    total_score: Optional[int] = None
    report_summary: Optional[str] = None
    completed_at: Optional[datetime] = None
    questions: List[QuestionReport] = []


class JobReportsResponse(BaseModel):
    """Schema for the full reports response for a job."""
    job_id: uuid.UUID
    job_title: str
    total_reports: int
    reports: List[CandidateReport] = []


class CandidateSummary(BaseModel):
    """Schema for a candidate entry in the summary report."""
    name: str
    score: Optional[int] = None
    summary: Optional[str] = None
    session_id: str


class JobReportsSummary(BaseModel):
    """Schema for the aggregated summary report from report_service."""
    job_title: str
    total_interviews: int
    average_score: float
    candidates: List[CandidateSummary] = []
