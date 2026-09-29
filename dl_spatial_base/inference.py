"""
Inference & Backend Feature Extraction Module for Landslide Spatial Base.
Supports:
  - Continuous susceptibility probability prediction [0, 1]
  - Binary landslide segmentation mask generation
  - Extracting 256-dimensional spatial susceptibility embeddings for backend weather/rainfall fusion
"""

import os
from typing import Union, Tuple, Optional, Dict
import numpy as np
import h5py
import torch
import torch.nn.functional as F

from dl_spatial_base.model import SpatialUNet, SpatialEmbeddingExtractor
from dl_spatial_base.dataset import TRAIN_BAND_MEANS, TRAIN_BAND_STDS
from dl_spatial_base.hardware import setup_hardware_acceleration


class LandslideSpatialBackend:
    """
    Inference & Feature Extraction Engine designed for backend integration.
    """

    def __init__(
        self,
        model_path: str = "checkpoints/landslide_spatial_unet_best.pt",
        device: Optional[str] = None,
        normalize_method: str = "zscore",
    ):
        if device is None:
            hw_config = setup_hardware_acceleration(prefer_cuda=True)
            self.device = hw_config.device
        else:
            self.device = torch.device(device)

        self.normalize_method = normalize_method
        self.means = TRAIN_BAND_MEANS.copy()
        self.stds = TRAIN_BAND_STDS.copy()

        # Load weights
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model checkpoint not found at: {model_path}")

        print(f"[Backend Engine] Loading weights from {model_path} onto {self.device}...")
        checkpoint = torch.load(model_path, map_location=self.device)

        self.model = SpatialUNet(in_channels=14, out_channels=1, base_channels=64, embedding_dim=256)
        if "model_state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.val_f1 = checkpoint.get("val_f1", None)
            print(f"[Backend Engine] Loaded checkpoint (Checkpoint Val F1: {self.val_f1})")
        else:
            self.model.load_state_dict(checkpoint)

        self.model.to(self.device)
        self.model.eval()

        # Also initialize embedding extractor
        self.embedding_extractor = SpatialEmbeddingExtractor(full_unet=self.model)
        self.embedding_extractor.to(self.device)
        self.embedding_extractor.eval()

    def preprocess_tensor(self, img_array: np.ndarray) -> torch.Tensor:
        """
        Preprocesses a raw 128x128x14 satellite tensor.
        Performs NaN handling, optical/DEM clipping, and strict z-score normalization.
        """
        img = img_array.astype(np.float32)
        img = np.nan_to_num(img, nan=0.0, posinf=1.0, neginf=0.0)

        # Clip optical glints and DEM spikes
        optical_max = np.array([4.0, 8.0, 10.0, 10.0, 6.0, 5.0, 5.0, 6.0, 5.0, 10.0, 6.0, 8.0], dtype=np.float32)
        img[..., :12] = np.clip(img[..., :12], 0.0, optical_max)
        img[..., 12] = np.clip(img[..., 12], 0.0, 6.0)
        img[..., 13] = np.clip(img[..., 13], 0.0, 6.0)

        if self.normalize_method == "zscore":
            img = (img - self.means) / (self.stds + 1e-6)

        # (H, W, C) -> (1, C, H, W)
        tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).float()
        return tensor.to(self.device)

    @torch.no_grad()
    def predict_susceptibility(
        self,
        input_data: Union[str, np.ndarray, torch.Tensor],
        threshold: float = 0.5,
    ) -> Dict[str, np.ndarray]:
        """
        Generates continuous landslide susceptibility map and binary mask.
        
        Args:
            input_data: Either a path to an .h5 file, a numpy array (128, 128, 14),
                        or a torch.Tensor (1, 14, 128, 128).
            threshold: Probability threshold for binary landslide classification.
            
        Returns:
            Dictionary with:
              - 'probability_map': (128, 128) float32 array in [0.0, 1.0]
              - 'binary_mask': (128, 128) uint8 array in {0, 1}
              - 'susceptibility_score': scalar mean susceptibility over patch
        """
        if isinstance(input_data, str):
            with h5py.File(input_data, "r") as f:
                raw_img = f["img"][:]
            tensor = self.preprocess_tensor(raw_img)
        elif isinstance(input_data, np.ndarray):
            tensor = self.preprocess_tensor(input_data)
        elif isinstance(input_data, torch.Tensor):
            tensor = input_data.to(self.device)
        else:
            raise TypeError(f"Unsupported input type: {type(input_data)}")

        logits = self.model(tensor)
        probs = torch.sigmoid(logits).squeeze().cpu().numpy()
        binary_mask = (probs >= threshold).astype(np.uint8)

        return {
            "probability_map": probs,
            "binary_mask": binary_mask,
            "susceptibility_score": float(np.mean(probs)),
            "high_risk_ratio": float(np.mean(binary_mask)),
        }

    @torch.no_grad()
    def extract_spatial_embedding(
        self,
        input_data: Union[str, np.ndarray, torch.Tensor],
    ) -> np.ndarray:
        """
        Extracts 256-dimensional spatial susceptibility vector for backend fusion.
        """
        if isinstance(input_data, str):
            with h5py.File(input_data, "r") as f:
                raw_img = f["img"][:]
            tensor = self.preprocess_tensor(raw_img)
        elif isinstance(input_data, np.ndarray):
            tensor = self.preprocess_tensor(input_data)
        elif isinstance(input_data, torch.Tensor):
            tensor = input_data.to(self.device)
        else:
            raise TypeError(f"Unsupported input type: {type(input_data)}")

        embedding = self.embedding_extractor(tensor) # (1, 256)
        return embedding.squeeze().cpu().numpy()
