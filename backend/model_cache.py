"""
Global In-Memory Model Cache for FastAPI Lifecycle.
Loads the PyTorch .pt model and native XGBoost .json model into memory exactly once on startup.
Eliminates high disk I/O and deserialization latency on individual HTTP requests.
"""

import os
import time
from typing import Dict, Any, Optional
import numpy as np
import torch
import xgboost as xgb
import shap

from backend.config import settings
from dl_spatial_base.inference import LandslideSpatialBackend
from temporal_engine.temporal_features import IMDRainfallFeatureEngine
from temporal_engine.smap_soil_moisture import SMAPSoilMoistureProxy
from temporal_engine.grid_alignment import SpatialGridAligner


class ModelCache:
    """
    Singleton in-memory model cache for PyTorch and XGBoost models.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.is_loaded = False
            cls._instance.spatial_backend = None
            cls._instance.temporal_model = None
            cls._instance.shap_explainer = None
            cls._instance.rain_engine = None
            cls._instance.smap_engine = None
            cls._instance.grid_aligner = None
            cls._instance.load_time_seconds = 0.0
        return cls._instance

    def load_models(self) -> None:
        """
        Loads models into memory exactly once during FastAPI startup.
        """
        if self.is_loaded:
            print("[ModelCache] Models are already loaded in memory.")
            return

        t0 = time.time()
        print("=" * 80)
        print("[ModelCache] STARTUP LIFECYCLE: Loading ML/DL models into memory...")
        print("=" * 80)

        # 1. Load PyTorch Spatial U-Net .pt checkpoint
        pt_path = settings.PYTORCH_SPATIAL_MODEL_PATH
        if os.path.exists(pt_path):
            print(f"[ModelCache] (1/4) Loading PyTorch Spatial Susceptibility Model from {pt_path}...")
            self.spatial_backend = LandslideSpatialBackend(model_path=pt_path)
            print("[ModelCache] -> PyTorch Spatial Model cached successfully.")
        else:
            print(f"[ModelCache Warning] PyTorch model checkpoint not found at: {pt_path}")

        # 2. Load XGBoost Temporal Engine .json model
        xgb_path = settings.XGBOOST_TEMPORAL_MODEL_PATH
        if os.path.exists(xgb_path):
            print(f"[ModelCache] (2/4) Loading XGBoost Temporal 6-24h Model from {xgb_path}...")
            self.temporal_model = xgb.XGBClassifier()
            self.temporal_model.load_model(xgb_path)
            print("[ModelCache] -> XGBoost .json model cached successfully.")

            # Bind shap.TreeExplainer once into memory
            print("[ModelCache] (3/4) Binding shap.TreeExplainer to cached XGBoost model...")
            import shap.explainers._tree as shap_tree
            if hasattr(shap_tree, "decode_ubjson_buffer") and not getattr(shap_tree, "_is_sih_patched", False):
                orig_decode = shap_tree.decode_ubjson_buffer
                def patched_decode(fd):
                    res = orig_decode(fd)
                    try:
                        bs = res["learner"]["learner_model_param"]["base_score"]
                        if isinstance(bs, str):
                            res["learner"]["learner_model_param"]["base_score"] = float(bs.strip("[]"))
                    except Exception:
                        pass
                    return res
                shap_tree.decode_ubjson_buffer = patched_decode
                shap_tree._is_sih_patched = True

            self.shap_explainer = shap.TreeExplainer(self.temporal_model)
            print("[ModelCache] -> SHAP TreeExplainer cached successfully.")
        else:
            print(f"[ModelCache Warning] XGBoost model file not found at: {xgb_path}")

        # 3. Load IMD NetCDF Dynamic Precipitation & SMAP Satellite Engines
        nc_path = settings.NC_RAINFALL_PATH
        if os.path.exists(nc_path):
            print(f"[ModelCache] (4/4) Initializing IMD NetCDF Engine & NSIDC SMAP Proxy from {nc_path}...")
            self.rain_engine = IMDRainfallFeatureEngine(nc_path=nc_path)
            self.smap_engine = SMAPSoilMoistureProxy()
            self.grid_aligner = SpatialGridAligner(nc_path=nc_path, spatial_model_path=pt_path)
            print("[ModelCache] -> Dynamic meteorological & satellite engines initialized.")

        self.is_loaded = True
        self.load_time_seconds = time.time() - t0
        print("=" * 80)
        print(f"[ModelCache] ALL MODELS LOADED & CACHED IN {self.load_time_seconds:.2f}s. READY FOR ZERO-LATENCY SERVING.")
        print("=" * 80)


model_cache = ModelCache()
