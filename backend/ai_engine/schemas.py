from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CategoryEnum(str, Enum):
    INTERNSHIP = "internship"
    SCHOLARSHIP = "scholarship"
    HACKATHON = "hackathon"
    RESEARCH = "research"

class StudentProfile(BaseModel):
    id: str = Field(..., description="Unique student ID")
    name: str = Field(..., description="Full name of student")
    degree: str = Field(..., description="Current degree level (e.g. B.S., M.S., Ph.D.)")
    major: str = Field(..., description="Field of study / Major")
    gpa: Optional[float] = Field(None, description="Cumulative GPA out of 4.0")
    graduation_year: int = Field(..., description="Expected graduation year (e.g., 2026)")
    location: str = Field(..., description="Current location or preferred region")
    skills: List[str] = Field(default_factory=list, description="List of technical and soft skills")
    interests: List[str] = Field(default_factory=list, description="List of domains or focus areas of interest")
    citizenship_or_authorization: List[str] = Field(
        default_factory=list, 
        description="Work authorization / citizenship status (e.g. US Citizen, Green Card, F-1 OPT, Needs Sponsorship)"
    )
    preferred_categories: List[CategoryEnum] = Field(
        default_factory=lambda: [CategoryEnum.INTERNSHIP, CategoryEnum.SCHOLARSHIP, CategoryEnum.HACKATHON, CategoryEnum.RESEARCH],
        description="Categories the student wants to prioritize"
    )

class RawListing(BaseModel):
    id: str = Field(..., description="Unique raw listing ID")
    source_name: str = Field(..., description="Name of the source site/portal")
    source_url: Optional[str] = Field(None, description="URL of origin")
    raw_text: str = Field(..., description="Unstructured raw text content of the posting")
    ingested_at: str = Field(..., description="Ingestion timestamp ISO format")

class EligibilityCriteria(BaseModel):
    min_gpa: Optional[float] = Field(None, description="Minimum GPA required, if any")
    allowed_majors: List[str] = Field(default_factory=list, description="Allowed majors or fields of study (empty means all)")
    graduation_years: List[int] = Field(default_factory=list, description="Target graduation years (empty means all)")
    target_degrees: List[str] = Field(default_factory=list, description="Target degree levels (e.g. B.S., M.S.)")
    location_requirement: str = Field("Flexible", description="Geographic or citizenship restrictions")
    work_authorization: List[str] = Field(default_factory=list, description="Required work authorization status")

class ExtractedOpportunity(BaseModel):
    id: str = Field(..., description="Unique opportunity ID")
    title: str = Field(..., description="Title of the role, scholarship, hackathon, or lab")
    organization: str = Field(..., description="Company, university, or host organization")
    category: CategoryEnum = Field(..., description="Opportunity classification")
    location: str = Field("Remote", description="Primary location or remote status")
    is_remote: bool = Field(True, description="Whether remote participation is allowed")
    deadline: Optional[str] = Field(None, description="Application deadline (ISO format YYYY-MM-DD or readable string)")
    eligibility: EligibilityCriteria = Field(default_factory=EligibilityCriteria, description="Extracted eligibility rules")
    required_skills: List[str] = Field(default_factory=list, description="Extracted required/preferred skills")
    tags: List[str] = Field(default_factory=list, description="Topic tags (e.g. AI, Systems, Diversity, Machine Learning)")
    summary: str = Field(..., description="2-3 sentence clear summary of the opportunity")
    apply_url: Optional[str] = Field(None, description="Direct URL to apply")
    extraction_confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score of AI extraction")

class HardEligibilityCheck(BaseModel):
    passed: bool = Field(..., description="Whether the student satisfies all strict requirements")
    gpa_check: Dict[str, Any] = Field(default_factory=dict, description="Details on GPA evaluation")
    grad_year_check: Dict[str, Any] = Field(default_factory=dict, description="Details on graduation year evaluation")
    major_check: Dict[str, Any] = Field(default_factory=dict, description="Details on major evaluation")
    degree_check: Dict[str, Any] = Field(default_factory=dict, description="Details on degree evaluation")
    reasons: List[str] = Field(default_factory=list, description="List of hard eligibility failures or passes")

class ScoringResult(BaseModel):
    opportunity_id: str = Field(..., description="Target opportunity ID")
    student_id: str = Field(..., description="Target student ID")
    hard_eligibility: HardEligibilityCheck = Field(..., description="Deterministic hard eligibility check results")
    relevance_score: float = Field(..., ge=0.0, le=100.0, description="Overall match score out of 100")
    overall_fit: str = Field(..., description="Classification: Strong Match, Good Match, Partial Match, or Ineligible")
    match_highlights: List[str] = Field(default_factory=list, description="Key reasons why this is a good match")
    eligibility_gaps: List[str] = Field(default_factory=list, description="Any gaps or warnings (e.g. GPA below requirement)")
    recommendation_reason: str = Field(..., description="Summary paragraph of AI recommendation")

class RankedFeedItem(BaseModel):
    opportunity: ExtractedOpportunity
    score: ScoringResult

class ProcessBatchResponse(BaseModel):
    student_id: str
    total_processed: int
    ranked_feed: List[RankedFeedItem]
