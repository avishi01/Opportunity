import logging
from typing import Optional
from pydantic import BaseModel
from backend.ai_engine.schemas import StudentProfile, ExtractedOpportunity, ScoringResult

logger = logging.getLogger(__name__)

class ApplicationPitch(BaseModel):
    opportunity_id: str
    student_id: str
    elevator_pitch: str
    cover_letter_snippet: str
    key_talking_points: list[str]

class ApplicationTailorer:
    """
    Agentic AI Module that generates customized cover letter snippets, 
    elevator pitches, and key talking points for a student applying to a specific opportunity.
    """

    def generate_pitch(
        self, profile: StudentProfile, opportunity: ExtractedOpportunity, score: ScoringResult
    ) -> ApplicationPitch:
        matched_skills = [s for s in opportunity.required_skills if any(ps.lower() == s.lower() for ps in profile.skills)]
        display_skills = ", ".join(matched_skills[:3]) if matched_skills else ", ".join(profile.skills[:3])
        
        # Elevator Pitch (1-2 sentences)
        elevator_pitch = (
            f"Hi! I'm {profile.name}, a {profile.degree} student in {profile.major} at expected graduation {profile.graduation_year}. "
            f"I have strong hands-on experience in {display_skills} and am deeply passionate about {opportunity.organization}'s work in {opportunity.title}."
        )

        # Cover Letter Snippet (2 paragraphs)
        cover_letter_snippet = (
            f"Dear Hiring Team at {opportunity.organization},\n\n"
            f"I am writing to express my enthusiastic interest in the {opportunity.title} position. "
            f"As a {profile.degree} candidate in {profile.major} with a {profile.gpa if profile.gpa else 'strong'} GPA, "
            f"I have built technical expertise in {display_skills}. My background directly aligns with your focus on "
            f"{', '.join(opportunity.tags[:3]) if opportunity.tags else 'technology innovation'}.\n\n"
            f"What excites me most about {opportunity.organization} is the opportunity to contribute to {opportunity.summary[:120]}... "
            f"I look forward to discussing how my skills in {display_skills} can add immediate value to your team.\n\n"
            f"Sincerely,\n{profile.name}"
        )

        # Key Talking Points for Interviews
        talking_points = [
            f"Highlight background in {profile.major} (Graduating {profile.graduation_year}).",
            f"Emphasize matched technical skills: {display_skills}.",
            f"Demonstrate alignment with {opportunity.organization}'s mission in {opportunity.category.value}."
        ]
        if score.eligibility_gaps:
            talking_points.append(f"Proactively address criteria: {score.eligibility_gaps[0]}")

        return ApplicationPitch(
            opportunity_id=opportunity.id,
            student_id=profile.id,
            elevator_pitch=elevator_pitch,
            cover_letter_snippet=cover_letter_snippet,
            key_talking_points=talking_points
        )
