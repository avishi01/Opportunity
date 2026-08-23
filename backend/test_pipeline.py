import sys
import json
import logging
from pprint import pprint

# Ensure UTF-8 output formatting on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from backend.ai_engine.schemas import StudentProfile, RawListing, CategoryEnum
from backend.ai_engine.pipeline import AgenticPipeline
from backend.ai_engine.sample_data import get_sample_student_profiles, get_sample_raw_listings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_pipeline")

def print_separator(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)

def run_tests():
    print_separator("1. Initializing Agentic AI Pipeline")
    pipeline = AgenticPipeline()
    print("[OK] Pipeline initialized successfully.")

    profiles = get_sample_student_profiles()
    listings = get_sample_raw_listings()

    print(f"Loaded {len(profiles)} sample student profiles.")
    print(f"Loaded {len(listings)} raw opportunity listings.")

    # Test 1: Single Extraction
    print_separator("2. Testing AI Extraction on Raw Listings")
    extracted_opps = []
    for idx, raw in enumerate(listings, 1):
        extracted = pipeline.extract_single(raw)
        extracted_opps.append(extracted)
        print(f"\n--- Listing #{idx} [{raw.source_name}] ---")
        print(f"Title:       {extracted.title}")
        print(f"Org:         {extracted.organization}")
        print(f"Category:    {extracted.category.value.upper()}")
        print(f"Location:    {extracted.location} (Remote: {extracted.is_remote})")
        print(f"Deadline:    {extracted.deadline}")
        print(f"Min GPA:     {extracted.eligibility.min_gpa}")
        print(f"Skills:      {', '.join(extracted.required_skills) if extracted.required_skills else 'None'}")
        print(f"Tags:        {', '.join(extracted.tags) if extracted.tags else 'None'}")
        print(f"Confidence:  {extracted.extraction_confidence}")

    # Test 2: Multi-Persona Ranking & Personalization
    print_separator("3. Testing Multi-Persona Personalization & Feed Ranking")
    
    for student in profiles:
        print(f"\n" + "-" * 70)
        print(f"STUDENT PERSONA: {student.name}")
        print(f"   Degree: {student.degree} in {student.major} | GPA: {student.gpa} | Grad Year: {student.graduation_year}")
        print(f"   Skills: {', '.join(student.skills)}")
        print(f"   Interests: {', '.join(student.interests)}")
        print("-" * 70)

        response = pipeline.rank_for_student(listings, student)
        
        print(f"\nRANKED FEED FOR {student.name.upper()} (Top Matches First):")
        for rank, item in enumerate(response.ranked_feed, 1):
            opp = item.opportunity
            score = item.score
            pass_status = "[ELIGIBLE]" if score.hard_eligibility.passed else "[INELIGIBLE/GAP]"
            
            print(f"\n  #{rank}. [{score.overall_fit.upper()}] {opp.title} @ {opp.organization}")
            print(f"      Score: {score.relevance_score}/100 | Status: {pass_status} | Category: {opp.category.value}")
            print(f"      Recommendation: {score.recommendation_reason}")
            if score.match_highlights:
                print(f"      Highlights: {', '.join(score.match_highlights[:3])}")
            if score.eligibility_gaps:
                print(f"      Eligibility Gaps: {', '.join(score.eligibility_gaps)}")

    # Test 3: Validate JSON Output Contract
    print_separator("4. Validating Backend JSON Output Contract")
    sample_response = pipeline.rank_for_student(listings, profiles[0])
    json_output = sample_response.model_dump_json(indent=2)
    
    # Verify valid JSON parse
    parsed = json.loads(json_output)
    assert "student_id" in parsed
    assert "ranked_feed" in parsed
    assert len(parsed["ranked_feed"]) == len(listings)
    
    print(f"[OK] JSON Schema Validation Passed!")
    print(f"Sample Payload Keys verified: {list(parsed.keys())}")
    print(f"Sample Ranked Item Keys: {list(parsed['ranked_feed'][0].keys())}")

    print_separator("All AI Engine Verification Tests Passed Successfully!")

if __name__ == "__main__":
    run_tests()
