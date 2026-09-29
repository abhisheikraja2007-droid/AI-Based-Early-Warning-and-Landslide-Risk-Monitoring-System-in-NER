"""
Master Training Pipeline Launcher.
Trains both the Deep Learning Spatial Base and the XGBoost Temporal Engine.

Usage:
    python train_all.py --spatial --temporal
    python train_all.py --temporal  # Train only the 6-to-24h temporal classifier
    python train_all.py --spatial   # Train only the 14-channel PyTorch U-Net
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from train_spatial_baseline import train as train_spatial
from train_temporal_engine import run_pipeline as train_temporal


def main():
    parser = argparse.ArgumentParser(description="Master Landslide Early Warning Model Training Pipeline")
    parser.add_argument("--spatial", action="store_true", help="Train PyTorch 14-Channel Spatial U-Net")
    parser.add_argument("--temporal", action="store_true", help="Train XGBoost 6-to-24h Temporal Lead-Time Classifier")
    parser.add_argument("--spatial_epochs", type=int, default=10, help="Epochs for PyTorch U-Net")
    parser.add_argument("--spatial_batch_size", type=int, default=32, help="Batch size for PyTorch U-Net")
    parser.add_argument("--rebuild_dataset", action="store_true", default=False, help="Rebuild fused dataset from raw NetCDF")

    args = parser.parse_args()

    # If neither flag is passed, default to training both or prompting
    train_spatial_flag = args.spatial
    train_temporal_flag = args.temporal
    if not train_spatial_flag and not train_temporal_flag:
        train_spatial_flag = True
        train_temporal_flag = True

    print("=" * 80)
    print("AI-BASED LANDSLIDE EARLY WARNING: END-TO-END MODEL TRAINING")
    print("=" * 80)

    # 1. Train Deep Learning Spatial Base
    if train_spatial_flag:
        print("\n>>> [1/2] TRAINING DEEP LEARNING SPATIAL BASE (PyTorch U-Net) <<<")
        train_spatial(
            data_dir=".",
            output_dir="checkpoints",
            epochs=args.spatial_epochs,
            batch_size=args.spatial_batch_size,
            lr=1e-3,
            loss_type="combined",
            focal_alpha=0.75,
            focal_gamma=2.0,
            normalize_method="zscore",
        )

    # 2. Train XGBoost Temporal Engine
    if train_temporal_flag:
        print("\n>>> [2/2] TRAINING FEATURE FUSION & XGBOOST TEMPORAL ENGINE <<<")
        train_temporal(
            gsi_path="landslide_inventory.csv",
            nc_path="RF25_ind2025_rfp25.nc",
            spatial_model_path="checkpoints/landslide_spatial_unet_best.pt",
            output_dir="checkpoints",
            dataset_cache_path="fused_landslide_leadtime_dataset.csv",
            rebuild_dataset=args.rebuild_dataset,
        )

    print("\n" + "=" * 80)
    print("ALL MODELS TRAINED & SAVED IN 'checkpoints/' DIRECTORY.")
    print("=" * 80)


if __name__ == "__main__":
    main()
