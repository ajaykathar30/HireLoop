"""
RecruitSight — Pydantic I/O Schemas
All structured output models used by agents for strict JSON responses.
These are passed to the Gemini `response_schema` parameter.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════
# 1. REPO INGESTION AGENT
# ═══════════════════════════════════════════════════════════════════

class IngestionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class RepoIngestionOutput(BaseModel):
    """Output from the Repo Ingestion Agent."""
    status: IngestionStatus = Field(description="Whether the repo was cloned successfully")
    local_path: str = Field(description="Path to the cloned repository on disk")
    owner: str = Field(description="GitHub username / org that owns the repo")
    repo_name: str = Field(description="Repository name")
    default_branch: str = Field(description="Default branch name (e.g. main, master)")
    total_commits: int = Field(description="Total number of commits in the repo")
    clone_timestamp: str = Field(description="ISO timestamp of when the clone happened")
    error: Optional[str] = Field(default=None, description="Error message if status is failed")


# ═══════════════════════════════════════════════════════════════════
# 2. FILE STRUCTURE ANALYST AGENT
# ═══════════════════════════════════════════════════════════════════

class FileStructureOutput(BaseModel):
    """Output from the File Structure Analyst Agent."""
    project_type: str = Field(description="Detected project type (web app, CLI, API, ML, library, mobile, etc.)")
    directory_tree: str = Field(description="Text representation of the folder structure")
    structure_score: int = Field(description="Structure quality score from 1-10")
    strengths: list[str] = Field(description="List of structural strengths")
    red_flags: list[str] = Field(description="List of structural red flags")
    has_tests: bool = Field(description="Whether the project has a test directory with test files")
    has_ci_cd: bool = Field(description="Whether CI/CD configuration files exist")
    has_docker: bool = Field(description="Whether Docker configuration exists")
    summary: str = Field(description="2-3 sentence summary of the structure analysis")


# ═══════════════════════════════════════════════════════════════════
# 3. COMMIT FORENSICS AGENT
# ═══════════════════════════════════════════════════════════════════

class CommitDistribution(str, Enum):
    CLUSTERED = "clustered"
    CONSISTENT = "consistent"
    SPARSE = "sparse"


class CommitVerdict(str, Enum):
    LIKELY_GENUINE = "LIKELY GENUINE"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH_RISK = "HIGH RISK"


class CommitForensicsOutput(BaseModel):
    """Output from the Commit Forensics Agent."""
    total_commits: int = Field(description="Total number of commits")
    time_span_days: int = Field(description="Number of days from first to last commit")
    first_commit_date: str = Field(description="ISO date of the first commit")
    last_commit_date: str = Field(description="ISO date of the last commit")
    avg_commits_per_week: float = Field(description="Average commits per week")
    commit_distribution: CommitDistribution = Field(description="Whether commits are clustered, consistent, or sparse")
    message_quality_score: int = Field(description="Commit message quality score from 1-10")
    author_consistency: bool = Field(description="Whether the author is consistent throughout")
    red_flags: list[str] = Field(description="List of commit-related red flags")
    positive_signals: list[str] = Field(description="List of positive commit signals")
    authenticity_score: int = Field(description="Authenticity score from 1-10")
    verdict: CommitVerdict = Field(description="Overall commit authenticity verdict")
    summary: str = Field(description="3-4 sentence forensic summary")


# ═══════════════════════════════════════════════════════════════════
# 4. CODE QUALITY & LOGIC AGENT
# ═══════════════════════════════════════════════════════════════════

class CompletionLevel(str, Enum):
    PROTOTYPE = "prototype"
    MVP = "MVP"
    PRODUCTION_READY = "production-ready"


class SuspicionLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CodeQualityOutput(BaseModel):
    """Output from the Code Quality & Logic Agent."""
    primary_language: str = Field(description="Primary programming language used")
    files_sampled: list[str] = Field(description="List of file paths that were sampled for analysis")
    logic_quality_score: int = Field(description="Logic quality score from 1-10")
    code_style_score: int = Field(description="Code style/convention score from 1-10")
    test_quality_score: Optional[int] = Field(default=None, description="Test quality score from 1-10, null if no tests")
    has_hardcoded_secrets: bool = Field(description="Whether hardcoded secrets/API keys were found")
    dead_code_percentage: str = Field(description="Estimated percentage of dead/unused code")
    completion_level: CompletionLevel = Field(description="Project completion level")
    red_flags: list[str] = Field(description="List of code quality red flags")
    strengths: list[str] = Field(description="List of code quality strengths")
    ai_generated_suspicion: SuspicionLevel = Field(description="Suspicion level for AI-generated code")
    overall_code_score: int = Field(description="Overall code quality score from 1-10")
    summary: str = Field(description="3-4 sentence code evaluation")


# ═══════════════════════════════════════════════════════════════════
# 5. DEPENDENCY AUDITOR AGENT
# ═══════════════════════════════════════════════════════════════════

class DependencyAuditOutput(BaseModel):
    """Output from the Dependency Auditor Agent."""
    dependency_files_found: list[str] = Field(description="List of dependency files found (package.json, requirements.txt, etc.)")
    total_dependencies: int = Field(description="Total number of production dependencies")
    dev_dependencies: int = Field(description="Total number of dev dependencies")
    key_libraries: list[str] = Field(description="Key libraries with their purpose (e.g. 'express: HTTP server')")
    has_lock_file: bool = Field(description="Whether a lock file exists")
    dependency_appropriateness_score: int = Field(description="Dependency appropriateness score from 1-10")
    red_flags: list[str] = Field(description="List of dependency red flags")
    strengths: list[str] = Field(description="List of dependency strengths")
    unusual_or_suspicious_packages: list[str] = Field(description="List of unusual or suspicious packages")
    summary: str = Field(description="2-3 sentence dependency analysis")


# ═══════════════════════════════════════════════════════════════════
# 6. README VS REALITY AGENT
# ═══════════════════════════════════════════════════════════════════

class ClaimStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIAL = "PARTIAL"
    UNVERIFIABLE = "UNVERIFIABLE"
    FALSE = "FALSE"


class ReadmeImpression(str, Enum):
    UNDER_SELLS = "under-sells"
    ACCURATE = "accurate"
    OVER_SELLS = "over-sells"
    FABRICATES = "fabricates"


class ClaimVerification(BaseModel):
    """A single README claim and its verification status."""
    claim: str = Field(description="What the README claims")
    status: ClaimStatus = Field(description="Verification status of the claim")
    evidence: str = Field(description="What the code actually shows")


class ReadmeRealityOutput(BaseModel):
    """Output from the README vs Reality Agent."""
    readme_exists: bool = Field(description="Whether a README file exists")
    readme_length: str = Field(description="README length classification: minimal, adequate, or comprehensive")
    claims_analyzed: list[ClaimVerification] = Field(description="List of claims and their verification")
    verified_count: int = Field(description="Number of verified claims")
    false_count: int = Field(description="Number of false claims")
    honesty_score: int = Field(description="README honesty score from 1-10")
    overall_impression: ReadmeImpression = Field(description="Overall impression of README accuracy")
    summary: str = Field(description="2-3 sentence verdict on README honesty")


# ═══════════════════════════════════════════════════════════════════
# 7. SIMILAR REPO DISCOVERY AGENT
# ═══════════════════════════════════════════════════════════════════

class SimilarityType(str, Enum):
    CONCEPTUAL = "conceptual"
    STRUCTURAL = "structural"
    POTENTIAL_SOURCE = "potential_source"


class SimilarRepo(BaseModel):
    """A single similar repository found via web search."""
    url: str = Field(description="GitHub URL of the similar repo")
    name: str = Field(description="Repository name")
    description: str = Field(description="Brief description of the repo")
    similarity_type: SimilarityType = Field(description="Type of similarity")
    stars: Optional[int] = Field(default=None, description="Star count if available")
    is_tutorial_project: bool = Field(description="Whether this is a tutorial/starter project")


class SimilarRepoOutput(BaseModel):
    """Output from the Similar Repo Discovery Agent."""
    search_queries_used: list[str] = Field(description="List of search queries used")
    similar_repos: list[SimilarRepo] = Field(description="List of similar repositories found")
    is_common_tutorial_project: bool = Field(description="Whether the candidate's project is a common tutorial")
    tutorial_project_name: Optional[str] = Field(default=None, description="Name of the tutorial if applicable")
    summary: str = Field(description="2-3 sentence context about similar repos")


# ═══════════════════════════════════════════════════════════════════
# 8. PLAGIARISM & ORIGINALITY AGENT
# ═══════════════════════════════════════════════════════════════════

class PlagiarismVerdict(str, Enum):
    ORIGINAL = "ORIGINAL"
    INSPIRED = "INSPIRED"
    HEAVILY_BORROWED = "HEAVILY_BORROWED"
    COPIED = "COPIED"


class PlagiarismOutput(BaseModel):
    """Output from the Plagiarism & Originality Agent."""
    compared_against: list[str] = Field(description="List of repo URLs compared against")
    structural_match_detected: bool = Field(description="Whether structural matches were found")
    matching_repos: list[str] = Field(description="List of URLs with high structural match")
    evidence_of_copying: list[str] = Field(description="Specific evidence items of copying")
    evidence_of_originality: list[str] = Field(description="Specific original elements found")
    tutorial_remnants_found: bool = Field(description="Whether tutorial remnants were found")
    originality_score: int = Field(description="Originality score from 1-10")
    verdict: PlagiarismVerdict = Field(description="Overall plagiarism verdict")
    summary: str = Field(description="3-4 sentence verdict with evidence")


# ═══════════════════════════════════════════════════════════════════
# 9. REAL-WORLD VALUE & UNIQUENESS AGENT
# ═══════════════════════════════════════════════════════════════════

class ProjectCategory(str, Enum):
    TUTORIAL_CLONE = "TUTORIAL_CLONE"
    SATURATED_SPACE = "SATURATED_SPACE"
    INCREMENTAL = "INCREMENTAL"
    GENUINELY_USEFUL = "GENUINELY_USEFUL"
    INNOVATIVE = "INNOVATIVE"


class UniquenessOutput(BaseModel):
    """Output from the Real-World Value & Uniqueness Agent."""
    project_category: ProjectCategory = Field(description="Project category classification")
    problem_being_solved: str = Field(description="Clear 1-sentence description of the problem")
    existing_solutions: list[str] = Field(description="Major existing solutions in this space")
    candidate_differentiators: list[str] = Field(description="What makes this project different")
    real_world_relevance_score: int = Field(description="Real-world relevance score from 1-10")
    uniqueness_score: int = Field(description="Uniqueness score from 1-10")
    ambition_score: int = Field(description="Ambition score from 1-10")
    recruiter_insight: str = Field(description="What this project reveals about the candidate")
    summary: str = Field(description="3-4 sentence evaluation")


# ═══════════════════════════════════════════════════════════════════
# 10. REPORT COMPILER AGENT
# ═══════════════════════════════════════════════════════════════════

class OverallGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class RecruiterVerdict(str, Enum):
    STRONG_CANDIDATE = "STRONG CANDIDATE"
    MODERATE_CANDIDATE = "MODERATE CANDIDATE"
    WEAK_CANDIDATE = "WEAK CANDIDATE"
    DISQUALIFY = "DISQUALIFY"


class ReportCompilerOutput(BaseModel):
    """Output from the Report Compiler Agent."""
    report_path: str = Field(description="File path where the report was saved")
    composite_score: float = Field(description="Weighted composite score out of 10")
    grade: OverallGrade = Field(description="Overall project grade")
    verdict: RecruiterVerdict = Field(description="Recruiter recommendation verdict")
    report_markdown: str = Field(description="The full markdown report content")


# ═══════════════════════════════════════════════════════════════════
# ORCHESTRATOR — Aggregated Results Container
# ═══════════════════════════════════════════════════════════════════

class AgentResult(BaseModel):
    """Wrapper for an individual agent's result with status tracking."""
    agent_name: str
    status: str = Field(default="success", description="success or failed")
    error: Optional[str] = Field(default=None)
    output: Optional[dict] = Field(default=None)


class PipelineResult(BaseModel):
    """Final pipeline result containing all agent outputs."""
    repo_url: str
    owner: str
    repo_name: str
    agent_results: dict[str, AgentResult] = Field(default_factory=dict)
    report_path: Optional[str] = None
    composite_score: Optional[float] = None
    grade: Optional[str] = None
    verdict: Optional[str] = None
