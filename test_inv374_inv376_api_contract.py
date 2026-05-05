"""INV-374/INV-376 API contract regression tests."""

from fastapi.testclient import TestClient

from backend.api.main import app
from backend.config import settings


def test_frontend_live_data_contract_endpoint_exists(monkeypatch):
    monkeypatch.setattr(settings, "WEATHER_ENABLED", False)
    monkeypatch.setattr(settings, "BTC_ENABLED", False)

    response = TestClient(app).get("/api/data")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) >= {
        "ts",
        "kalshi",
        "polymarket",
        "lifetime",
        "metar_lines",
        "metar_poly_lines",
        "metar_v2_signals",
        "system",
    }
    assert isinstance(payload["system"]["services"], list)
    assert isinstance(payload["system"]["socks_up"], bool)


def test_frontend_market_contract_endpoints_exist(monkeypatch):
    monkeypatch.setattr(settings, "WEATHER_ENABLED", False)

    client = TestClient(app)
    kalshi_response = client.get("/api/kalshi/markets")
    poly_response = client.get("/api/polymarket/markets")

    assert kalshi_response.status_code == 200
    assert kalshi_response.json() == {
        "markets": [],
        "count": 0,
        "traded_today_count": 0,
    }
    assert poly_response.status_code == 200
    assert poly_response.json() == {"markets": [], "count": 0}


def test_bot_start_stop_controls_toggle_state():
    client = TestClient(app)

    stopped = client.post("/api/bot/stop")
    assert stopped.status_code == 200
    assert stopped.json()["is_running"] is False
    assert client.get("/api/data").json()["system"]["services"][0]["running"] is False

    started = client.post("/api/bot/start")
    assert started.status_code == 200
    assert started.json()["is_running"] is True
    assert client.get("/api/data").json()["system"]["services"][0]["running"] is True
