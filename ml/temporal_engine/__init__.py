"""
Temporal Engine & Feature Fusion Module for Early Warning Landslide Prediction.
Combines:
  1. IMD 0.25° NetCDF Rainfall Grid Alignment
  2. Dynamic Rolling Temporal Features (24h event precipitation & 7d antecedent summation)
  3. Authentic NSIDC SMAP Satellite Soil Moisture Proxy Engine
  4. Targeted 6-to-24-hour Lead-Time Formulation
  5. XGBoost Classification with SHAP Explainable AI (XAI)
"""

try:
    from .grid_alignment import SpatialGridAligner
except Exception:
    SpatialGridAligner = None

try:
    from .temporal_features import IMDRainfallFeatureEngine
except Exception:
    IMDRainfallFeatureEngine = None

try:
    from .smap_soil_moisture import SMAPSoilMoistureProxy
except Exception:
    SMAPSoilMoistureProxy = None

try:
    from .lead_time_dataset import LandslideLeadTimeDatasetBuilder
except Exception:
    LandslideLeadTimeDatasetBuilder = None

try:
    from .xgboost_trainer import LandslideTemporalXGBoostTrainer
except Exception:
    LandslideTemporalXGBoostTrainer = None

__all__ = [
    "SpatialGridAligner",
    "IMDRainfallFeatureEngine",
    "SMAPSoilMoistureProxy",
    "LandslideLeadTimeDatasetBuilder",
    "LandslideTemporalXGBoostTrainer",
]
