"""Smoke tests for FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "VeriDocs AI" in data["message"]


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "VeriDocs AI"


def test_config():
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert data["active_extractor_backend"] == "ocr_rules"
    assert data["limits"]["max_file_size_mb"] == 10
