"""
U-Net Deep Learning Architecture for Spatial Landslide Susceptibility Segmentation.
Ingests 14-channel multi-sensor tensors (Sentinel-2 multispectral + ALOS DEM + ALOS Slope).
Features:
  - 14-channel multi-sensor input projection
  - DoubleConv residual/conv blocks with BatchNorm and GELU activations
  - Multi-scale skip connections
  - Latent spatial embedding bottleneck for downstream backend feature extraction
  - Binary landslide probability head
"""

from typing import Tuple, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F


class DoubleConv(nn.Module):
    """[Conv2d -> BatchNorm2d -> GELU] x 2 with optional residual connection."""

    def __init__(self, in_channels: int, out_channels: int, mid_channels: Optional[int] = None):
        super().__init__()
        if not mid_channels:
            mid_channels = out_channels
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, mid_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(mid_channels),
            nn.GELU(),
            nn.Conv2d(mid_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.GELU(),
        )
        self.residual = (
            nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)
            if in_channels != out_channels
            else nn.Identity()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.double_conv(x) + self.residual(x)


class DownBlock(nn.Module):
    """Downscaling with MaxPool then DoubleConv."""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.maxpool_conv(x)


class UpBlock(nn.Module):
    """Upscaling then DoubleConv with skip connection."""

    def __init__(self, in_channels: int, out_channels: int, bilinear: bool = True):
        super().__init__()
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True)
            self.conv = DoubleConv(in_channels, out_channels, in_channels // 2)
        else:
            self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
            self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        x1 = self.up(x1)
        # Pad if input dimensions differ slightly
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]
        if diffX != 0 or diffY != 0:
            x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2, diffY // 2, diffY - diffY // 2])
        # Concatenate along channel axis
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class SpatialUNet(nn.Module):
    """
    14-channel Spatial U-Net for Landslide Susceptibility Segmentation.
    
    Architecture:
      - Multi-Sensor Input: (B, 14, 128, 128)
      - Encoder:
          inc   -> (B, 64, 128, 128)
          down1 -> (B, 128, 64, 64)
          down2 -> (B, 256, 32, 32)
          down3 -> (B, 512, 16, 16)
      - Latent Bottleneck (Spatial Embedding Layer):
          bottleneck -> (B, 512, 16, 16)
      - Decoder:
          up1   -> (B, 256, 32, 32)
          up2   -> (B, 128, 64, 64)
          up3   -> (B, 64, 128, 128)
      - Output Head:
          outc  -> (B, 1, 128, 128) raw logits for susceptibility
    """

    def __init__(
        self,
        in_channels: int = 14,
        out_channels: int = 1,
        base_channels: int = 64,
        bilinear: bool = True,
        embedding_dim: int = 256,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.bilinear = bilinear
        self.embedding_dim = embedding_dim

        # Encoder stages
        self.inc = DoubleConv(in_channels, base_channels)
        self.down1 = DownBlock(base_channels, base_channels * 2)
        self.down2 = DownBlock(base_channels * 2, base_channels * 4)
        self.down3 = DownBlock(base_channels * 4, base_channels * 8)

        factor = 2 if bilinear else 1
        self.down4 = DownBlock(base_channels * 8, (base_channels * 16) // factor)

        # Spatial embedding projector at bottleneck (16x16 resolution)
        self.embedding_proj = nn.Sequential(
            nn.Conv2d((base_channels * 16) // factor, embedding_dim, kernel_size=1),
            nn.BatchNorm2d(embedding_dim),
            nn.GELU(),
        )

        # Decoder stages
        self.up1 = UpBlock(base_channels * 16, (base_channels * 8) // factor, bilinear)
        self.up2 = UpBlock(base_channels * 8, (base_channels * 4) // factor, bilinear)
        self.up3 = UpBlock(base_channels * 4, (base_channels * 2) // factor, bilinear)
        self.up4 = UpBlock(base_channels * 2, base_channels, bilinear)

        # Output segmentation head
        self.outc = nn.Conv2d(base_channels, out_channels, kernel_size=1)

    def extract_spatial_embeddings(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Extracts spatial susceptibility embeddings for downstream backend integration:
        Returns:
            dense_embedding: Latent feature map (B, embedding_dim, 8, 8)
            pooled_embedding: Global terrain embedding vector (B, embedding_dim)
        """
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        dense_embedding = self.embedding_proj(x5)
        pooled_embedding = F.adaptive_avg_pool2d(dense_embedding, (1, 1)).flatten(1)
        return dense_embedding, pooled_embedding

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for segmentation.
        Args:
            x: Input satellite tensor of shape (B, 14, 128, 128)
        Returns:
            logits: Output susceptibility logits of shape (B, 1, 128, 128)
        """
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)

        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        logits = self.outc(x)
        return logits


class SpatialEmbeddingExtractor(nn.Module):
    """
    Lightweight backend spatial embedding backbone.
    Extracts static susceptibility embeddings directly from 14-channel imagery
    for fusion with dynamic weather/precipitation features.
    """

    def __init__(self, full_unet: Optional[SpatialUNet] = None, in_channels: int = 14, embedding_dim: int = 256):
        super().__init__()
        if full_unet is not None:
            self.inc = full_unet.inc
            self.down1 = full_unet.down1
            self.down2 = full_unet.down2
            self.down3 = full_unet.down3
            self.down4 = full_unet.down4
            self.embedding_proj = full_unet.embedding_proj
        else:
            base_channels = 64
            factor = 2
            self.inc = DoubleConv(in_channels, base_channels)
            self.down1 = DownBlock(base_channels, base_channels * 2)
            self.down2 = DownBlock(base_channels * 2, base_channels * 4)
            self.down3 = DownBlock(base_channels * 4, base_channels * 8)
            self.down4 = DownBlock(base_channels * 8, (base_channels * 16) // factor)
            self.embedding_proj = nn.Sequential(
                nn.Conv2d((base_channels * 16) // factor, embedding_dim, kernel_size=1),
                nn.BatchNorm2d(embedding_dim),
                nn.GELU(),
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor (B, 14, 128, 128)
        Returns:
            Global spatial embedding vector (B, embedding_dim)
        """
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        dense = self.embedding_proj(x5)
        return F.adaptive_avg_pool2d(dense, (1, 1)).flatten(1)
