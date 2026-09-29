"""
Training Pipeline for Landslide4Sense Spatial Susceptibility Segmentation.
Leverages NVIDIA CUDA acceleration, Mixed Precision (AMP), and Imbalance-Aware Losses.
Saves the final spatial susceptibility model and spatial embedding backbone weights as .pt files for backend integration.
"""

import os
import time
import argparse
from typing import Dict, Any, Tuple, Optional
import numpy as np
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR, ReduceLROnPlateau

from dl_spatial_base.dataset import get_landslide_dataloaders
from dl_spatial_base.losses import FocalLoss, DiceLoss, CombinedFocalDiceLoss
from dl_spatial_base.model import SpatialUNet, SpatialEmbeddingExtractor
from dl_spatial_base.hardware import setup_hardware_acceleration, log_vram_usage


def compute_metrics(logits: torch.Tensor, targets: torch.Tensor, threshold: float = 0.5) -> Dict[str, float]:
    """
    Computes precision, recall, F1 (Dice), and IoU for the positive landslide class.
    """
    probs = torch.sigmoid(logits)
    preds = (probs > threshold).float()
    targets = targets.float()

    # Flatten
    preds = preds.view(-1)
    targets = targets.view(-1)

    tp = (preds * targets).sum().item()
    fp = (preds * (1.0 - targets)).sum().item()
    fn = ((1.0 - preds) * targets).sum().item()
    tn = ((1.0 - preds) * (1.0 - targets)).sum().item()

    precision = tp / (tp + fp + 1e-7)
    recall = tp / (tp + fn + 1e-7)
    f1 = 2 * precision * recall / (precision + recall + 1e-7)
    iou = tp / (tp + fp + fn + 1e-7)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "iou": iou,
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }


def train_one_epoch(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    scaler: torch.amp.GradScaler,
    device_config,
    max_batches: Optional[int] = None,
) -> Tuple[float, Dict[str, float]]:
    model.train()
    running_loss = 0.0
    total_metrics = {"precision": 0.0, "recall": 0.0, "f1": 0.0, "iou": 0.0}
    num_batches = 0

    device = device_config.device
    use_amp = device_config.use_amp
    amp_dtype = device_config.amp_dtype
    non_blocking = device_config.non_blocking

    for inputs, targets in loader:
        if max_batches is not None and num_batches >= max_batches:
            break
        inputs = inputs.to(device, non_blocking=non_blocking)
        targets = targets.to(device, non_blocking=non_blocking)

        optimizer.zero_grad(set_to_none=True)

        # NVIDIA Automatic Mixed Precision (AMP)
        if use_amp and device.type == "cuda":
            with torch.amp.autocast(device_type="cuda", dtype=amp_dtype):
                logits = model(inputs)
                loss = criterion(logits, targets)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            logits = model(inputs)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()

        running_loss += loss.item()
        batch_metrics = compute_metrics(logits.detach(), targets)
        for k in total_metrics:
            total_metrics[k] += batch_metrics[k]
        num_batches += 1

    avg_loss = running_loss / max(num_batches, 1)
    avg_metrics = {k: v / max(num_batches, 1) for k, v in total_metrics.items()}
    return avg_loss, avg_metrics


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device_config,
    max_batches: Optional[int] = None,
) -> Tuple[float, Dict[str, float]]:
    model.eval()
    running_loss = 0.0
    total_metrics = {"precision": 0.0, "recall": 0.0, "f1": 0.0, "iou": 0.0}
    num_batches = 0

    device = device_config.device
    use_amp = device_config.use_amp
    amp_dtype = device_config.amp_dtype
    non_blocking = device_config.non_blocking

    for inputs, targets in loader:
        if max_batches is not None and num_batches >= max_batches:
            break
        inputs = inputs.to(device, non_blocking=non_blocking)
        targets = targets.to(device, non_blocking=non_blocking)

        if use_amp and device.type == "cuda":
            with torch.amp.autocast(device_type="cuda", dtype=amp_dtype):
                logits = model(inputs)
                loss = criterion(logits, targets)
        else:
            logits = model(inputs)
            loss = criterion(logits, targets)

        running_loss += loss.item()
        batch_metrics = compute_metrics(logits, targets)
        for k in total_metrics:
            total_metrics[k] += batch_metrics[k]
        num_batches += 1

    avg_loss = running_loss / max(num_batches, 1)
    avg_metrics = {k: v / max(num_batches, 1) for k, v in total_metrics.items()}
    return avg_loss, avg_metrics


def train(
    data_dir: str,
    output_dir: str = "checkpoints",
    epochs: int = 15,
    batch_size: int = 32,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    loss_type: str = "combined",
    focal_alpha: float = 0.75,
    focal_gamma: float = 2.0,
    dice_smooth: float = 1e-6,
    num_workers: int = 4,
    normalize_method: str = "zscore",
    max_batches: Optional[int] = None,
) -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)

    # 1. Hardware acceleration setup
    device_config = setup_hardware_acceleration(num_workers=num_workers)

    # 2. DataLoaders
    print(f"\n[DataLoader] Loading Landslide4Sense tensors from: {data_dir}")
    train_loader, val_loader, _ = get_landslide_dataloaders(
        data_dir=data_dir,
        batch_size=batch_size,
        num_workers=device_config.num_workers,
        pin_memory=device_config.pin_memory,
        persistent_workers=(device_config.num_workers > 0),
        normalize_method=normalize_method,
        augment_train=True,
    )
    print(f"[DataLoader] Train batches: {len(train_loader)} | Val batches: {len(val_loader)}")

    # 3. Model
    model = SpatialUNet(in_channels=14, out_channels=1, base_channels=64, embedding_dim=256)
    model.to(device_config.device)
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[Model Architecture] SpatialUNet (14 -> 1): {total_params / 1e6:.2f}M trainable parameters")

    # 4. Class Imbalance-Aware Loss Selection
    if loss_type == "focal":
        criterion = FocalLoss(alpha=focal_alpha, gamma=focal_gamma)
        print(f"[Loss Function] Binary Focal Loss (alpha={focal_alpha}, gamma={focal_gamma})")
    elif loss_type == "dice":
        criterion = DiceLoss(smooth=dice_smooth)
        print(f"[Loss Function] Soft Dice Loss (smooth={dice_smooth})")
    elif loss_type == "combined":
        criterion = CombinedFocalDiceLoss(
            alpha=focal_alpha,
            gamma=focal_gamma,
            smooth=dice_smooth,
            lambda_focal=1.0,
            lambda_dice=1.0,
        )
        print(f"[Loss Function] Combined Focal + Dice Loss (alpha={focal_alpha}, gamma={focal_gamma})")
    else:
        raise ValueError(f"Unknown loss_type: {loss_type}")

    # 5. Optimizer & Scaler
    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)
    scaler = torch.amp.GradScaler("cuda", enabled=(device_config.use_amp and device_config.device.type == "cuda"))

    best_val_f1 = 0.0
    best_epoch = 0
    history = []

    print("\n" + "=" * 80)
    print(f"{'Epoch':<6} | {'Train Loss':<10} | {'Train F1':<9} | {'Val Loss':<10} | {'Val F1':<8} | {'Val IoU':<8} | {'LR':<9} | {'Time':<6}")
    print("=" * 80)

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        train_loss, train_met = train_one_epoch(model, train_loader, criterion, optimizer, scaler, device_config, max_batches=max_batches)
        val_loss, val_met = evaluate(model, val_loader, criterion, device_config, max_batches=max_batches)
        scheduler.step()
        epoch_time = time.time() - t0

        curr_lr = optimizer.param_groups[0]["lr"]
        print(
            f"{epoch:<6} | {train_loss:<10.4f} | {train_met['f1']:<9.4f} | "
            f"{val_loss:<10.4f} | {val_met['f1']:<8.4f} | {val_met['iou']:<8.4f} | "
            f"{curr_lr:<9.2e} | {epoch_time:<5.1f}s"
        )

        history.append({
            "epoch": epoch,
            "train_loss": train_loss,
            "train_f1": train_met["f1"],
            "val_loss": val_loss,
            "val_f1": val_met["f1"],
            "val_iou": val_met["iou"],
            "lr": curr_lr,
        })

        # Save Best Checkpoint based on benchmark metric (Val F1 / Dice)
        if val_met["f1"] > best_val_f1 or epoch == 1:
            best_val_f1 = val_met["f1"]
            best_epoch = epoch

            # 1. Full model checkpoint (state_dict, optimizer, epoch, metrics)
            best_model_path = os.path.join(output_dir, "landslide_spatial_unet_best.pt")
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "val_f1": best_val_f1,
                    "val_iou": val_met["iou"],
                    "val_loss": val_loss,
                    "normalize_method": normalize_method,
                    "in_channels": 14,
                    "out_channels": 1,
                },
                best_model_path,
            )

            # 2. Final spatial embedding weights for backend integration
            embedding_extractor = SpatialEmbeddingExtractor(full_unet=model)
            backend_weights_path = os.path.join(output_dir, "spatial_embedding_backbone.pt")
            torch.save(
                {
                    "embedding_dim": 256,
                    "in_channels": 14,
                    "state_dict": embedding_extractor.state_dict(),
                    "description": "Static spatial terrain susceptibility embedding backbone for Landslide4Sense",
                },
                backend_weights_path,
            )

    print("=" * 80)
    print(f"\n[Training Complete] Best Validation F1: {best_val_f1:.4f} at Epoch {best_epoch}")
    print(f"[Saved Artifact] Full model checkpoint: {os.path.join(output_dir, 'landslide_spatial_unet_best.pt')}")
    print(f"[Saved Artifact] Spatial embedding backbone: {os.path.join(output_dir, 'spatial_embedding_backbone.pt')}")

    return {
        "best_epoch": best_epoch,
        "best_val_f1": best_val_f1,
        "history": history,
        "model_path": os.path.join(output_dir, "landslide_spatial_unet_best.pt"),
        "embedding_path": os.path.join(output_dir, "spatial_embedding_backbone.pt"),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Landslide Spatial Susceptibility Base")
    parser.add_argument("--data_dir", type=str, default=".", help="Root dataset directory containing TrainData and ValidData")
    parser.add_argument("--output_dir", type=str, default="checkpoints", help="Output directory for saved .pt weights")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--loss", type=str, default="combined", choices=["combined", "focal", "dice"], help="Loss function")
    parser.add_argument("--num_workers", type=int, default=4, help="Number of DataLoader workers")
    parser.add_argument("--normalize", type=str, default="zscore", choices=["zscore", "minmax"], help="Normalization method")
    parser.add_argument("--max_batches", type=int, default=None, help="Optional max batches per epoch for quick validation/benchmarking")

    args = parser.parse_args()
    train(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        loss_type=args.loss,
        num_workers=args.num_workers,
        normalize_method=args.normalize,
        max_batches=args.max_batches,
    )
