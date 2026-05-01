"""
RecruitSight — LinkedIn Pydantic I/O Schemas
All structured output models used by the 5 LinkedIn analysis agents.
These are passed to the Gemini `response_schema` parameter.

NOTE: These schemas are intentionally SEPARATE from the GitHub schemas
      in schemas.py. LinkedIn and GitHub reports are independent.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════
# 1. LINKEDIN PROFILE INTELLIGENCE AGENT
# ═══════════════════════════════════════════════════════════════════

class AboutSectionQuality(str, Enum):
    MISSING = "missing"
    GENERIC = "generic"
    PERSONALIZED = "personalized"
    COMPELLING = "compelling"


class EmploymentEntry(BaseModel):
    """A single employment record from the candidate's timeline."""
    company: str = Field(description="Company name")
    role: str = Field(description="Job title / role")
    start: str = Field(description="Start date (e.g. Jan 2022)")
    end: str = Field(description="End date or 'Present'")
    duration_months: int = Field(description="Duration in months")
    description_summary: Optional[str] = Field(default=None, description="Brief summary of role description if available")


class EducationEntry(BaseModel):
    """A single education record."""
    degree: str = Field(description="Degree obtained")
    institution: str = Field(description="University / institution name")
    year: str = Field(description="Graduation year or date range")


class CertificationEntry(BaseModel):
    """A single certification record."""
    name: str = Field(description="Certification name")
    issuer: str = Field(description="Issuing organization")
    date: str = Field(description="Date obtained")
    relevant: bool = Field(description="Whether this cert is relevant to the candidate's claimed role")


class LinkedInProfileOutput(BaseModel):
    """Output from the LinkedIn Profile Intelligence Agent."""
    full_name: str = Field(description="Candidate's full name")
    headline: str = Field(description="LinkedIn headline")
    location: str = Field(description="City, country")
    current_role: str = Field(description="Current role at company")
    total_experience_years: float = Field(description="Total years of professional experience")
    employment_timeline: list[EmploymentEntry] = Field(description="Full employment timeline")
    employment_gaps: list[str] = Field(description="Employment gaps longer than 6 months")
    promotions_detected: list[str] = Field(description="Promotions detected within same company")
    education: list[EducationEntry] = Field(description="Education records")
    top_skills: list[str] = Field(description="Top skills with endorsement counts if visible")
    certifications: list[CertificationEntry] = Field(description="Certifications")
    honors_awards: list[str] = Field(description="Honors and awards")
    linkedin_projects: list[str] = Field(description="Projects listed on LinkedIn profile")
    profile_completeness_score: int = Field(description="Profile completeness score from 1-10")
    about_section_quality: AboutSectionQuality = Field(description="Quality of the About section")
    consistency_flags: list[str] = Field(description="Consistency issues found")
    summary: str = Field(description="3-4 sentence professional snapshot")


# ═══════════════════════════════════════════════════════════════════
# 2. LINKEDIN CONTENT & THOUGHT LEADERSHIP AGENT
# ═══════════════════════════════════════════════════════════════════

class PostingFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    RARE = "rare"
    NONE = "none"


class ExpertiseAlignment(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    NONE = "none"


class CommunicationQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"


class ThoughtLeadershipLevel(str, Enum):
    NONE = "none"
    EMERGING = "emerging"
    ESTABLISHED = "established"
    INFLUENTIAL = "influential"


class ContentTypeBreakdown(BaseModel):
    """Breakdown of content types as percentages."""
    technical: str = Field(description="Percentage of technical posts")
    career_updates: str = Field(description="Percentage of career update posts")
    motivational: str = Field(description="Percentage of motivational posts")
    reshares: str = Field(description="Percentage of reshares")


class LinkedInContentOutput(BaseModel):
    """Output from the LinkedIn Content & Thought Leadership Agent."""
    total_posts_analyzed: int = Field(description="Number of posts analyzed")
    posting_frequency: PostingFrequency = Field(description="How frequently the candidate posts")
    primary_topics: list[str] = Field(description="Primary topics the candidate posts about")
    content_type_breakdown: ContentTypeBreakdown = Field(description="Breakdown of content types")
    avg_engagement_per_post: Optional[int] = Field(default=None, description="Average engagement per post")
    expertise_alignment: ExpertiseAlignment = Field(description="How well posts align with claimed expertise")
    communication_quality: CommunicationQuality = Field(description="Quality of writing/communication")
    thought_leadership_level: ThoughtLeadershipLevel = Field(description="Thought leadership level")
    red_flags: list[str] = Field(description="Content-related red flags")
    notable_posts: list[str] = Field(description="1-2 standout posts with topic and why")
    content_score: int = Field(description="Content & thought leadership score from 1-10")
    summary: str = Field(description="2-3 sentence content evaluation")


# ═══════════════════════════════════════════════════════════════════
# 3. LINKEDIN INTERACTION & ENGAGEMENT AGENT
# ═══════════════════════════════════════════════════════════════════

class CommentQuality(str, Enum):
    SUBSTANTIVE = "substantive"
    MIXED = "mixed"
    SURFACE_LEVEL = "surface-level"
    NONE = "none"


class ProfessionalTone(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    CONCERNING = "concerning"


class InteractionTargets(BaseModel):
    """Who the candidate interacts with, by percentage."""
    seniors_leaders: str = Field(description="Percentage interacting with seniors/leaders")
    peers: str = Field(description="Percentage interacting with peers")
    juniors_students: str = Field(description="Percentage interacting with juniors/students")
    recruiters: str = Field(description="Percentage interacting with recruiters")


class LinkedInInteractionOutput(BaseModel):
    """Output from the LinkedIn Interaction & Engagement Agent."""
    comment_quality: CommentQuality = Field(description="Quality of comments on others' posts")
    interaction_targets: InteractionTargets = Field(description="Who they interact with")
    collaboration_signals: list[str] = Field(description="Specific evidence of collaboration")
    professional_tone: ProfessionalTone = Field(description="Professional tone in interactions")
    red_flags: list[str] = Field(description="Interaction-related red flags")
    positive_signals: list[str] = Field(description="Positive interaction signals")
    interaction_score: int = Field(description="Interaction & engagement score from 1-10")
    personality_insight: str = Field(description="1-2 sentence insight on what interaction style reveals")
    summary: str = Field(description="2-3 sentence evaluation")


# ═══════════════════════════════════════════════════════════════════
# 4. LINKEDIN ACHIEVEMENT & CREDIBILITY AGENT
# ═══════════════════════════════════════════════════════════════════

class CertRelevance(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNRELATED = "unrelated"


class IssuerCredibility(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CertificationPattern(str, Enum):
    SPECIALIST = "specialist"
    GENERALIST = "generalist"
    CERT_COLLECTOR = "cert-collector"
    MINIMAL = "minimal"
    NONE = "none"


class SkillEndorsementCredibility(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    SUSPICIOUS = "suspicious"


class HonorType(str, Enum):
    EXTERNAL = "external"
    SELF_REPORTED = "self-reported"


class CertEvaluation(BaseModel):
    """Detailed evaluation of a single certification."""
    name: str = Field(description="Certification name")
    issuer: str = Field(description="Issuing organization")
    date: str = Field(description="Date obtained")
    relevance: CertRelevance = Field(description="Relevance to claimed role")
    is_current: bool = Field(description="Whether the cert is still current")
    issuer_credibility: IssuerCredibility = Field(description="Credibility of the issuer")


class HonorEvaluation(BaseModel):
    """Evaluation of a single honor or award."""
    name: str = Field(description="Honor/award name")
    issuer: str = Field(description="Issuing organization")
    year: str = Field(description="Year received")
    type: HonorType = Field(description="Whether external or self-reported")


class LinkedInCredibilityOutput(BaseModel):
    """Output from the LinkedIn Achievement & Credibility Agent."""
    certifications_evaluated: list[CertEvaluation] = Field(description="Detailed cert evaluations")
    certification_pattern: CertificationPattern = Field(description="Overall certification pattern")
    skill_endorsement_credibility: SkillEndorsementCredibility = Field(description="Skill endorsement credibility")
    honors_awards: list[HonorEvaluation] = Field(description="Evaluated honors and awards")
    notable_absences: list[str] = Field(description="Expected certs that are missing")
    red_flags: list[str] = Field(description="Credibility red flags")
    strengths: list[str] = Field(description="Credibility strengths")
    credibility_score: int = Field(description="Credibility score from 1-10")
    recruiter_insight: str = Field(description="2-sentence insight on credentials pattern")
    summary: str = Field(description="2-3 sentence credibility verdict")


# ═══════════════════════════════════════════════════════════════════
# 5. LINKEDIN REPORT COMPILER AGENT
# ═══════════════════════════════════════════════════════════════════

class LinkedInGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class LinkedInVerdict(str, Enum):
    STRONG_PROFILE = "STRONG PROFILE"
    SOLID_PROFILE = "SOLID PROFILE"
    AVERAGE_PROFILE = "AVERAGE PROFILE"
    WEAK_PROFILE = "WEAK PROFILE"
    INCOMPLETE = "INCOMPLETE"


class LinkedInReportOutput(BaseModel):
    """Output from the LinkedIn Report Compiler Agent."""
    report_path: str = Field(description="File path where the LinkedIn report was saved")
    composite_score: float = Field(description="Weighted composite score out of 10")
    grade: LinkedInGrade = Field(description="Overall LinkedIn grade")
    verdict: LinkedInVerdict = Field(description="LinkedIn profile verdict")
    report_markdown: str = Field(description="The full markdown report content")


# ═══════════════════════════════════════════════════════════════════
# LINKEDIN ORCHESTRATOR — Pipeline Result Container
# ═══════════════════════════════════════════════════════════════════

class LinkedInAgentResult(BaseModel):
    """Wrapper for an individual LinkedIn agent's result with status tracking."""
    agent_name: str
    status: str = Field(default="success", description="success or failed")
    error: Optional[str] = Field(default=None)
    output: Optional[dict] = Field(default=None)


class LinkedInPipelineResult(BaseModel):
    """Final LinkedIn pipeline result containing all agent outputs."""
    linkedin_url: str
    candidate_name: str = Field(default="")
    agent_results: dict[str, LinkedInAgentResult] = Field(default_factory=dict)
    report_path: Optional[str] = None
    composite_score: Optional[float] = None
    grade: Optional[str] = None
    verdict: Optional[str] = None
