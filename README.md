# 🏔️ DRISHTI-NER — AI-Based Early Warning & Landslide Risk Monitoring System in NER

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-18%2B-61DAFB?style=for-the-badge&logo=react)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-38B2AC?style=for-the-badge&logo=tailwind-css)
![SIH](https://img.shields.io/badge/Smart_India_Hackathon-2024%2F2025-orange?style=for-the-badge)

An enterprise multi-hazard AI early warning and geospatial landslide risk intelligence platform engineered specifically for the steep, fragile terrain of the **North Eastern Region (NER) of India** (e.g., Imphal-Jiribam corridor, NH-37 / NH-2).

---

## 📌 Architecture & Modules
- **Dual-Engine Predictive Pipeline**:
  - **Spatial Baseline**: Terrain steepness, geotechnical lithology, historical landslide inventories, and fault proximity.
  - **Temporal Dynamic Engine**: High-cadence satellite precipitation (GPM/IMERG), SMAP soil moisture anomalies, and live IoT sensor arrays.
- **Corridor Safety Matrix**: Automated risk categorization of critical highway segments into Green (Safe), Yellow (Caution), and Red (High Probability) with automated evacuation buffer zones.
- **Emergency Dispatch & Citizen Broadcast**: Automated multi-lingual SMS alerts, emergency rescue dispatch dispatchers, and citizen crowdsourced hazard reporting.

---

## 📂 Project Structure
```text
AIML hackacthon SIH26 1/
├── backend/                   # FastAPI high-throughput geospatial inference API
│   ├── routers/               # Corridors, inference, sensors, and telemetry endpoints
│   ├── config.py              # Geospatial and API configurations
│   └── model_cache.py         # In-memory LRU model weight cache
├── data/                      # Historical inventories, geojson corridors, and delta steps
├── ml/                        # Training pipelines, spatial baseline, and temporal models
├── src/                       # React + TypeScript command center dashboard
├── DRISHTI_NER_Project_Proposal.docx # Full research & grant project proposal
└── README.md                  # System documentation
```

---

## 🚀 Running Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend Dashboard
```bash
npm install
npm run dev
```
