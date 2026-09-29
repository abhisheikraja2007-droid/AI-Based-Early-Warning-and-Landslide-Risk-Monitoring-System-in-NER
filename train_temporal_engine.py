"""
Main Execution Script for Feature Fusion & XGBoost Temporal Engine.
Constructs targeted 6-to-24-hour lead-time dataset:
  1. PyTorch spatial susceptibility aligned onto IMD 0.25° grid
  2. Dynamic rolling features from IMD NetCDF (24h event rain & 7d antecedent summation)
  3. NASA/NSIDC SMAP satellite soil moisture proxy
  4. XGBoost Classifier trained on 6-to-24-hour early warning window
  5. shap.TreeExplainer binding for transparent XAI
"""

import sys
import os
import argparse
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from temporal_engine.lead_time_dataset import LandslideLeadTimeDatasetBuilder
from temporal_engine.xgboost_trainer import LandslideTemporalXGBoostTrainer


def run_pipeline(
    gsi_path: str = "landslide_inventory.csv",
    nc_path: str = "RF25_ind2025_rfp25.nc",
    spatial_model_path: str = "checkpoints/landslide_spatial_unet_best.pt",
    output_dir: str = "checkpoints",
    dataset_cache_path: str = "fused_landslide_leadtime_dataset.csv",
    rebuild_dataset: bool = True,
):
    print("=" * 80)
    print("LANDSLIDE FEATURE FUSION & XGBOOST TEMPORAL ENGINE")
    print("Target Lead Time: 6-to-24 Hours Ahead of Trigger Event")
    print("=" * 80)

    # Step 1: Build or load fused tabular dataset
    if os.path.exists(dataset_cache_path) and not rebuild_dataset:
        print(f"\n[Step 1] Loading cached fused dataset from: {dataset_cache_path}")
        fused_df = pd.read_csv(dataset_cache_path)
    else:
        print("\n[Step 1] Building multimodal fused dataset from GSI inventory, IMD NetCDF, and SMAP proxy...")
        builder = LandslideLeadTimeDatasetBuilder(
            gsi_csv_path=gsi_path,
            nc_rainfall_path=nc_path,
            spatial_model_path=spatial_model_path,
        )
        fused_df = builder.build_fused_dataset(target_year=2025, negative_ratio=3.0)
        fused_df.to_csv(dataset_cache_path, index=False)
        print(f"[Step 1] Fused dataset saved to: {dataset_cache_path}")

    # Step 2: Display dataset summary and correlation
    print(f"\n[Step 2] Dataset Shape: {fused_df.shape}")
    print("\nFeature Summary Statistics (Grouped by Landslide Target):")
    summary_cols = [
        "spatial_susceptibility",
        "rainfall_24h_mm",
        "rainfall_7d_antecedent_mm",
        "smap_surface_sm",
        "smap_rootzone_sm",
        "smap_saturation_ratio",
    ]
    print(fused_df.groupby("target_landslide_6_to_24h")[summary_cols].mean().round(4))

    # Step 3: Train XGBoost Classifier on 6-24h window
    print("\n[Step 3] Training XGBoost Classifier on 6-to-24h Early Warning Horizon...")
    trainer = LandslideTemporalXGBoostTrainer(
        output_dir=output_dir,
        n_estimators=150,
        max_depth=4,
        learning_rate=0.05,
    )
    results = trainer.train_and_evaluate(fused_df, test_size=0.20)

    # Step 4: Test Explainable AI on a representative early warning alert
    print("\n[Step 4] Demonstrating SHAP TreeExplainer on a High-Risk Verification Alert:")
    pos_sample = fused_df[fused_df["target_landslide_6_to_24h"] == 1].iloc[0].to_dict()
    explanation = trainer.explain_instance(pos_sample)

    print(f"\nAlert Status:             {explanation['early_warning_status']}")
    print(f"Predicted Risk Probability: {explanation['predicted_risk_probability'] * 100:.1f}%")
    print(f"Lead Time Window:           {explanation['lead_time_window']}")
    print("\nTop Contributing Factors to Alert Decision:")
    for f in explanation["driving_factors"][:5]:
        effect = f.get('effect', '')
        shap_val = f.get('shap_contribution', 0.0)
        print(f"  * {f['feature']:<28} = {f['measured_value']:<8} (SHAP: {shap_val:+.4f} -> {effect})")

    print("\n" + "=" * 80)
    print("[SUCCESS] Feature Fusion & XGBoost Temporal Engine pipeline complete!")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Landslide Temporal Engine")
    parser.add_argument("--gsi_path", type=str, default="landslide_inventory.csv")
    parser.add_argument("--nc_path", type=str, default="RF25_ind2025_rfp25.nc")
    parser.add_argument("--spatial_model", type=str, default="checkpoints/landslide_spatial_unet_best.pt")
    parser.add_argument("--output_dir", type=str, default="checkpoints")
    parser.add_argument("--rebuild", action="store_true", default=True)

    args = parser.parse_args()
    run_pipeline(
        gsi_path=args.gsi_path,
        nc_path=args.nc_path,
        spatial_model_path=args.spatial_model,
        output_dir=args.output_dir,
        rebuild_dataset=args.rebuild,
    )
