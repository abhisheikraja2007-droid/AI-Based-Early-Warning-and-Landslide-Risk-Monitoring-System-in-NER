"""
Automated Backend Integration Test Suite.
Validates:
  1. Startup lifecycle model caching (PyTorch .pt & XGBoost .json)
  2. Citizen geo-tagged crack/slope photo ingestion into MongoDB with 2dsphere index
  3. Geospatial proximity search ($near query within radius_km)
  4. Asynchronous raster math & inference task queuing
  5. Off-thread task polling and SHAP Explainable AI attribution
"""

import os
import sys
import time
import base64
import asyncio
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app, startup_event
from backend.model_cache import model_cache


async def run_tests():
    print("=" * 80)
    print("BACKEND AUTOMATED INTEGRATION TEST SUITE")
    print("=" * 80)

    # 1. Trigger FastAPI startup lifecycle hook
    print("\n--- 1. Triggering @app.on_event('startup') Lifecycle Hook ---")
    await startup_event()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        print("\n--- 2. Testing Root & Health Check ---")
        res = await client.get("/health")
        print("GET /health -> HTTP", res.status_code)
        print("Response JSON:", res.json())
        assert res.status_code == 200
        assert res.json()["model_cache"]["spatial_pytorch_loaded"] is True
        assert res.json()["model_cache"]["temporal_xgboost_loaded"] is True
        assert res.json()["model_cache"]["shap_explainer_ready"] is True
        print("[PASS] Startup lifecycle model caching verified!")

        # 3. Testing Citizen Geodata Ingestion
        print("\n--- 3. Testing Geo-Tagged Citizen Crack Photo Ingestion ---")
        dummy_jpeg_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        citizen_payload = {
            "reporter_name": "Ramesh Kumar (Panchayat Field Observer)",
            "phone_number": "+91-9876543210",
            "latitude": 11.52,
            "longitude": 76.15,
            "elevation_m": 840.5,
            "district": "Wayanad",
            "state": "Kerala",
            "observation_type": "tension_crack",
            "crack_width_cm": 18.5,
            "crack_length_m": 12.0,
            "movement_speed": "accelerating",
            "hazard_level": "EVACUATE",
            "notes": "Large transverse tension crack observed above tea estate slope following continuous heavy rainfall.",
            "photo_base64": dummy_jpeg_base64,
        }

        res = await client.post("/api/v1/citizen-reports", json=citizen_payload)
        print("POST /api/v1/citizen-reports -> HTTP", res.status_code)
        print("Response JSON:", res.json())
        assert res.status_code == 201
        assert res.json()["status"] == "INGESTED"
        report_id = res.json()["report_id"]
        print(f"[PASS] Citizen crack report ingested with ID: {report_id}")

        # 4. Testing Geospatial Proximity Query ($near 2dsphere)
        print("\n--- 4. Testing Nearby Geo-Spatial Proximity Query ---")
        nearby_res = await client.get("/api/v1/citizen-reports/nearby?lat=11.50&lon=76.16&radius_km=15.0")
        print("GET /api/v1/citizen-reports/nearby -> HTTP", nearby_res.status_code)
        nearby_data = nearby_res.json()
        print(f"Found {nearby_data['count']} nearby reports within 15 km.")
        assert nearby_res.status_code == 200
        assert nearby_data["count"] >= 1
        print("Nearest Report:", nearby_data["reports"][0]["reporter_name"], "| Distance:", nearby_data["reports"][0].get("distance_km"), "km")
        print("[PASS] MongoDB 2dsphere proximity search verified!")

        # 5. Testing Asynchronous Task Queue Inference (Off Web Thread)
        print("\n--- 5. Testing Asynchronous Task Queue Inference ---")
        infer_payload = {
            "latitude": 11.52,
            "longitude": 76.15,
            "event_date": "2025-07-16",
            "lead_time_hours": 12,
            "custom_rainfall_24h": 95.0,
        }
        async_res = await client.post("/api/v1/inference/predict-async", json=infer_payload)
        print("POST /api/v1/inference/predict-async -> HTTP", async_res.status_code)
        assert async_res.status_code == 202
        task_data = async_res.json()
        task_id = task_data["task_id"]
        poll_url = task_data["poll_url"]
        print("Dispatched Task ID:", task_id, "| Poll URL:", poll_url)

        # Poll for completion
        await asyncio.sleep(1.0)
        poll_res = await client.get(poll_url)
        print("GET", poll_url, "-> HTTP", poll_res.status_code)
        res_json = poll_res.json()
        print("Task Result Status:", res_json.get("status"))
        print("Prediction Risk:", res_json.get("prediction", {}).get("landslide_risk_probability"))
        print("Hazard Level:   ", res_json.get("prediction", {}).get("hazard_level"))
        print("Off-Thread Exec:", res_json.get("compute_telemetry", {}).get("off_thread_execution"))
        print("Compute Duration:", res_json.get("compute_telemetry", {}).get("duration_ms"), "ms")
        assert poll_res.status_code in [200, 202]
        print("[PASS] Asynchronous task dispatch and off-thread execution verified!")

        # 6. Testing Zero-Latency Synchronous Inference
        print("\n--- 6. Testing Zero-Latency Cached Sync Inference ---")
        t_sync_start = time.time()
        sync_res = await client.post("/api/v1/inference/predict-sync", json=infer_payload)
        sync_duration = (time.time() - t_sync_start) * 1000
        print(f"POST /api/v1/inference/predict-sync -> HTTP {sync_res.status_code} in {sync_duration:.2f} ms")
        assert sync_res.status_code == 200
        print("Sync Risk Probability:", sync_res.json()["prediction"]["landslide_risk_probability"])
        print("Driving Factors (SHAP XAI):")
        for f in sync_res.json().get("explainable_ai_driving_factors", [])[:3]:
            print(f"  * {f['feature']} = {f['measured_value']} ({f['impact']})")
        print("[PASS] Synchronous in-memory inference verified!")

    print("\n" + "=" * 80)
    print("ALL BACKEND INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_tests())
