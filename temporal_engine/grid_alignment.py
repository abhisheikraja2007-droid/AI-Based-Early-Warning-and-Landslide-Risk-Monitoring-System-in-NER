"""
Grid Alignment Engine:
Aligns high-resolution PyTorch spatial susceptibility outputs onto the 0.25° geographic grid
defined by the IMD (India Meteorological Department) NetCDF precipitation dataset.
"""

from typing import Tuple, Dict, Optional, Union
import numpy as np
import xarray as xr
import torch

from dl_spatial_base.inference import LandslideSpatialBackend


class SpatialGridAligner:
    """
    Coordinates transformation and spatial alignment between:
      1. High-resolution PyTorch Spatial U-Net susceptibility outputs
      2. IMD 0.25° x 0.25° NetCDF geographic grid (129 lat x 135 lon)
    """

    def __init__(
        self,
        nc_path: str = "RF25_ind2025_rfp25.nc",
        spatial_model_path: str = "checkpoints/landslide_spatial_unet_best.pt",
    ):
        self.nc_path = nc_path
        # Open dataset to extract geographic coordinate vectors
        ds = xr.open_dataset(nc_path)
        self.latitudes = ds["LATITUDE"].values.astype(np.float32)   # 129 elements: 6.5 to 38.5
        self.longitudes = ds["LONGITUDE"].values.astype(np.float32) # 135 elements: 66.5 to 100.0
        self.lat_step = 0.25
        self.lon_step = 0.25
        ds.close()

        # Load backend spatial model engine
        self.spatial_backend = None
        self.spatial_model_path = spatial_model_path

    def _ensure_backend_loaded(self):
        if self.spatial_backend is None:
            self.spatial_backend = LandslideSpatialBackend(model_path=self.spatial_model_path)

    def find_nearest_grid_cell(self, lat: float, lon: float) -> Tuple[int, int, float, float]:
        """
        Maps continuous (latitude, longitude) coordinate to nearest IMD 0.25° grid cell.
        
        Returns:
            (lat_idx, lon_idx, grid_lat, grid_lon)
        """
        lat_idx = int(np.argmin(np.abs(self.latitudes - lat)))
        lon_idx = int(np.argmin(np.abs(self.longitudes - lon)))
        grid_lat = float(self.latitudes[lat_idx])
        grid_lon = float(self.longitudes[lon_idx])
        return lat_idx, lon_idx, grid_lat, grid_lon

    def align_spatial_prediction(
        self,
        spatial_patch_h5_or_tensor: Union[str, np.ndarray, torch.Tensor],
    ) -> Dict[str, float]:
        """
        Flattens high-resolution (128x128) PyTorch spatial susceptibility outputs
        into summarized spatial vulnerability metrics calibrated for 0.25° grid fusion.
        
        Returns:
            Dictionary with:
              - 'spatial_susceptibility_mean': patch average probability [0, 1]
              - 'spatial_susceptibility_max': peak slope susceptibility
              - 'spatial_susceptibility_p90': 90th percentile susceptibility (focus on steep scarps)
              - 'spatial_high_risk_ratio': fraction of patch with susceptibility > 0.5
        """
        self._ensure_backend_loaded()
        pred = self.spatial_backend.predict_susceptibility(spatial_patch_h5_or_tensor)
        prob_map = pred["probability_map"]

        return {
            "spatial_susceptibility_mean": float(np.mean(prob_map)),
            "spatial_susceptibility_max": float(np.max(prob_map)),
            "spatial_susceptibility_p90": float(np.percentile(prob_map, 90)),
            "spatial_high_risk_ratio": float(np.mean(prob_map > 0.5)),
        }

    def generate_static_spatial_grid(
        self,
        gsi_inventory_df,
    ) -> np.ndarray:
        """
        Constructs a base spatial susceptibility grid (129, 135) across India
        by combining historical GSI geomorphological event density with terrain priors.
        """
        grid_susceptibility = np.zeros((len(self.latitudes), len(self.longitudes)), dtype=np.float32)
        counts = np.zeros_like(grid_susceptibility)

        for _, row in gsi_inventory_df.iterrows():
            lat = row.get("latitude")
            lon = row.get("longitude")
            if np.isnan(lat) or np.isnan(lon):
                continue
            if self.latitudes.min() <= lat <= self.latitudes.max() and self.longitudes.min() <= lon <= self.longitudes.max():
                lat_idx, lon_idx, _, _ = self.find_nearest_grid_cell(lat, lon)
                counts[lat_idx, lon_idx] += 1

        # Smooth counts with spatial gaussian kernel and normalize to [0, 1]
        from scipy.ndimage import gaussian_filter
        smoothed = gaussian_filter(counts, sigma=1.2)
        if smoothed.max() > 0:
            grid_susceptibility = smoothed / smoothed.max()

        return grid_susceptibility
