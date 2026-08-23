import sys
from fastapi.testclient import TestClient

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from backend.app import app
from backend.ai_engine.sample_data import get_sample_student_profiles, get_sample_raw_listings

def test_api():
    client = TestClient(app)
    
    # 1. Health check
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("[OK] /health endpoint passed!")

    # 2. Extract single
    listings = get_sample_raw_listings()
    raw_dict = listings[0].model_dump()
    response = client.post("/api/extract", json=raw_dict)
    assert response.status_code == 200
    extracted_data = response.json()
    assert "title" in extracted_data
    assert extracted_data["category"] == "internship"
    print("[OK] /api/extract endpoint passed!")

    # 3. Pipeline Rank
    profiles = get_sample_student_profiles()
    rank_payload = {
        "profile": profiles[0].model_dump(),
        "raw_listings": [l.model_dump() for l in listings]
    }
    response = client.post("/api/pipeline/rank", json=rank_payload)
    assert response.status_code == 200
    rank_data = response.json()
    assert rank_data["total_processed"] == len(listings)
    assert len(rank_data["ranked_feed"]) == len(listings)
    print("[OK] /api/pipeline/rank endpoint passed!")

    # 4. Demo endpoint
    response = client.get("/api/demo/run-sample")
    assert response.status_code == 200
    print("[OK] /api/demo/run-sample endpoint passed!")

    print("\nAll FastAPI Microservice Endpoints Tested and Operational!")

if __name__ == "__main__":
    test_api()
