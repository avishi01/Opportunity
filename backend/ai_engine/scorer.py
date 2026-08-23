import logging
from typing import List, Dict, Any, Tuple
from backend.ai_engine.schemas import (
    StudentProfile, 
    ExtractedOpportunity, 
    ScoringResult, 
    HardEligibilityCheck
)

logger = logging.getLogger(__name__)

class OpportunityScorer:
    """
    AI Match & Ranking Engine that compares student profiles against 
    extracted opportunity specifications. Performs deterministic hard-eligibility 
    validation + semantic fit scoring and generates human-readable match rationales.
    """

    def score(self, profile: StudentProfile, opportunity: ExtractedOpportunity) -> ScoringResult:
        # 1. Hard Eligibility Check
        hard_check = self._evaluate_hard_eligibility(profile, opportunity)

        # 2. Soft Relevance Score Calculation (0 - 100)
        relevance_score, highlights = self._calculate_relevance(profile, opportunity)

        # 3. Apply Hard Check Penalty if failed
        gaps = list(hard_check.reasons)
        if not hard_check.passed:
            relevance_score = max(0.0, relevance_score - 30.0)

        # Round relevance score
        relevance_score = round(relevance_score, 1)

        # 4. Classify Overall Fit
        if not hard_check.passed and relevance_score < 50:
            overall_fit = "Ineligible"
        elif relevance_score >= 80:
            overall_fit = "Strong Match"
        elif relevance_score >= 65:
            overall_fit = "Good Match"
        else:
            overall_fit = "Partial Match"

        # 5. Recommendation Synthesis
        recommendation = self._synthesize_recommendation(
            profile, opportunity, overall_fit, relevance_score, highlights, gaps
        )

        return ScoringResult(
            opportunity_id=opportunity.id,
            student_id=profile.id,
            hard_eligibility=hard_check,
            relevance_score=relevance_score,
            overall_fit=overall_fit,
            match_highlights=highlights,
            eligibility_gaps=gaps,
            recommendation_reason=recommendation
        )

    def _evaluate_hard_eligibility(
        self, profile: StudentProfile, opportunity: ExtractedOpportunity
    ) -> HardEligibilityCheck:
        reasons = []
        passed = True

        # GPA Check
        gpa_info = {"student_gpa": profile.gpa, "required_min_gpa": opportunity.eligibility.min_gpa}
        if opportunity.eligibility.min_gpa is not None and profile.gpa is not None:
            if profile.gpa < opportunity.eligibility.min_gpa:
                passed = False
                reasons.append(
                    f"GPA restriction: Required minimum is {opportunity.eligibility.min_gpa}, but student GPA is {profile.gpa}."
                )
            else:
                gpa_info["status"] = "PASSED"

        # Graduation Year Check
        grad_info = {
            "student_grad_year": profile.graduation_year,
            "target_grad_years": opportunity.eligibility.graduation_years
        }
        if opportunity.eligibility.graduation_years:
            if profile.graduation_year not in opportunity.eligibility.graduation_years:
                # Slight flexibility: allow +- 1 year warning
                if abs(profile.graduation_year - min(opportunity.eligibility.graduation_years)) > 1:
                    passed = False
                    reasons.append(
                        f"Graduation year mismatch: Opportunity targets {opportunity.eligibility.graduation_years}, student graduates in {profile.graduation_year}."
                    )

        # Major Check
        major_info = {
            "student_major": profile.major,
            "allowed_majors": opportunity.eligibility.allowed_majors
        }
        if opportunity.eligibility.allowed_majors:
            major_matched = any(
                m.lower() in profile.major.lower() or profile.major.lower() in m.lower()
                for m in opportunity.eligibility.allowed_majors
            )
            if not major_matched and "all" not in [m.lower() for m in opportunity.eligibility.allowed_majors]:
                passed = False
                reasons.append(
                    f"Major requirement gap: Targeted majors are {', '.join(opportunity.eligibility.allowed_majors)}, but student major is '{profile.major}'."
                )

        # Degree Check
        degree_info = {
            "student_degree": profile.degree,
            "target_degrees": opportunity.eligibility.target_degrees
        }
        if opportunity.eligibility.target_degrees:
            degree_matched = any(
                d.lower() in profile.degree.lower() or profile.degree.lower() in d.lower()
                for d in opportunity.eligibility.target_degrees
            )
            if not degree_matched:
                reasons.append(
                    f"Degree level caution: Targeted degrees are {', '.join(opportunity.eligibility.target_degrees)}."
                )

        # Location Check
        loc_info = {
            "student_location": profile.location,
            "is_remote": opportunity.is_remote,
            "opp_location": opportunity.location
        }

        return HardEligibilityCheck(
            passed=passed,
            gpa_check=gpa_info,
            grad_year_check=grad_info,
            major_check=major_info,
            degree_check=degree_info,
            location_check=loc_info,
            reasons=reasons
        )

    def _calculate_relevance(
        self, profile: StudentProfile, opportunity: ExtractedOpportunity
    ) -> Tuple[float, List[str]]:
        score = 0.0
        highlights = []

        # 1. Preferred Category Score (20 pts)
        if opportunity.category in profile.preferred_categories:
            score += 20.0
            highlights.append(f"Category '{opportunity.category.value.capitalize()}' matches student preferences.")

        # 2. Technical Skill Match (35 pts)
        if opportunity.required_skills and profile.skills:
            profile_skills_lower = {s.lower() for s in profile.skills}
            opp_skills_lower = {s.lower() for s in opportunity.required_skills}
            
            matched_skills = profile_skills_lower.intersection(opp_skills_lower)
            match_ratio = len(matched_skills) / max(1, len(opp_skills_lower))
            skill_pts = min(35.0, match_ratio * 35.0 + len(matched_skills) * 3.0)
            score += skill_pts
            
            if matched_skills:
                display_matched = [s.capitalize() for s in matched_skills]
                highlights.append(f"Matches {len(matched_skills)} required skill(s): {', '.join(display_matched)}.")
        else:
            score += 15.0  # General baseline if no specific skills listed

        # 3. Domain & Interest Overlap (25 pts)
        profile_interests_lower = {i.lower() for i in profile.interests}
        opp_tags_lower = {t.lower() for t in opportunity.tags}
        
        domain_matches = profile_interests_lower.intersection(opp_tags_lower)
        # Also check if interest keywords are in title/summary
        text_content = f"{opportunity.title} {opportunity.summary}".lower()
        keyword_matches = [i for i in profile_interests_lower if i in text_content]

        total_interest_hits = set(list(domain_matches) + keyword_matches)
        if total_interest_hits:
            interest_pts = min(25.0, len(total_interest_hits) * 8.5)
            score += interest_pts
            highlights.append(f"Aligns with core student interests: {', '.join([i.capitalize() for i in total_interest_hits])}.")
        else:
            score += 10.0

        # 4. Location / Remote Preference (10 pts)
        if opportunity.is_remote:
            score += 10.0
            highlights.append("Remote-friendly opportunity.")
        elif profile.location.lower() in opportunity.location.lower():
            score += 10.0
            highlights.append(f"Location match ({opportunity.location}).")
        else:
            score += 5.0

        # 5. GPA / Academic Standing Bonus (10 pts)
        if profile.gpa is not None and profile.gpa >= 3.5:
            score += 10.0
            highlights.append(f"Strong academic record (GPA {profile.gpa}).")
        elif profile.gpa is not None:
            score += 5.0

        return min(100.0, score), highlights

    def _synthesize_recommendation(
        self,
        profile: StudentProfile,
        opportunity: ExtractedOpportunity,
        overall_fit: str,
        score: float,
        highlights: List[str],
        gaps: List[str]
    ) -> str:
        if overall_fit == "Strong Match":
            return (
                f"Highly Recommended ({score}/100): '{opportunity.title}' at {opportunity.organization} is an exceptional fit "
                f"for {profile.name}. Key alignments include strong skill overlap ({', '.join(highlights[:2])})."
            )
        elif overall_fit == "Good Match":
            return (
                f"Recommended ({score}/100): '{opportunity.title}' at {opportunity.organization} matches {profile.name}'s profile well. "
                f"Good domain overlap with minor criteria to verify."
            )
        elif overall_fit == "Partial Match":
            gap_summary = gaps[0] if gaps else "some skill gaps"
            return (
                f"Consider Applying ({score}/100): '{opportunity.title}' matches some of {profile.name}'s interests, "
                f"but has noticeable eligibility criteria or skill mismatches ({gap_summary})."
            )
        else:
            return (
                f"Ineligible ({score}/100): '{opportunity.title}' at {opportunity.organization} has hard eligibility "
                f"restrictions that {profile.name} does not meet: {'; '.join(gaps)}."
            )
