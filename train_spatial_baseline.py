"""
Convenience CLI launcher for Landslide4Sense Spatial Base Training.
Run:
    python train_spatial_baseline.py --epochs 10 --batch_size 32 --loss combined
"""

import sys
import os

# Add workspace directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dl_spatial_base.train import train, argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Landslide4Sense Deep Learning Spatial Susceptibility Baseline")
    parser.add_argument("--data_dir", type=str, default=".", help="Dataset directory containing TrainData and ValidData")
    parser.add_argument("--output_dir", type=str, default="checkpoints", help="Directory where .pt models will be saved")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size (e.g. 16, 32, 64)")
    parser.add_argument("--lr", type=float, default=1e-3, help="Initial learning rate")
    parser.add_argument("--loss", type=str, default="combined", choices=["combined", "focal", "dice"], help="Loss function")
    parser.add_argument("--focal_alpha", type=float, default=0.75, help="Alpha parameter for Focal Loss")
    parser.add_argument("--focal_gamma", type=float, default=2.0, help="Gamma focusing parameter for Focal Loss")
    parser.add_argument("--num_workers", type=int, default=2, help="Number of DataLoader worker processes")
    parser.add_argument("--normalize", type=str, default="zscore", choices=["zscore", "minmax"], help="Per-band normalization method")
    parser.add_argument("--max_batches", type=int, default=None, help="Optional max batches per epoch for quick smoke-testing")

    args = parser.parse_args()

    print("=" * 80)
    print("LANDSLIDE4SENSE DEEP LEARNING SPATIAL BASELINE")
    print("=" * 80)
    print(f"Data Directory:     {os.path.abspath(args.data_dir)}")
    print(f"Output Directory:   {os.path.abspath(args.output_dir)}")
    print(f"Loss Function:      {args.loss.upper()} (Alpha: {args.focal_alpha}, Gamma: {args.focal_gamma})")
    print(f"Batch Size:         {args.batch_size} | Epochs: {args.epochs}")
    print(f"Normalization:      {args.normalize.upper()} (Strict per-band Sentinel-2 + ALOS DEM)")
    if args.max_batches is not None:
        print(f"Max Batches/Epoch:  {args.max_batches}")
    print("=" * 80)

    results = train(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        loss_type=args.loss,
        focal_alpha=args.focal_alpha,
        focal_gamma=args.focal_gamma,
        num_workers=args.num_workers,
        normalize_method=args.normalize,
        max_batches=args.max_batches,
    )

    print("\nSummary of Training:")
    print(f"Best Epoch: {results['best_epoch']} | Best Val F1 (Dice): {results['best_val_f1']:.4f}")
    print(f"Model checkpoint: {results['model_path']}")
    print(f"Spatial embedding weights: {results['embedding_path']}")
