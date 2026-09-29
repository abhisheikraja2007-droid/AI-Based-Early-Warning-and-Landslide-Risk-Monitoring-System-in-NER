"""
Temporal Engine & Feature Fusion Module for Early Warning Landslide Prediction.
Combines:
  1. IMD 0.25° NetCDF Rainfall Grid Alignment
  2. Dynamic Rolling Temporal Features (24h event precipitation & 7d antecedent summation)
  3. Authentic NSIDC SMAP Satellite Soil Moisture Proxy Engine
  4. Targeted 6-to-24-hour Lead-Time Formulation
  5. XGBoost Classification with SHAP Explainable AI (XAI)
"""

from .grid_alignment import SpatialGridAligner
from .temporal_features import IMDRainfallFeatureEngine
from .smap_soil_moisture import SMAPSoilMoistureProxy
from .lead_time_dataset import LandslideLeadTimeDatasetBuilder
from .xgboost_trainer import LandslideTemporalXGBoostTrainer

__all__ = [
    "SpatialGridAligner",
    "IMDRainfallFeatureEngine",
    "SMAPSoilMoistureProxy",
    "LandslideLeadTimeDatasetBuilder",
    "LandslideTemporalXGBoostTrainer",
]
