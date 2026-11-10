import pytest
from fastapi.testclient import TestClient
from services.api.src.main import app
from services.api.src.services.priority import calculate_priority_score
from services.api.src.db.models import GrievanceCategory

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ai_adapters" in data
    assert data["ai_adapters"]["stt"] == "mock"
    assert data["ai_adapters"]["tts"] == "mock"

def test_priority_calculation_life_safety():
    # Life safety hazard test -> High priority >= 70
    p_high = calculate_priority_score(
        title="Fire and live electrical wire sparking on main road",
        summary="Live wire snapped and fell into water puddle near school.",
        distinct_reporters_count=1
    )
    assert p_high["priority_level"] == "high"
    assert p_high["total_score"] >= 70.0
    assert p_high["is_life_safety_override"] == True

def test_priority_calculation_routine():
    # Low priority routine complaint
    p_low = calculate_priority_score(
        title="Name spelling correction request",
        summary="Minor typo in property tax receipt.",
        distinct_reporters_count=1
    )
    assert p_low["priority_level"] == "low"
    assert p_low["total_score"] < 40.0

def test_sensitive_category_definition():
    cat = GrievanceCategory(
        code="TEST_CORRUPT",
        name_en="Corruption Complaint",
        name_ta="லஞ்ச புகார்",
        is_sensitive=True
    )
    assert cat.is_sensitive == True
