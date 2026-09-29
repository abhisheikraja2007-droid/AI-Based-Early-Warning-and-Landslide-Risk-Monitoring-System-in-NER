"""
Landslide4Sense Benchmark PyTorch Dataset.
Ingests 128x128x14 HDF5 multi-sensor satellite imagery (Sentinel-2 + ALOS PALSAR DEM & Slope).
Implements strict per-band normalization separating optical reflectance from elevation & slope topography.
"""

import os
import glob
from typing import Optional, Tuple, List, Union
import numpy as np
import h5py
import torch
from torch.utils.data import Dataset, DataLoader


# Exact channel definitions in Landslide4Sense benchmark
BAND_NAMES = [
    "B1_Coastal",       # Sentinel-2 Coastal aerosol (443 nm)
    "B2_Blue",          # Sentinel-2 Blue (490 nm)
    "B3_Green",         # Sentinel-2 Green (560 nm)
    "B4_Red",           # Sentinel-2 Red (665 nm)
    "B5_VRE1",          # Sentinel-2 Vegetation Red Edge (705 nm)
    "B6_VRE2",          # Sentinel-2 Vegetation Red Edge (740 nm)
    "B7_VRE3",          # Sentinel-2 Vegetation Red Edge (783 nm)
    "B8_NIR",           # Sentinel-2 NIR wide (842 nm)
    "B8A_NarrowNIR",    # Sentinel-2 NIR narrow (865 nm)
    "B9_WaterVapour",   # Sentinel-2 Water vapour (945 nm)
    "B11_SWIR1",        # Sentinel-2 SWIR-1 (1610 nm)
    "B12_SWIR2",        # Sentinel-2 SWIR-2 (2190 nm)
    "ALOS_DEM",         # ALOS PALSAR Digital Elevation Model
    "ALOS_Slope",       # ALOS PALSAR Topographic Slope
]

# Globally computed channel statistics across all 3,799 training patches (62.24M pixels)
TRAIN_BAND_MEANS = np.array([
    0.925704, 0.922701, 0.954109, 0.959639, 1.022790, 1.042612, 1.035844,
    1.046756, 1.169941, 1.173598, 1.049497, 1.037032, 1.251108, 1.649543
], dtype=np.float32)

TRAIN_BAND_STDS = np.array([
    0.140988, 0.220698, 0.318425, 0.572375, 0.460096, 0.446514, 0.465075,
    0.494845, 0.513311, 0.683558, 0.532293, 0.662800, 0.678369, 1.072711
], dtype=np.float32)

TRAIN_BAND_MINS = np.array([
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
], dtype=np.float32)

TRAIN_BAND_MAXS = np.array([
    3.105740, 19.761549, 31.551830, 33.160150,  9.972776,  4.144120,
    3.692531,  8.312891,  3.548563, 21.441501,  5.786442, 19.661323,
    4.040945,  5.121427
], dtype=np.float32)


class LandslideH5Dataset(Dataset):
    """
    Custom PyTorch Dataset for Landslide4Sense multi-sensor satellite imagery.
    
    Each sample consists of:
      - Raw HDF5 array of shape (128, 128, 14) stored under key 'img'
        - Bands 0..11: Sentinel-2 optical reflectance bands
        - Band 12: ALOS PALSAR DEM (Elevation)
        - Band 13: ALOS PALSAR Slope (Topographic incline)
      - Binary ground-truth mask of shape (128, 128) stored under key 'mask' (1 = Landslide, 0 = Background)
    
    Strict Normalization Strategy:
      Because elevation and slope differ fundamentally in dynamic range and physical units from optical reflectance:
      1. Z-Score Standardization: (X - mu) / (sigma + eps) per individual band.
      2. Robust Percentile Clipping: Mitigates extreme specular glints/cloud saturation in optical bands
         and sharp ridge artifacts in DEM/slope without distorting the underlying distributions.
      3. Min-Max Scaling (Optional): Rescales each band to [0, 1] or [-1, 1].
    """

    def __init__(
        self,
        img_dir: str,
        mask_dir: Optional[str] = None,
        normalize_method: str = "zscore",
        clip_outliers: bool = True,
        augment: bool = False,
        means: Optional[np.ndarray] = None,
        stds: Optional[np.ndarray] = None,
    ):
        """
        Args:
            img_dir: Directory containing image HDF5 files (*.h5).
            mask_dir: Directory containing mask HDF5 files (*.h5). If None, dataset operates in test/unsupervised mode.
            normalize_method: 'zscore', 'minmax', or 'none'.
            clip_outliers: Whether to clip extreme optical glints and elevation spikes before z-score scaling.
            augment: Whether to apply spatial augmentations (rotations, flips).
            means: Custom per-band mean array (14,). If None, uses benchmark global means.
            stds: Custom per-band std array (14,). If None, uses benchmark global stds.
        """
        super().__init__()
        self.img_dir = img_dir
        self.mask_dir = mask_dir
        self.normalize_method = normalize_method
        self.clip_outliers = clip_outliers
        self.augment = augment

        # Locate image files
        self.img_paths = sorted(glob.glob(os.path.join(img_dir, "*.h5")))
        if len(self.img_paths) == 0:
            raise FileNotFoundError(f"No .h5 files found in image directory: {img_dir}")

        # Normalization constants (14 channels)
        self.means = means if means is not None else TRAIN_BAND_MEANS.copy()
        self.stds = stds if stds is not None else TRAIN_BAND_STDS.copy()
        self.mins = TRAIN_BAND_MINS.copy()
        self.maxs = TRAIN_BAND_MAXS.copy()

        # Check if masks exist
        self.has_masks = mask_dir is not None and os.path.exists(mask_dir)
        if self.has_masks:
            self.mask_paths = []
            for img_path in self.img_paths:
                basename = os.path.basename(img_path)
                # Handle image_X.h5 -> mask_X.h5 mapping
                mask_name = basename.replace("image_", "mask_")
                mask_path = os.path.join(mask_dir, mask_name)
                if not os.path.exists(mask_path):
                    # Fallback to direct name match
                    mask_path = os.path.join(mask_dir, basename)
                if not os.path.exists(mask_path):
                    raise FileNotFoundError(f"Could not find matching mask for {basename} at {mask_path}")
                self.mask_paths.append(mask_path)
        else:
            self.mask_paths = None

    def __len__(self) -> int:
        return len(self.img_paths)

    def _normalize(self, img: np.ndarray) -> np.ndarray:
        """
        Strict per-channel normalization:
        - Sentinel-2 optical bands (0..11): optical reflectance
        - ALOS PALSAR DEM (12): elevation in km/standardized height
        - ALOS PALSAR Slope (13): topographic incline
        """
        # Ensure float32 for model computation
        img = img.astype(np.float32)

        # Replace any potential NaNs or Infs with channel medians/means
        if np.isnan(img).any() or np.isinf(img).any():
            img = np.nan_to_num(img, nan=0.0, posinf=1.0, neginf=0.0)

        if self.clip_outliers:
            # Clip extreme optical glints (> 99.9th percentile) and topographic spikes
            # Optical bands (0..11) can spike due to cloud reflections
            # Elevation & slope bands (12, 13)
            optical_max = np.array([4.0, 8.0, 10.0, 10.0, 6.0, 5.0, 5.0, 6.0, 5.0, 10.0, 6.0, 8.0], dtype=np.float32)
            img[..., :12] = np.clip(img[..., :12], 0.0, optical_max)
            img[..., 12] = np.clip(img[..., 12], 0.0, 6.0) # DEM
            img[..., 13] = np.clip(img[..., 13], 0.0, 6.0) # Slope

        if self.normalize_method == "zscore":
            # Per-band standardization: (X - mean) / std
            eps = 1e-6
            img = (img - self.means) / (self.stds + eps)
        elif self.normalize_method == "minmax":
            # Min-Max scaling to [0, 1]
            diff = self.maxs - self.mins
            diff[diff == 0] = 1.0
            img = (img - self.mins) / diff
            img = np.clip(img, 0.0, 1.0)
        elif self.normalize_method == "none":
            pass
        else:
            raise ValueError(f"Unknown normalize_method: {self.normalize_method}")

        return img

    def _apply_augmentations(self, img: np.ndarray, mask: Optional[np.ndarray]) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Synchronized spatial data augmentations across all 14 channels and the 1-channel mask.
        Supports random horizontal flip, vertical flip, and 90-degree rotations.
        """
        # Random horizontal flip
        if np.random.rand() > 0.5:
            img = np.fliplr(img).copy()
            if mask is not None:
                mask = np.fliplr(mask).copy()

        # Random vertical flip
        if np.random.rand() > 0.5:
            img = np.flipud(img).copy()
            if mask is not None:
                mask = np.flipud(mask).copy()

        # Random 90, 180, or 270 degree rotation
        rot_k = np.random.randint(0, 4)
        if rot_k > 0:
            img = np.rot90(img, k=rot_k, axes=(0, 1)).copy()
            if mask is not None:
                mask = np.rot90(mask, k=rot_k, axes=(0, 1)).copy()

        return img, mask

    def __getitem__(self, idx: int) -> Union[Tuple[torch.Tensor, torch.Tensor], torch.Tensor]:
        img_path = self.img_paths[idx]

        # Read HDF5 safely inside getitem to avoid multiprocessing file lock contention
        with h5py.File(img_path, "r") as hf:
            # Shape: (128, 128, 14)
            img = hf["img"][:]

        mask = None
        if self.has_masks:
            mask_path = self.mask_paths[idx]
            with h5py.File(mask_path, "r") as hf:
                # Shape: (128, 128)
                mask = hf["mask"][:]

        # Apply synchronized spatial augmentations
        if self.augment:
            img, mask = self._apply_augmentations(img, mask)

        # Apply strict per-channel normalization
        img = self._normalize(img)

        # Convert to PyTorch tensors
        # Channels-first format: (H, W, C) -> (C, H, W)
        img_tensor = torch.from_numpy(img).permute(2, 0, 1).float()

        if self.has_masks:
            # Mask format: (1, H, W) float32 for binary loss computation
            mask_tensor = torch.from_numpy(mask).unsqueeze(0).float()
            return img_tensor, mask_tensor
        else:
            return img_tensor


def get_landslide_dataloaders(
    data_dir: str,
    batch_size: int = 32,
    num_workers: int = 4,
    pin_memory: bool = True,
    persistent_workers: bool = True,
    normalize_method: str = "zscore",
    augment_train: bool = True,
) -> Tuple[DataLoader, DataLoader, Optional[DataLoader]]:
    """
    Constructs high-throughput PyTorch DataLoaders for Landslide4Sense.
    
    Args:
        data_dir: Root directory containing TrainData/, ValidData/, and optional TestData/.
        batch_size: Training and validation batch size.
        num_workers: Number of DataLoader subprocesses for asynchronous disk I/O.
        pin_memory: Fast host-to-device pinned memory transfers for CUDA.
        persistent_workers: Retains worker processes across epochs for maximum throughput.
        normalize_method: 'zscore' or 'minmax'.
        augment_train: Apply random flips/rotations to training set.
        
    Returns:
        (train_loader, val_loader, test_loader)
    """
    train_img_dir = os.path.join(data_dir, "TrainData", "img")
    train_mask_dir = os.path.join(data_dir, "TrainData", "mask")
    val_img_dir = os.path.join(data_dir, "ValidData", "img")
    val_mask_dir = os.path.join(data_dir, "ValidData", "mask")
    test_img_dir = os.path.join(data_dir, "TestData", "img")

    train_dataset = LandslideH5Dataset(
        img_dir=train_img_dir,
        mask_dir=train_mask_dir,
        normalize_method=normalize_method,
        augment=augment_train,
    )

    val_dataset = LandslideH5Dataset(
        img_dir=val_img_dir,
        mask_dir=val_mask_dir,
        normalize_method=normalize_method,
        augment=False,
    )

    # Multi-worker persistent workers settings
    use_persistent = persistent_workers and num_workers > 0

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=use_persistent,
        drop_last=True,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=use_persistent,
        drop_last=False,
    )

    test_loader = None
    if os.path.exists(test_img_dir):
        test_dataset = LandslideH5Dataset(
            img_dir=test_img_dir,
            mask_dir=None,
            normalize_method=normalize_method,
            augment=False,
        )
        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
            persistent_workers=use_persistent,
            drop_last=False,
        )

    return train_loader, val_loader, test_loader
