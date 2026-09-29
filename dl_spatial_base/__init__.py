"""
Deep Learning Spatial Base Package for Landslide4Sense Benchmark.
Provides Dataset, Loss Functions, Model Architectures, and Hardware Optimizations.
"""

from .dataset import LandslideH5Dataset, get_landslide_dataloaders
from .losses import FocalLoss, DiceLoss, CombinedFocalDiceLoss
from .model import SpatialUNet, SpatialEmbeddingExtractor
from .hardware import setup_hardware_acceleration, DeviceConfig

__all__ = [
    "LandslideH5Dataset",
    "get_landslide_dataloaders",
    "FocalLoss",
    "DiceLoss",
    "CombinedFocalDiceLoss",
    "SpatialUNet",
    "SpatialEmbeddingExtractor",
    "setup_hardware_acceleration",
    "DeviceConfig",
]
