"""
Hardware Acceleration and NVIDIA CUDA Optimization Module.
Maximizes throughput for PyTorch model training and inference:
  - CuDNN Auto-Tuner (torch.backends.cudnn.benchmark = True)
  - Automatic Mixed Precision (AMP) with FP16/BF16 and GradScaler
  - Pinned memory asynchronous transfers (non_blocking=True)
  - GPU telemetry and VRAM tracking
"""

from dataclasses import dataclass
from typing import Tuple, Optional
import os
import torch


@dataclass
class DeviceConfig:
    device: torch.device
    device_name: str
    use_amp: bool
    amp_dtype: torch.dtype
    pin_memory: bool
    non_blocking: bool
    num_workers: int
    vram_gb: float


def setup_hardware_acceleration(
    prefer_cuda: bool = True,
    mixed_precision: bool = True,
    num_workers: Optional[int] = None,
) -> DeviceConfig:
    """
    Detects hardware capabilities and configures NVIDIA CUDA acceleration pipelines.
    
    Returns:
        DeviceConfig object with calibrated flags for DataLoader and training loops.
    """
    if prefer_cuda and torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        # Pre-flight check: verify that active PyTorch binary has compatible kernels for this GPU
        cuda_compatible = True
        try:
            test_x = torch.zeros(1, 1, 1, 1, device="cuda:0")
            test_conv = torch.nn.Conv2d(1, 1, 1).to("cuda:0")
            _ = test_conv(test_x)
            del test_x, test_conv
            torch.cuda.empty_cache()
        except RuntimeError as e:
            if "no kernel image is available" in str(e) or "CUDA capability" in str(e):
                print(f"[Hardware Warning] CUDA device {device_name} detected, but current PyTorch lacks sm_120 Blackwell kernels.")
                print("[Hardware Warning] Please ensure PyTorch with CUDA 12.8 (cu128) is active. Falling back to host execution.")
                cuda_compatible = False
            else:
                raise e

        if cuda_compatible:
            device = torch.device("cuda:0")
            vram_bytes = torch.cuda.get_device_properties(0).total_memory
            vram_gb = vram_bytes / (1024 ** 3)
            torch.backends.cudnn.benchmark = True

            if torch.cuda.is_bf16_supported():
                amp_dtype = torch.bfloat16
            else:
                amp_dtype = torch.float16

            if num_workers is None:
                num_workers = min(4, os.cpu_count() or 2)

            print(f"[Hardware Setup] Active Compute Device: {device_name}")
            print(f"[Hardware Setup] Total VRAM: {vram_gb:.2f} GB")
            print(f"[Hardware Setup] CuDNN Benchmark: Enabled")
            print(f"[Hardware Setup] Mixed Precision (AMP): {mixed_precision} ({amp_dtype})")
            print(f"[Hardware Setup] Host Pinned Memory: Enabled (Workers: {num_workers})")

            return DeviceConfig(
                device=device,
                device_name=device_name,
                use_amp=mixed_precision,
                amp_dtype=amp_dtype,
                pin_memory=True,
                non_blocking=True,
                num_workers=num_workers,
                vram_gb=vram_gb,
            )

    # CPU Fallback
    device = torch.device("cpu")
    device_name = "Host CPU"
    vram_gb = 0.0
    mixed_precision = False
    amp_dtype = torch.float32
    if num_workers is None:
        num_workers = 0
    print("[Hardware Setup] Active Compute Device: Host CPU")

    return DeviceConfig(
        device=device,
        device_name=device_name,
        use_amp=mixed_precision,
        amp_dtype=amp_dtype,
        pin_memory=False,
        non_blocking=False,
        num_workers=num_workers,
        vram_gb=vram_gb,
    )


def log_vram_usage(prefix: str = "") -> None:
    """Logs current GPU VRAM allocation and cached memory."""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / (1024 ** 2)
        reserved = torch.cuda.memory_reserved() / (1024 ** 2)
        print(f"[{prefix} VRAM] Allocated: {allocated:.1f} MB | Reserved: {reserved:.1f} MB")
