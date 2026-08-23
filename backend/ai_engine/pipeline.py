import logging
from typing import List, Optional
from backend.ai_engine.schemas import (
    RawListing, 
    StudentProfile, 
    ExtractedOpportunity, 
    ScoringResult, 
    RankedFeedItem, 
    ProcessBatchResponse
)
from backend.ai_engine.extractor import OpportunityExtractor
from backend.ai_engine.scorer import OpportunityScorer

logger = logging.getLogger(__name__)

class AgenticPipeline:
    """
    End-to-end Agentic Pipeline for AI Opportunity Agent.
    Handles ingestion of raw text -> AI Extraction -> AI Eligibility & Fit Scoring -> Ranked Feed output.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.extractor = OpportunityExtractor(api_key=api_key)
        self.scorer = OpportunityScorer()

    def extract_single(self, raw_listing: RawListing) -> ExtractedOpportunity:
        """Extract structured fields from a single raw listing."""
        return self.extractor.extract(raw_listing)

    def extract_batch(self, raw_listings: List[RawListing]) -> List[ExtractedOpportunity]:
        """Extract structured fields from multiple raw listings."""
        return [self.extractor.extract(r) for r in raw_listings]

    def score_opportunity(
        self, profile: StudentProfile, opportunity: ExtractedOpportunity
    ) -> ScoringResult:
        """Score a single opportunity against a student profile."""
        return self.scorer.score(profile, opportunity)

    def rank_for_student(
        self, raw_listings: List[RawListing], profile: StudentProfile
    ) -> ProcessBatchResponse:
        """
        Full end-to-end pipeline:
        1. Extract structured data for all raw listings.
        2. Score each opportunity against the target student profile.
        3. Sort opportunities by overall score descending.
        4. Return formatted RankedFeed response.
        """
        extracted_list = self.extract_batch(raw_listings)
        feed_items: List[RankedFeedItem] = []

        for opp in extracted_list:
            score_result = self.score_opportunity(profile, opp)
            feed_items.append(RankedFeedItem(opportunity=opp, score=score_result))

        # Sort feed items by relevance score descending
        # Secondary sort by hard eligibility pass status
        feed_items.sort(
            key=lambda item: (item.score.hard_eligibility.passed, item.score.relevance_score),
            reverse=True
        )

        return ProcessBatchResponse(
            student_id=profile.id,
            total_processed=len(feed_items),
            ranked_feed=feed_items
        )
