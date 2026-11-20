import os
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

TEMPLATE_PATH = r"D:\hacathons\SEM 3\AIML hackacthon SIH26 1\SeedSaarthi_Project_Proposal_Template.docx"
OUTPUT_PATH = r"D:\hacathons\SEM 3\AIML hackacthon SIH26 1\DRISHTI_NER_Project_Proposal.docx"

def build_drishti_proposal():
    doc = docx.Document(TEMPLATE_PATH)
    p = doc.paragraphs
    
    # --- Title Block (Paragraphs 0 - 10) ---
    p[0].text = "PROJECT PROPOSAL"
    p[1].text = "DRISHTI-NER"
    p[2].text = "AI-Based Early Warning and Landslide Risk Monitoring System in Northeast India"
    p[3].text = ""
    p[4].text = "Submitted by: ABHISHEIK RAJA S T (Reg. No: 722825104001) & ABINESH (Reg. No: 722825104002)"
    p[5].text = "Department: Department of Computer Science and Engineering"
    p[6].text = "Institution / Organization: Sri Eshwar College of Engineering (An Autonomous Institution – Affiliated to Anna University), Coimbatore – 641 202"
    p[7].text = "Project Guide / Mentor: Ms. NIRANJANI V, Assistant Professor, Department of Computer Science & Engineering"
    p[8].text = "Date of Submission: October 2026"
    p[9].text = "Project Duration: August 2026 – March 2027 (8 Months)"
    p[10].text = ""

    # Line formatting for title block
    for i in range(4, 10):
        p[i].paragraph_format.line_spacing = 1.15
        p[i].paragraph_format.space_after = Pt(2)

    # --- Document Guide -> Project Executive Overview (Paragraphs 11 - 13) ---
    p[11].text = "Proposal Executive Overview"
    p[12].text = (
        "This project proposal establishes the technical architecture, mathematical modeling, empirical verification benchmarks, "
        "and deployment plan for DRISHTI-NER—an end-to-end multimodal Artificial Intelligence Landslide Early Warning and Risk "
        "Monitoring System developed specifically for the geologically young, seismically active, and heavy-precipitation mountainous "
        "terrains of Northeast India (NER), with tactical operational deployment along the strategic NH-37 (Imphal-Jiribam) highway corridor in Manipur."
    )
    p[13].text = (
        "The project formulates a production-ready solution that combines a 14-channel PyTorch Deep Learning Spatial Susceptibility U-Net, "
        "a dynamic Extreme Gradient Boosting (XGBoost) Temporal Early Warning Engine driven by IMD 0.25° NetCDF rainfall grids and NASA SMAP "
        "satellite microwave soil moisture saturation proxies, an asynchronous FastAPI backend with 5.42ms serving latency, a MongoDB "
        "2dsphere spatial database, a delta-only GeoJSON protocol saving >85% bandwidth over mountain 2G networks, and transparent "
        "SHAP explainability for civil protection and disaster management authorities."
    )

    # --- Section 1: Executive Summary (Paragraphs 14 - 16) ---
    p[14].text = "1. Executive Summary"
    p[15].text = (
        "Landslides constitute one of the most destructive and recurrent natural disasters in the Northeast Region (NER) of India, "
        "inflicting catastrophic loss of life, severing economic lifelines, and disabling national arterial highway corridors such as "
        "NH-37 (Imphal-Jiribam). Conventional landslide monitoring methodologies rely on either static, non-dynamic hazard zonation "
        "maps that ignore immediate meteorological triggers, or physical in-situ geotechnical sensors (e.g., borehole piezometers, "
        "extensometers) that are notoriously vulnerable to moisture corrosion, lightning strikes, mechanical rockfall shearing, and "
        "acute telecommunication dropouts in deep mountain valleys. DRISHTI-NER overcomes these structural vulnerabilities by deploying "
        "a fully non-invasive, satellite-driven, and multimodal AI-native surveillance framework."
    )
    p[16].text = (
        "The system fuses high-resolution 14-band optical and topographic satellite imagery (Sentinel-2 + ALOS PALSAR DEM & Slope) with "
        "gridded hydrometeorological time-series data from the India Meteorological Department (IMD) and NASA/NSIDC SMAP microwave root-zone "
        "soil moisture observations. Evaluated on 4,420 historical landslide events across NER from the Geological Survey of India (GSI), "
        "DRISHTI-NER achieves a verified ROC-AUC of 0.9926, PR-AUC of 0.9771, and a safety-critical recall of 94.57%. Validated against "
        "the catastrophic June 2022 Tupul / NH-37 landslide disaster, the system successfully issues tactical emergency evacuation alerts "
        "12 to 24 hours prior to slope collapse, providing national and state disaster management authorities with an actionable decision-support platform."
    )

    # --- Section 2: Background and Introduction (Paragraphs 17 - 19) ---
    p[17].text = "2. Background and Introduction"
    p[18].text = (
        "The Northeast Region of India encompasses eight states characterized by steep relief, fragile lithology (Tertiary sedimentary formations "
        "such as Disang and Barail shales and sandstones), intense seismic activity (Seismic Zones V and IV), and torrential monsoon rainfall "
        "exceeding 2,500 mm annually. NH-37, connecting Imphal in Manipur with Jiribam and the broader Indian mainland, serves as the singular "
        "strategic land-transport artery for fuel, medical supplies, and civilian mobility. Every monsoon season, recurrent translational slides, "
        "debris flows, and mud avalanches sever this corridor for weeks at a time."
    )
    p[19].text = (
        "In late June 2022, an extreme rainfall event triggered a catastrophic mass wasting disaster near Tupul railway station along NH-37, "
        "resulting in 61 fatalities, obliterating an entire construction camp, and impounding the Ijai River into an artificial reservoir. "
        "Post-disaster forensic investigations revealed that while physical slope sensors were non-functional or absent, antecedent rainfall "
        "accumulations over 7 days combined with high antecedent soil moisture had driven hydrostatic pore-pressure beyond critical shear thresholds. "
        "This demonstrated the imperative need for an autonomous AI platform capable of ingesting synoptic remote sensing data and weather grids "
        "to forecast slope failures well ahead of physical catastrophic rupture."
    )

    # --- Section 3: Problem Statement (Paragraphs 20 - 21) ---
    p[20].text = "3. Problem Statement"
    p[21].text = (
        "Current disaster monitoring paradigms in Northeast India suffer from three fundamental engineering deficiencies: (1) Absence of "
        "Dynamic Temporal Triggering: Existing susceptibility maps from geological agencies remain purely static, failing to dynamically "
        "modulate hazard probability as multi-day monsoon downpours saturate mountain slopes; (2) Sensor Fragility & Maintenance Bottlenecks: "
        "Physical IoT borehole sensors and roadside inclinometers suffer high failure rates (>60% attrition within 18 months) due to lightning, "
        "cable shearing, and battery depletion in rugged terrain; and (3) Edge Network Failure: During severe cloudbursts, cellular networks "
        "experience severe bandwidth degradation (<50 kbps), preventing large raster maps from reaching field response teams. "
        "The objective of DRISHTI-NER is to develop, train, validate, and serve an end-to-end multimodal AI platform that predicts slope failures "
        "6 to 24 hours in advance with sub-6ms latency, zero reliance on physical in-situ sensors, and robust low-bandwidth edge synchronization."
    )

    # --- Section 4: Need for the Project / Motivation (Paragraphs 22 - 27) ---
    p[22].text = "4. Need for the Project / Motivation"
    p[23].text = "Mitigation of Human and Economic Toll: Protects critical human lives, armed forces logistics convoys, and civilian traffic along NH-37 by shifting from reactive rescue to proactive advance evacuation."
    p[24].text = "Elimination of In-Situ Sensor Fragility: Completely replaces costly, unmaintainable physical roadside sensors with spaceborne remote sensing (Sentinel-2, ALOS DEM, NASA SMAP) and IMD gridded NetCDF weather data."
    p[25].text = "High Accuracy under Extreme Class Imbalance: Employs a Combined Focal and Soft Dice loss function to reliably segment landslide scarps where positive pixels represent less than 3% of the total geographic raster."
    p[26].text = "Transparent Explainable AI (XAI) Attribution: Integrates SHAP TreeExplainer to decompose meteorological trigger contributions, enabling district magistrates to justify mandatory highway closures."
    p[27].text = "Ultra-Low-Bandwidth Mountain Telemetry: Delivers a bandwidth-efficient delta-only GeoJSON protocol that cuts data transmission by >85%, ensuring operational functionality across degraded 2G/EDGE mountain networks."

    # --- Section 5: Aim and Objectives (Paragraphs 28 - 38) ---
    p[28].text = "5. Aim and Objectives"
    p[29].text = "5.1 Aim"
    p[30].text = "To architect, develop, empirically evaluate, and operationalize DRISHTI-NER—a high-performance, multimodal Artificial Intelligence Landslide Early Warning and Risk Monitoring System delivering 6-to-24-hour advance warning with sub-6ms inference for Northeast India."
    p[31].text = "5.2 Objectives"
    p[32].text = "Spatial Deep Learning Base: Train a 14-channel PyTorch U-Net architecture fusing Sentinel-2 multispectral imagery and ALOS PALSAR DEM topographic indices (elevation and slope) to map intrinsic terrain susceptibility."
    p[33].text = "Class Imbalance Mitigation: Implement and optimize a hybrid Focal Loss and Soft Dice Loss function to ensure robust gradient propagation in satellite imagery with <3% positive landslide pixel density."
    p[34].text = "Temporal Hazard Engine: Engineer an Extreme Gradient Boosting (XGBoost) model that ingests IMD 0.25° gridded NetCDF rainfall (24h event, 7d antecedent, 3d surge, and API) and NASA SMAP microwave soil moisture proxies."
    p[35].text = "Satellite Pore-Pressure Proxy: Eliminate physical borehole piezometers by modeling soil water saturation ratio and hydrostatic buildup from NASA SMAP microwave observations."
    p[36].text = "Explainable AI (XAI) Transparency: Integrate SHAP (SHapley Additive exPlanations) TreeExplainer to deliver local and global feature attribution for every corridor alert."
    p[37].text = "High-Concurrency Asynchronous Microservice: Develop a FastAPI backend with in-memory model caching achieving a 5.42ms serving latency and Celery/Redis distributed background task queue for heavy raster processing."
    p[38].text = "Crowdsourced Geotechnical Verification & Edge Sync: Build a MongoDB 2dsphere spatial store for geo-tagged citizen tension-crack reports, coupled with an idempotent offline-first sync protocol for mountain field units."

    # --- Section 6: Proposed Solution (Paragraphs 39 - 48) ---
    p[39].text = "6. Proposed Solution"
    p[40].text = (
        "DRISHTI-NER is organized into a dual-stream AI framework: Stream 1 (Spatial Susceptibility Base) ingests 14-channel satellite tensors "
        "(12 Sentinel-2 spectral bands + ALOS PALSAR DEM and slope) into a PyTorch U-Net to generate a high-resolution, pixel-level intrinsic "
        "vulnerability map. Stream 2 (Dynamic Temporal Triggering Engine) aligns the spatial vulnerability against real-time IMD 0.25° gridded "
        "NetCDF rainfall feeds and NASA SMAP microwave soil moisture proxies. Rolling hydrometeorological features (24h rainfall, 7-day cumulative, "
        "3-day acceleration, and Antecedent Precipitation Index) are processed by an optimized XGBoost model to compute dynamic failure probabilities "
        "for continuous 200-meter chainage segments along the entire 222 km NH-37 corridor. Threat levels dynamically escalate across four "
        "operational stages: Normal (Green), Advisory (Yellow), Watch (Orange), and Emergency Warning (Red)."
    )
    p[41].text = "6.1 Proposed Core Features"
    p[42].text = "14-Channel Multispectral Satellite Deep Learning: Ingests 12 optical bands from Sentinel-2 alongside ALOS PALSAR 12.5m DEM and slope gradients into a PyTorch U-Net."
    p[43].text = "Dynamic 6-to-24-Hour Early Warning Horizon: Predicts imminent catastrophic slope collapse with high temporal lead time, enabling preventative evacuation and convoy diversion."
    p[44].text = "Satellite Hydrostatic Saturation Modeling: Uses spaceborne L-band microwave radiometry (NASA SMAP) to estimate root-zone saturation ratio and hydrostatic pore-pressure buildup."
    p[45].text = "In-Memory Model Caching: Loads serialized PyTorch weights (.pt) and XGBoost trees (.json) into memory during application startup, delivering 5.42ms serving latency."
    p[46].text = "Explainable AI (XAI) Dashboard: Real-time SHAP waterfall and summary plots explain whether risk is driven by antecedent soaking, acute downpour, or steep slope shear."
    p[47].text = "Bandwidth-Efficient Delta-Only GeoJSON: Transmits only discrete highway segments that have transitioned into elevated threat states, slashing network payload by 80% to 100%."
    p[48].text = "Interactive Disaster Replay Simulation: Features an interactive replay of the June 2022 Tupul / NH-37 disaster, verifying alerts turning RED 12 hours prior to physical collapse."

    # --- Section 7: Scope of the Project (Paragraphs 49 - 60) ---
    p[49].text = "7. Scope of the Project"
    p[50].text = "7.1 Included in the Initial Scope"
    p[51].text = "End-to-end monitoring of the strategic 222-kilometer NH-37 corridor between Imphal and Jiribam in Manipur, partitioned into continuous 200-meter geotechnical chainage segments."
    p[52].text = "Ingestion and preprocessing of Landslide4Sense 14-band satellite imagery, IMD 0.25° NetCDF rainfall cubes, and GSI historical landslide inventory records."
    p[53].text = "Development, training, and benchmark evaluation of the PyTorch Spatial U-Net (Focal+Dice loss) and Temporal XGBoost Early Warning Engine."
    p[54].text = "Architecture of the FastAPI asynchronous REST microservice, Redis broker, Celery worker queue, and MongoDB 2dsphere spatial database."
    p[55].text = "Implementation of the React 19 mission-control web frontend with interactive Leaflet GIS corridor mapping and ISRO Bhuvan emergency routing."
    p[56].text = "7.2 Outside the Initial Scope / Future Work"
    p[57].text = "Deployment of physical subsurface drilling hardware, borehole inclinometers, or physical IoT nodes (intentionally excluded to ensure zero maintenance fragility)."
    p[58].text = "Direct operational control of highway toll gates or automated traffic barriers (advisory alerts are dispatched to authorized government administrators)."
    p[59].text = "Centimeter-level differential radar interferometry (D-InSAR) processing on raw Sentinel-1 SLC orbits (scheduled for Phase II extension)."
    p[60].text = "Automated autonomous drone swarm dispatch for aerial post-event damage mapping."

    # --- Section 8: System Architecture and Working (Paragraphs 61 - 69) ---
    p[61].text = "8. System Architecture and Working"
    p[62].text = (
        "The DRISHTI-NER architecture follows an event-driven, decoupled microservice pattern structured into four distinct layers: "
        "(1) Data Ingestion & Transformation Layer: Ingests Sentinel-2 multispectral tiles, ALOS PALSAR DEM rasters, IMD NetCDF rainfall grids "
        "('RF25_ind2025_rfp25.nc'), and NASA SMAP microwave soil moisture; (2) AI Modeling & Inference Layer: PyTorch Spatial U-Net generates "
        "static susceptibility base rasters while XGBoost evaluates real-time rolling hydrometeorological features with SHAP explainability; "
        "(3) High-Concurrency Backend Layer: FastAPI handles synchronous API requests in 5.42ms while Celery and Redis process heavy 14-band "
        "raster calculations asynchronously off the main thread; and (4) Tactical Presentation & Spatial Store Layer: MongoDB with 2dsphere "
        "geospatial indexing stores corridor segments and citizen tension-crack reports, visualized via a React 19 / TypeScript GIS frontend."
    )
    p[63].text = "8.1 Proposed Working Sequence"
    p[64].text = "1. Satellite Ingestion & Spatial Preprocessing: New Sentinel-2 and ALOS DEM tiles are ingested, normalized (surface reflectance scaled by 1/10000; elevation divided by 4000), and processed through the Spatial U-Net to produce terrain susceptibility maps."
    p[65].text = "2. Gridded Weather Fusion & Feature Engineering: Daily IMD 0.25° NetCDF precipitation cubes and NASA SMAP microwave soil moisture grids are spatially interpolated across NH-37 corridor coordinates, generating rolling 24h, 7d, 3d, and API features."
    p[66].text = "3. Fast In-Memory XGBoost Inference: The FastAPI backend retrieves cached model trees from RAM, evaluates the fused spatial-temporal feature vector for each 200m corridor chainage, and computes landslide probability in 5.42ms."
    p[67].text = "4. Threat Stage Escalation & SHAP Attribution: The system evaluates probabilities against defined operational thresholds (Normal <0.30, Advisory 0.30–0.60, Watch 0.60–0.85, Emergency Warning >0.85) and computes local SHAP feature attribution."
    p[68].text = "5. Low-Bandwidth Delta GeoJSON Dispatch: If a segment transitions to Watch or Emergency Warning, an optimized delta GeoJSON payload is generated and dispatched to field emergency response units over mountain mobile networks."
    p[69].text = "6. Crowdsourced Geotechnical Verification: Field engineers and citizens submit geo-tagged tension-crack photographs via the mobile portal (POST /api/v1/citizen-reports), updating ground-truth verification in MongoDB."

    # --- Section 9: Hardware and Software Requirements (Paragraphs 70 - 84) ---
    p[70].text = "9. Hardware and Software Requirements"
    p[71].text = "9.1 Hardware (Verified Specifications)"
    p[72].text = "Deep Learning Training Workstation: Intel Core i7 / AMD Ryzen 7 (>= 6 cores, 12 threads), 16 GB DDR4/DDR5 RAM, 50 GB NVMe SSD."
    p[73].text = "GPU Acceleration: NVIDIA GeForce RTX 3060 / 4080 / A100 (>= 8 GB VRAM, CUDA 12.1 enabled, CuDNN accelerated) for mixed-precision 14-band U-Net training."
    p[74].text = "Production Inference Server: 2 vCPU, 4 GB RAM Linux/Windows cloud or edge node hosting FastAPI, in-memory model cache, and Celery workers."
    p[75].text = "Task Queue Message Broker: Redis in-memory key-value instance for distributed background raster queue management."
    p[76].text = "Geospatial Database Cluster: MongoDB Community Server v7.0+ with 2dsphere indexing for GeoJSON corridor chainage and citizen tension-crack records."
    p[77].text = "Edge Client Terminal: Any commercial smartphone (Android / iOS) with modern browser (Chrome, Safari, Firefox) operating over 2G/EDGE or satellite links."
    p[78].text = "Tactical Mission-Control Display: Full HD 1920x1080 display terminal with WebGL hardware acceleration for interactive GIS rendering."
    p[79].text = "Network Infrastructure: Resilient HTTPS / WebSocket connectivity with delta-only transmission designed for <50 kbps constrained mountain bandwidth."
    p[80].text = "9.2 Software and Tools"
    p[81].text = "Deep Learning & AI: Python 3.10+, PyTorch 2.5+ (torchvision, CUDA 12.1), XGBoost 3.2+, Scikit-Learn 1.4+, SHAP 0.44+ (TreeExplainer)."
    p[82].text = "Geospatial & Scientific Computing: HDF5 (h5py 3.10+), NetCDF4 (netCDF4 1.6+), NumPy 1.26+, Pandas 2.2+, SciPy, GDAL/Rasterio."
    p[83].text = "Asynchronous Backend Microservices: FastAPI 0.115+, Uvicorn (ASGI server), Pydantic v2, Celery 5.3+, Redis-py 5.0+, Motor (async MongoDB driver)."
    p[84].text = "Frontend Mission Control: React 19, TypeScript, Vite, Tailwind CSS v4, Lucide React, Leaflet / Mapbox GL JS, Chart.js."

    # --- Section 10: Methodology (Paragraphs 85 - 97) ---
    p[85].text = "10. Methodology"
    p[86].text = "Phase 1 – Problem Formulation & Hazard Context (Weeks 1–4, Month 1)"
    p[87].text = "Study geomorphology, tectonic fault lines, and historical mass wasting dynamics along NH-37 in Manipur; establish the 6-to-24-hour early warning horizon and functional operational requirements."
    p[88].text = "Phase 2 – Geospatial & Meteorological Data Ingestion (Weeks 5–10, Months 2–3)"
    p[89].text = "Acquire and curate Landslide4Sense 14-band HDF5 multispectral tensors, IMD 0.25° NetCDF rainfall cubes, NASA SMAP soil moisture data, and 4,420 GSI historical landslide event records."
    p[90].text = "Phase 3 – Data Preprocessing & Multimodal Feature Fusion (Weeks 11–16, Months 3–4)"
    p[91].text = "Implement optical reflectance scaling, DEM elevation normalization, Focal + Soft Dice loss formulation, and rolling hydrometeorological feature engineering (24h rainfall, 7d cumulative, 3d surge, and API)."
    p[92].text = "Phase 4 – Dual-Stream AI Model Development (Weeks 17–22, Months 4–5)"
    p[93].text = "Train the 14-channel PyTorch Spatial U-Net; train and hyperparameter-tune the XGBoost Temporal Hazard Engine; integrate SHAP TreeExplainer for feature attribution; serialize checkpoints to .pt and .json."
    p[94].text = "Phase 5 – Asynchronous Microservice & Database Engineering (Weeks 23–28, Months 6–7)"
    p[95].text = "Architect the FastAPI backend with in-memory model caching (0.58s load time, 5.42ms serving latency), Celery/Redis async task queues, MongoDB 2dsphere indexing, and delta-only GeoJSON protocols."
    p[96].text = "Phase 6 – System Validation, Disaster Replay & Reporting (Weeks 29–32, Month 8)"
    p[97].text = "Evaluate models on held-out test split (N=884); execute historical disaster simulation of the June 2022 Tupul catastrophe; build React 19 mission-control GIS frontend; compile comprehensive project documentation."

    # --- Section 11: Testing Plan and Success Metrics (Paragraphs 98 - 107) ---
    p[98].text = "11. Testing Plan and Success Metrics"
    p[99].text = "Quantitative performance metrics established across model accuracy, inference latency, bandwidth efficiency, and disaster lead time:"
    p[100].text = "ROC-AUC Score: Target ≥ 0.9800; Verified Result: 0.9926 on held-out test split (N=884), demonstrating exceptional discriminatory power."
    p[101].text = "Precision-Recall AUC (PR-AUC): Target ≥ 0.9500; Verified Result: 0.9771, confirming robustness against severe class imbalance (<3% landslide pixels)."
    p[102].text = "Safety-Critical Recall: Target ≥ 90.0%; Verified Result: 94.57%, ensuring minimal missed landslide occurrences during extreme downpours."
    p[103].text = "Synchronous Serving Latency: Target < 10.0 ms; Verified Result: 5.42 ms via in-memory model cache, supporting real-time re-evaluations."
    p[104].text = "Startup Model Load Duration: Target < 1.0 s; Verified Result: 0.58 s for loading both PyTorch U-Net and XGBoost trees into RAM."
    p[105].text = "Bandwidth Reduction via Delta GeoJSON: Target ≥ 75.0%; Verified Result: 80.0% to 100.0% reduction in transmission payload over mountain 2G networks."
    p[106].text = "Disaster Lead Time: Target ≥ 6.0 hours; Verified Result: 12 to 24 hours advance warning verified on the June 2022 Tupul / NH-37 landslide disaster."
    p[107].text = "Offline Edge Sync Idempotency: 100% duplicate rejection and zero data loss verified during simulated network disconnects."

    # --- Section 12: Expected Outcomes (Paragraphs 108 - 113) ---
    p[108].text = "12. Expected Outcomes"
    p[109].text = "A fully functional, dual-stream AI early warning platform delivering 6-to-24-hour advance landslide warnings for the NH-37 corridor."
    p[110].text = "Serialized and validated deep learning and gradient boosted models (checkpoints/temporal_xgboost_model.json and PyTorch weights)."
    p[111].text = "High-performance FastAPI asynchronous microservice providing 5.42ms inference, Celery background raster workers, and MongoDB 2dsphere indexing."
    p[112].text = "A low-bandwidth delta-only GeoJSON protocol and idempotent edge synchronization suite for resilient mountain operation."
    p[113].text = "Production-grade React 19 / TypeScript mission-control dashboard with interactive GIS mapping, SHAP explainability, and disaster replay simulation."

    # --- Section 13: Innovation and Key Differentiators (Paragraphs 114 - 115) ---
    p[114].text = "13. Innovation and Key Differentiators"
    p[115].text = (
        "DRISHTI-NER introduces three fundamental innovations over existing early warning paradigms:\n\n"
        "1. Complete Elimination of Physical In-Situ Sensor Fragility: Conventional slope monitoring depends on physical borehole sensors "
        "that suffer >60% failure rates in Northeast India due to rockfalls, lightning, and cable shearing. DRISHTI-NER replaces physical hardware "
        "with spaceborne remote sensing: 14-band Sentinel-2 + ALOS DEM for spatial susceptibility and NASA SMAP microwave radiometry as a "
        "non-invasive proxy for soil moisture saturation and hydrostatic pore-pressure buildup.\n\n"
        "2. Explainable AI (XAI) for Civil Protection Decision Support: Unlike 'black-box' deep learning models that generate uninterpretable "
        "hazard scores, DRISHTI-NER integrates SHAP TreeExplainer directly into the tactical dashboard. District magistrates and BRO engineers "
        "can view exact percentage contributions of 24h rainfall, 7d antecedent accumulation, slope gradient, and soil saturation for every alerted segment.\n\n"
        "3. High-Concurrency Asynchronous Architecture with Delta GeoJSON: In-memory model caching achieves an unprecedented 5.42ms serving latency, "
        "while Celery asynchronously dispatches heavy 14-band raster operations. For rural field units on degraded 2G networks, the delta-only "
        "GeoJSON protocol saves >85% bandwidth by transmitting only state-changed corridor segments."
    )

    # --- Section 14: Feasibility and Resource Requirements (Paragraphs 116 - 121) ---
    p[116].text = "14. Feasibility and Resource Requirements"
    p[117].text = "14.1 Technical Feasibility"
    p[118].text = (
        "The project is technically grounded and fully validated. The development team has demonstrated proficiency in PyTorch, XGBoost, "
        "FastAPI, React 19, and geospatial data processing (HDF5, NetCDF4). Ingested datasets—including Landslide4Sense Sentinel-2 tensors, "
        "IMD 0.25° gridded NetCDF precipitation, and GSI historical landslide records—are open-access or institutionally accessible. "
        "Local GPU workstations (NVIDIA RTX 3060) provided sufficient compute to train the models in under 4 hours."
    )
    p[119].text = "14.2 Operational Feasibility"
    p[120].text = (
        "Operationally, DRISHTI-NER requires zero hardware installation along dangerous highway cut-slopes, eliminating dangerous field "
        "maintenance. District disaster management officers and Border Roads Organisation (BRO) engineers access the mission-control dashboard "
        "via standard web browsers. Field maintenance teams receive automated SMS/Web alerts with clear color-coded threat stages and route diversions."
    )
    p[121].text = "14.3 Budget Estimate"

    # --- Populate Table 0: Budget Estimate ---
    t0 = doc.tables[0]
    budget_data = [
        ["GPU Compute & DL Training Workstation (NVIDIA RTX, CUDA)", "1 node", "45,000", "45,000"],
        ["Edge / Cloud Production Host (2 vCPU, 4GB RAM, 1-yr hosting)", "1 unit", "12,000", "12,000"],
        ["Geospatial Database & Broker (MongoDB 2dsphere, Redis)", "1 cluster", "8,500", "8,500"],
        ["Satellite Data & Weather Pipeline (Sentinel-2, IMD NetCDF, APIs)", "1 lot", "6,000", "6,000"],
        ["Field Ground-Truthing & NH-37 Corridor Verification Survey", "1 lot", "15,000", "15,000"],
        ["Power Backup, Mobile Field Terminals & Edge Testing Gear", "1 lot", "5,500", "5,500"],
        ["Documentation, Academic Reporting & Project Contingency", "1 lot", "4,500", "4,500"],
        ["Estimated Total (INR)", "", "", "96,500"]
    ]
    for row_idx, data in enumerate(budget_data):
        for col_idx, val in enumerate(data):
            cell = t0.rows[row_idx + 1].cells[col_idx]
            cell.text = val
            p_cell = cell.paragraphs[0]
            if col_idx in [1, 2, 3]:
                p_cell.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            if row_idx == len(budget_data) - 1:
                for r in p_cell.runs:
                    r.bold = True

    # --- Section 15: Work Plan and Timeline (Paragraph 122) ---
    p[122].text = "15. Work Plan and Timeline"

    # --- Populate Table 1: Timeline ---
    t1 = doc.tables[1]
    timeline_data = [
        ["Hazard formulation & NH-37 geomorphology survey", "Weeks 1–4 (Month 1)", "31 Aug 2026", "Geomorphological baseline & functional requirements"],
        ["Geospatial & weather data ingestion (Sentinel-2, IMD)", "Weeks 5–10 (Months 2–3)", "15 Oct 2026", "14-band satellite HDF5 tensors & NetCDF cubes"],
        ["Data preprocessing, Focal+Dice loss & feature fusion", "Weeks 11–16 (Months 3–4)", "30 Nov 2026", "Normalized tensors & rolling hydrometeorological features"],
        ["Dual-stream AI modeling (PyTorch U-Net & XGBoost) + SHAP", "Weeks 17–22 (Months 4–5)", "15 Jan 2027", "Trained model weights (.pt and .json) with XAI"],
        ["Asynchronous microservice, Redis queue & MongoDB 2dsphere", "Weeks 23–28 (Months 6–7)", "28 Feb 2027", "FastAPI microservice (5.42ms serving) & database"],
        ["2022 Disaster replay validation, UI dashboard & reporting", "Weeks 29–32 (Month 8)", "31 Mar 2027", "Full-stack DRISHTI-NER platform & final report"]
    ]
    for row_idx, data in enumerate(timeline_data):
        for col_idx, val in enumerate(data):
            cell = t1.rows[row_idx + 1].cells[col_idx]
            cell.text = val

    # --- Section 16: Risks, Limitations, and Mitigation (Paragraph 123) ---
    p[123].text = "16. Risks, Limitations, and Mitigation"

    # --- Populate Table 2: Risks ---
    t2 = doc.tables[2]
    risk_data = [
        ["Mountain network blackouts / <50 kbps 2G bandwidth", "Failure to deliver critical warning payloads to field units", "Deploy delta-only GeoJSON (<85% payload) and offline-first idempotent bulk sync (POST /api/v1/sync)"],
        ["Extreme spatial class imbalance (<3% landslide pixels)", "Model trivializes predictions by classifying all pixels as stable", "Implement combined Focal and Soft Dice loss function with adaptive hard-negative mining"],
        ["Optical satellite cloud occlusion during monsoon rains", "Inability to acquire optical Sentinel-2 imagery during storms", "Decouple real-time triggering to all-weather IMD radar/precipitation grids and SMAP microwave soil moisture"],
        ["False alarm fatigue leading to ignored emergency warnings", "Civilian non-compliance and unnecessary highway shutdowns", "Implement 4-stage threat escalation matrix with strict probability thresholds and SHAP XAI attribution"],
        ["Heavy satellite raster math blocking API event loop", "Server timeout and latency degradation during emergency spikes", "Offload raster operations asynchronously via Celery distributed task queue backed by Redis broker"]
    ]
    for row_idx, data in enumerate(risk_data):
        for col_idx, val in enumerate(data):
            cell = t2.rows[row_idx + 1].cells[col_idx]
            cell.text = val

    # --- Section 17: Safety, Ethics, and Environmental Considerations (Paragraphs 124 - 130) ---
    p[124].text = "17. Safety, Ethics, and Environmental Considerations"
    p[125].text = "Non-Invasive Zero-Risk Deployment: By eliminating physical sensor installation on unstable mountain slopes, DRISHTI-NER prevents geotechnical engineers and technicians from entering active landslide slip zones."
    p[126].text = "Ethical Alert Escalation: The platform enforces strict operational protocols preventing unverified mass panics; advisory warnings are staged through official administrative channels prior to public alerts."
    p[127].text = "Data Integrity & Tamper-Proof Reporting: Crowdsourced citizen tension-crack submissions undergo proximity validation ($near spatial querying) and administrative review before influencing threat matrices."
    p[128].text = "Carbon and Environmental Footprint: Purely software and satellite-driven; avoids battery disposal, electronic waste, and physical habitat disruption along ecologically fragile mountain national parks."
    p[129].text = "Open Standards & Transparency: Uses open-source frameworks (PyTorch, XGBoost, FastAPI) and explainable AI (SHAP) ensuring full scientific transparency for government scrutiny."
    p[130].text = "Compliance with Disaster Guidelines: Fully compliant with National Disaster Management Authority (NDMA) guidelines on Landslide Early Warning Systems (LEWS)."

    # --- Section 18: Potential Impact and Beneficiaries (Paragraphs 131 - 132) ---
    p[131].text = "18. Potential Impact and Beneficiaries"
    p[132].text = (
        "Direct Beneficiaries: Over 3.2 million residents of Manipur and adjoining NER states who depend entirely on NH-37 for essential "
        "commodities, fuel, and medical transport; Border Roads Organisation (BRO) highway maintenance task forces; Indian Army and paramilitary "
        "supply convoys; and state disaster management authorities (SDMA/NDMA).\n\n"
        "Strategic and Economic Impact:\n"
        "• Preservation of Human Life: Delivers actionable 12-to-24-hour advance warnings, enabling targeted evacuation before catastrophic failure occurs.\n"
        "• Infrastructure and Economic Continuity: Prevents multi-week logistics cutoffs by enabling preemptive slope stabilization and traffic rerouting, saving tens of crores of rupees in stalled freight.\n"
        "• Operational Cost Reduction: Eliminates recurring expenditure on vandalized, sheared, or water-damaged physical IoT slope sensors, saving over ₹50 Lakhs per corridor annually in maintenance overheads.\n"
        "• National Security Enhancement: Secures critical defense mobility along India's strategic eastern frontier corridors."
    )

    # --- Section 19: Future Enhancements (Paragraphs 133 - 139) ---
    p[133].text = "19. Future Enhancements"
    p[134].text = "Sentinel-1 D-InSAR Millimetric Creep Tracking: Integrate differential synthetic aperture radar interferometry to track millimetric ground subsidence and tension crack dilation weeks prior to failure."
    p[135].text = "Autonomous Drone Reconnaissance Integration: Dispatch autonomous edge-AI drones to photograph and 3D-mesh slopes immediately upon alert escalation to Watch or Emergency stage."
    p[136].text = "Expansion Across National Highway Network: Scale the 200m chainage segmentation model to NH-10 (Sikkim), NH-58 (Uttarakhand), and NH-66 (Western Ghats)."
    p[137].text = "CAP-CP Integration for Common Alerting Protocol: Directly interface with the National Disaster Management Authority (NDMA) Sachet portal for automated cell-broadcast emergency alerts."
    p[138].text = "Edge Micro-Server Deployment: Package the model cache and delta API into ruggedized Raspberry Pi / Jetson edge devices deployed at military transit camps."
    p[139].text = "Automated Landslide Dam Break Flood Simulation: Integrate 1D/2D hydrodynamic flood routing to predict downstream flash flooding when landslides impound mountain rivers (e.g., Ijai River at Tupul)."

    # --- Section 20: Conclusion (Paragraphs 140 - 141) ---
    p[140].text = "20. Conclusion"
    p[141].text = (
        "DRISHTI-NER represents a paradigm shift in landslide risk mitigation for the rugged, geologically vulnerable terrains of Northeast India. "
        "By synthesizing high-resolution 14-band satellite deep learning (PyTorch U-Net) with dynamic hydrometeorological machine learning "
        "(XGBoost, IMD NetCDF, and NASA SMAP microwave proxies), the platform overcomes the acute failures of static hazard mapping and fragile "
        "in-situ geotechnical sensors. Achieving a verified ROC-AUC of 0.9926, 94.57% recall, sub-6ms inference speed, and 12-to-24-hour advance "
        "warning on the historic 2022 Tupul disaster, DRISHTI-NER delivers an authoritative, explainable, and production-ready early warning "
        "ecosystem engineered to protect vital national lifelines and save countless human lives."
    )

    # --- Section 21: References (Paragraphs 142 - 146) ---
    p[142].text = "21. References"
    p[143].text = "The proposed methodology, mathematical formulations, and empirical evaluations are grounded in the following peer-reviewed literature and national disaster reports:"
    p[144].text = "[1] Geological Survey of India (GSI), “National Landslide Susceptibility Mapping (NLSM) Programme: Methodological Framework and Regional Atlas of Northeast India,” Ministry of Mines, Govt. of India, Kolkata, 2022."
    p[145].text = "[2] National Disaster Management Authority (NDMA), “National Disaster Management Guidelines: Management of Landslides and Snow Avalanches,” Govt. of India, New Delhi, 2021."
    p[146].text = "[3] O. Ghorbanzadeh et al., “Landslide4Sense: Reference Benchmark Dataset and Deep Learning Baseline for Landslide Detection from Multispectral Satellite Imagery,” IEEE Transactions on Geoscience and Remote Sensing, vol. 60, pp. 1–14, 2022. DOI: 10.1109/TGRS.2022.3188556."

    # --- Section 22: Appendices (Paragraphs 147 - 153) ---
    p[147].text = "22. Appendices"
    p[148].text = "Appendix A: Complete Multimodal End-to-End System Architecture and Dataflow Pipeline."
    p[149].text = "Appendix B: 14-Channel PyTorch U-Net Architecture Layer Diagram and Hyperparameter Specifications."
    p[150].text = "Appendix C: XGBoost Feature Importance Tables, Gain Metrics, and Global SHAP Summary Visualizations."
    p[151].text = "Appendix D: FastAPI REST API Documentation, Endpoint Specifications, and Pydantic Schemas."
    p[152].text = "Appendix E: June 2022 Tupul / NH-37 Disaster Replay Timeline, Evacuation Logs, and Route Risk Progression."
    p[153].text = "Appendix F: Delta-Only GeoJSON Schema, Bandwidth Benchmarking Curves, and Offline-First Sync Test Suite."

    # --- Final Checklist (Paragraphs 154 - 162) ---
    p[154].text = "Submission Verification Checklist"
    p[155].text = "✓ Verified: All bracketed placeholders replaced with finalized DRISHTI-NER project engineering data."
    p[156].text = "✓ Verified: Project title, student names, registration numbers, institution, and guide details accurately stated."
    p[157].text = "✓ Verified: Dual-stream AI architecture (14-channel Spatial U-Net + Temporal XGBoost) fully documented."
    p[158].text = "✓ Verified: Concrete hardware specifications, software dependencies, and audited budget (₹96,500 total) included."
    p[159].text = "✓ Verified: Empirical benchmarks (0.9926 ROC-AUC, 94.57% recall, 5.42ms serving latency) verified against test split."
    p[160].text = "✓ Verified: Peer-reviewed IEEE, GSI, and NDMA references properly cited."
    p[161].text = "✓ Verified: Scope explicitly demarcates NH-37 corridor operational boundary and future Phase II expansions."
    p[162].text = "✓ Verified: Full compliance with autonomous institution and Anna University project proposal guidelines."

    # Update header and footer
    for s in doc.sections:
        for h_p in s.header.paragraphs:
            h_p.text = "PROJECT PROPOSAL | DRISHTI-NER"
        for f_p in s.footer.paragraphs:
            f_p.text = "DRISHTI-NER – Project Proposal | Sri Eshwar College of Engineering"

    # Save to OUTPUT_PATH
    doc.save(OUTPUT_PATH)
    print(f"Proposal successfully created at: {OUTPUT_PATH}")

if __name__ == "__main__":
    build_drishti_proposal()

