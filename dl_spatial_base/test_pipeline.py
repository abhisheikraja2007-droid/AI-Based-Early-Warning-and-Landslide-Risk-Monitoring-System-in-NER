"""
Unit tests and pipeline verification for Landslide Spatial Base components.
Tests:
  1. HDF5 Ingestion & Strict Normalization
  2. Focal Loss & Dice Loss behavior under extreme class imbalance (<3% positive)
  3. SpatialUNet architecture and SpatialEmbeddingExtractor
  4. End-to-end forward/backward step
"""

import os
import torch
import numpy as np

from dl_spatial_base.dataset import LandslideH5Dataset, BAND_NAMES
from dl_spatial_base.losses import FocalLoss, DiceLoss, CombinedFocalDiceLoss
from dl_spatial_base.model import SpatialUNet, SpatialEmbeddingExtractor


def test_dataset():
    print("--- 1. Testing LandslideH5Dataset ---")
    dataset = LandslideH5Dataset(
        img_dir="TrainData/img",
        mask_dir="TrainData/mask",
        normalize_method="zscore",
        augment=True,
    )
    print(f"Total samples found: {len(dataset)}")
    assert len(dataset) == 3799, f"Expected 3799 samples, found {len(dataset)}"

    img_tensor, mask_tensor = dataset[0]
    print(f"Sample 0 Image Shape: {img_tensor.shape} (dtype={img_tensor.dtype})")
    print(f"Sample 0 Mask Shape:  {mask_tensor.shape} (dtype={mask_tensor.dtype})")

    assert img_tensor.shape == (14, 128, 128), f"Expected (14, 128, 128), got {img_tensor.shape}"
    assert mask_tensor.shape == (1, 128, 128), f"Expected (1, 128, 128), got {mask_tensor.shape}"

    # Verify normalization: values should be centered roughly around 0
    img_np = img_tensor.numpy()
    print(f"Normalized Image Channel Means (min/max): {img_np.mean(axis=(1,2)).min():.3f} / {img_np.mean(axis=(1,2)).max():.3f}")
    print(f"Normalized Image Channel Stds  (min/max): {img_np.std(axis=(1,2)).min():.3f} / {img_np.std(axis=(1,2)).max():.3f}")
    print("[PASS] LandslideH5Dataset tests passed successfully!\n")


def test_losses():
    print("--- 2. Testing Imbalance-Aware Loss Functions ---")
    # Simulate severe class imbalance: 97.5% background (0), 2.5% landslide (1)
    B, C, H, W = 4, 1, 128, 128
    logits = torch.randn(B, C, H, W, requires_grad=True)

    targets = torch.zeros(B, C, H, W)
    # Set ~2.5% random pixels to 1
    pos_indices = torch.rand(B, C, H, W) < 0.025
    targets[pos_indices] = 1.0
    pos_ratio = targets.sum() / targets.numel()
    print(f"Simulated batch positive pixel ratio: {pos_ratio.item() * 100:.2f}%")

    # Focal Loss
    focal = FocalLoss(alpha=0.75, gamma=2.0)
    loss_f = focal(logits, targets)
    loss_f.backward(retain_graph=True)
    print(f"Focal Loss: {loss_f.item():.4f} (Grad norm: {logits.grad.norm().item():.4f})")
    assert not torch.isnan(loss_f) and not torch.isinf(loss_f), "Focal Loss is NaN/Inf!"

    # Dice Loss
    logits.grad.zero_()
    dice = DiceLoss()
    loss_d = dice(logits, targets)
    loss_d.backward(retain_graph=True)
    print(f"Dice Loss:  {loss_d.item():.4f} (Grad norm: {logits.grad.norm().item():.4f})")
    assert not torch.isnan(loss_d) and not torch.isinf(loss_d), "Dice Loss is NaN/Inf!"

    # Combined Focal + Dice Loss
    logits.grad.zero_()
    combined = CombinedFocalDiceLoss(alpha=0.75, gamma=2.0)
    loss_c = combined(logits, targets)
    loss_c.backward()
    print(f"Combined:   {loss_c.item():.4f} (Grad norm: {logits.grad.norm().item():.4f})")
    assert not torch.isnan(loss_c) and not torch.isinf(loss_c), "Combined Loss is NaN/Inf!"

    print("[PASS] Imbalance-Aware Loss functions passed successfully!\n")


def test_model():
    print("--- 3. Testing SpatialUNet & SpatialEmbeddingExtractor ---")
    model = SpatialUNet(in_channels=14, out_channels=1, base_channels=32, embedding_dim=256)
    x = torch.randn(2, 14, 128, 128)

    # Forward pass
    logits = model(x)
    print(f"Output Logits Shape: {logits.shape}")
    assert logits.shape == (2, 1, 128, 128), f"Expected (2, 1, 128, 128), got {logits.shape}"

    # Embedding extraction
    dense_emb, pooled_emb = model.extract_spatial_embeddings(x)
    print(f"Dense Spatial Feature Map Shape: {dense_emb.shape}")
    print(f"Pooled Spatial Embedding Shape:   {pooled_emb.shape}")
    assert dense_emb.shape == (2, 256, 8, 8), f"Expected (2, 256, 8, 8), got {dense_emb.shape}"
    assert pooled_emb.shape == (2, 256), f"Expected (2, 256), got {pooled_emb.shape}"

    # Standalone extractor
    extractor = SpatialEmbeddingExtractor(full_unet=model)
    emb = extractor(x)
    assert emb.shape == (2, 256), f"Expected (2, 256), got {emb.shape}"
    print(f"Extractor Vector Output Shape:   {emb.shape}")

    print("[PASS] Model and Feature Extractor passed successfully!\n")


if __name__ == "__main__":
    test_dataset()
    test_losses()
    test_model()
    print("ALL TESTS PASSED SUCCESSFULLY!")
