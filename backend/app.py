from dotenv import load_dotenv
load_dotenv() 
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.ai_engine.schemas import (
    RawListing, 
    StudentProfile, 
    ExtractedOpportunity, 
    ScoringResult, 
    ProcessBatchResponse
)
from backend.ai_engine.pipeline import AgenticPipeline
from backend.ai_engine.sample_data import get_sample_student_profiles, get_sample_raw_listings
from backend.ai_engine.tailor import ApplicationTailorer, ApplicationPitch
from backend.ai_engine.action_plan import ActionPlanGenerator, ApplicationActionPlan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("opp_ai_agent")

app = FastAPI(
    title="Opp.ai — AI Opportunity Agent Engine",
    description="Agentic AI microservice for structured extraction, profile matching, eligibility scoring, application pitch generation, and action plans.",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = AgenticPipeline()
tailorer = ApplicationTailorer()
plan_generator = ActionPlanGenerator()

class ScoreRequest(BaseModel):
    profile: StudentProfile
    opportunity: ExtractedOpportunity

class RankRequest(BaseModel):
    profile: StudentProfile
    raw_listings: List[RawListing]

class PitchRequest(BaseModel):
    profile: StudentProfile
    opportunity: ExtractedOpportunity

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Opp.ai Engine",
        "version": "1.1.0"
    }

@app.post("/api/extract", response_model=ExtractedOpportunity)
def extract_opportunity(raw_listing: RawListing):
    try:
        return pipeline.extract_single(raw_listing)
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract-batch", response_model=List[ExtractedOpportunity])
def extract_batch(raw_listings: List[RawListing]):
    try:
        return pipeline.extract_batch(raw_listings)
    except Exception as e:
        logger.error(f"Error during batch extraction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/score", response_model=ScoringResult)
def score_opportunity(request: ScoreRequest):
    try:
        return pipeline.score_opportunity(request.profile, request.opportunity)
    except Exception as e:
        logger.error(f"Error during scoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pipeline/rank", response_model=ProcessBatchResponse)
def rank_feed(request: RankRequest):
    try:
        return pipeline.rank_for_student(request.raw_listings, request.profile)
    except Exception as e:
        logger.error(f"Error during feed ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tailor", response_model=ApplicationPitch)
def generate_pitch(request: PitchRequest):
    """
    Generate customized application elevator pitch and cover letter snippet for an opportunity.
    """
    try:
        score = pipeline.score_opportunity(request.profile, request.opportunity)
        return tailorer.generate_pitch(request.profile, request.opportunity, score)
    except Exception as e:
        logger.error(f"Error generating pitch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/action-plan", response_model=ApplicationActionPlan)
def generate_action_plan(request: PitchRequest):
    """
    Generate step-by-step checklist and application timeline.
    """
    try:
        return plan_generator.generate_plan(request.profile, request.opportunity)
    except Exception as e:
        logger.error(f"Error generating action plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/demo/run-sample")
def run_demo():
    profiles = get_sample_student_profiles()
    listings = get_sample_raw_listings()
    alex_profile = profiles[0]
    result = pipeline.rank_for_student(listings, alex_profile)
    return {
        "message": f"Successfully processed {len(listings)} listings for student '{alex_profile.name}'",
        "result": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
