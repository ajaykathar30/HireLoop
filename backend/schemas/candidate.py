from pydantic import BaseModel
from typing import Optional

class CandidateUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    experience_years: Optional[int] = None
