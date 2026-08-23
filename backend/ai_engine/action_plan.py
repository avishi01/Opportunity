import logging
from pydantic import BaseModel
from backend.ai_engine.schemas import StudentProfile, ExtractedOpportunity

logger = logging.getLogger(__name__)

class ActionStep(BaseModel):
    step_number: int
    title: str
    description: str
    target_timeline: str

class ApplicationActionPlan(BaseModel):
    opportunity_id: str
    student_id: str
    opportunity_title: str
    deadline: str
    steps: list[ActionStep]

class ActionPlanGenerator:
    """
    Agentic AI Module that generates a step-by-step preparation timeline
    and checklist for a student applying to an opportunity.
    """

    def generate_plan(self, profile: StudentProfile, opportunity: ExtractedOpportunity) -> ApplicationActionPlan:
        matched_skills = [s for s in opportunity.required_skills if any(ps.lower() == s.lower() for ps in profile.skills)]
        missing_skills = [s for s in opportunity.required_skills if s not in matched_skills]

        steps = [
            ActionStep(
                step_number=1,
                title="Profile & Resume Alignment",
                description=f"Tailor resume bullet points to emphasize key skills: {', '.join(opportunity.required_skills[:3]) if opportunity.required_skills else profile.major}.",
                target_timeline="Day 1"
            ),
            ActionStep(
                step_number=2,
                title="Prepare Cover Letter / Pitch",
                description=f"Draft custom application snippet highlighting your work at {opportunity.organization}.",
                target_timeline="Day 2"
            )
        ]

        if missing_skills:
            steps.append(
                ActionStep(
                    step_number=3,
                    title=f"Review Bonus Skill: {missing_skills[0]}",
                    description=f"Complete a quick tutorial or highlight transferable project experience in {missing_skills[0]}.",
                    target_timeline="Day 3-4"
                )
            )

        steps.append(
            ActionStep(
                step_number=len(steps) + 1,
                title="Submit Application & Confirmation",
                description=f"Submit application before deadline ({opportunity.deadline or 'Rolling'}). Save submission confirmation.",
                target_timeline=f"Before {opportunity.deadline or 'Deadline'}"
            )
        )

        return ApplicationActionPlan(
            opportunity_id=opportunity.id,
            student_id=profile.id,
            opportunity_title=opportunity.title,
            deadline=opportunity.deadline or "Rolling Basis",
            steps=steps
        )
