"""
Temporal Dynamic Feature Engineering Module:
Calculates dynamic rolling precipitation features directly from the IMD 0.25° NetCDF grid.
Computes:
  - 24-hour event precipitation
  - 7-day antecedent precipitation summation
  - 3-day short-term surge summation
  - Antecedent Precipitation Index (API) with soil drainage decay
  - Rainfall intensity anomaly and acceleration
"""

from typing import Tuple, Dict, Optional, Union
import numpy as np
import pandas as pd
import xarray as xr


class IMDRainfallFeatureEngine:
    """
    High-throughput feature engine for IMD 0.25° gridded daily precipitation.
    Grid: (365 days, 129 latitudes, 135 longitudes)
    """

    def __init__(self, nc_path: str = "RF25_ind2025_rfp25.nc"):
        self.nc_path = nc_path
        ds = xr.open_dataset(nc_path)
        self.times = pd.to_datetime(ds["TIME"].values)
        self.latitudes = ds["LATITUDE"].values.astype(np.float32)
        self.longitudes = ds["LONGITUDE"].values.astype(np.float32)

        # Load rainfall array (365, 129, 135)
        raw_rainfall = ds["RAINFALL"].values.astype(np.float32)
        # Clean fill values (-999.0 or NaNs)
        raw_rainfall = np.where((raw_rainfall < 0) | np.isnan(raw_rainfall), 0.0, raw_rainfall)
        self.rainfall = raw_rainfall
        ds.close()

        # Date to index lookup
        self.date_to_idx = {d.strftime("%Y-%m-%d"): i for i, d in enumerate(self.times)}
        self.precompute_rolling_grids()

    def precompute_rolling_grids(self):
        """
        Vectorized pre-computation of dynamic rolling features across all 365 days and grid points.
        """
        T, H, W = self.rainfall.shape

        # 1. 24-hour event precipitation (daily rainfall at time t)
        self.r24h_grid = self.rainfall.copy()

        # 2. 7-day antecedent summation: sum_{k=1..7} R(t - k)
        self.r7d_grid = np.zeros_like(self.rainfall)
        # 3. 3-day short-term deluge: sum_{k=1..3} R(t - k)
        self.r3d_grid = np.zeros_like(self.rainfall)
        # 4. Antecedent Precipitation Index (API): sum_{k=1..7} (0.85^k) * R(t - k)
        self.api7d_grid = np.zeros_like(self.rainfall)

        decay_weights = np.array([0.85 ** k for k in range(1, 8)], dtype=np.float32)

        for t in range(T):
            if t > 0:
                # 3-day window
                start_3d = max(0, t - 3)
                self.r3d_grid[t] = np.sum(self.rainfall[start_3d:t], axis=0)

                # 7-day window
                start_7d = max(0, t - 7)
                window_7d = self.rainfall[start_7d:t]
                self.r7d_grid[t] = np.sum(window_7d, axis=0)

                # API calculation
                num_days = window_7d.shape[0]
                weights = decay_weights[:num_days][::-1, None, None]
                self.api7d_grid[t] = np.sum(window_7d * weights, axis=0)

    def extract_point_temporal_features(
        self,
        lat: float,
        lon: float,
        date_str: str,
        lead_time_hours: int = 12,
    ) -> Dict[str, float]:
        """
        Extracts temporal rolling rainfall features for a specific location and early-warning date.
        
        Args:
            lat: Latitude (e.g. 11.5)
            lon: Longitude (e.g. 76.2)
            date_str: Target date string 'YYYY-MM-DD'
            lead_time_hours: Warning lead time (6 to 24 hours).
                            At 6-to-24h lead time, the observation time t_obs is strictly prior to event day.
        """
        # Parse date
        target_date = pd.to_datetime(date_str)
        # When predicting 6-24h out, observation day is the day immediately preceding the event
        obs_date = (target_date - pd.Timedelta(days=1)).strftime("%Y-%m-%d")

        if obs_date not in self.date_to_idx:
            # Fallback to closest available date in 2025
            t_idx = 0 if target_date.year < 2025 else len(self.times) - 1
        else:
            t_idx = self.date_to_idx[obs_date]

        # Find nearest 0.25° grid indices
        lat_idx = int(np.argmin(np.abs(self.latitudes - lat)))
        lon_idx = int(np.argmin(np.abs(self.longitudes - lon)))

        r24h = float(self.r24h_grid[t_idx, lat_idx, lon_idx])
        r3d = float(self.r3d_grid[t_idx, lat_idx, lon_idx])
        r7d = float(self.r7d_grid[t_idx, lat_idx, lon_idx])
        api7d = float(self.api7d_grid[t_idx, lat_idx, lon_idx])

        # Intensity anomaly: 24h event vs. daily average of prior 7 days
        daily_prior_mean = r7d / 7.0
        intensity_ratio = (r24h + 1e-4) / (daily_prior_mean + 1.0)
        rainfall_acceleration = r24h - daily_prior_mean

        return {
            "rainfall_24h_mm": r24h,
            "rainfall_3d_sum_mm": r3d,
            "rainfall_7d_antecedent_mm": r7d,
            "rainfall_api_7d": api7d,
            "rainfall_intensity_ratio": intensity_ratio,
            "rainfall_acceleration_mm": rainfall_acceleration,
            "grid_lat": float(self.latitudes[lat_idx]),
            "grid_lon": float(self.longitudes[lon_idx]),
            "lead_time_hours": lead_time_hours,
        }
