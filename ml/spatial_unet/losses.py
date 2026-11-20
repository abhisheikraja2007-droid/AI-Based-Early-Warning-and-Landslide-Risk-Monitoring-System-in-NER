"""
Loss Functions for Extreme Class Imbalance in Landslide Semantic Segmentation.
In the Landslide4Sense benchmark, positive landslide pixels account for <3% of all pixels.
Standard Binary Cross Entropy causes the network to collapse to predicting 'all background'.
This module provides Focal Loss, Soft Dice Loss, and Combined Focal+Dice Loss to force learning of rare landslide features.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    """
    Binary Focal Loss with numerically stable logit formulation:
        FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)
        
    Args:
        alpha: Weighting factor for positive class (landslide). Default: 0.75.
               Balances positive vs. negative pixel loss.
        gamma: Focusing parameter. Default: 2.0.
               Smoothly reduces the loss contribution from easy background examples
               and focuses gradients on hard landslide boundaries.
        reduction: 'mean', 'sum', or 'none'.
    """

    def __init__(self, alpha: float = 0.75, gamma: float = 2.0, reduction: str = "mean"):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Args:
            logits: Predicted raw logits of shape (B, 1, H, W) or (B, H, W).
            targets: Binary ground truth masks of same shape, values in {0, 1}.
        """
        # Ensure flat or matching shapes
        if logits.shape != targets.shape:
            targets = targets.view(logits.shape)

        # Standard binary cross entropy per pixel (unreduced)
        bce_loss = F.binary_cross_entropy_with_logits(logits, targets, reduction="none")

        # Probability of true class p_t
        p = torch.sigmoid(logits)
        p_t = p * targets + (1.0 - p) * (1.0 - targets)

        # Class weighting alpha_t
        alpha_t = self.alpha * targets + (1.0 - self.alpha) * (1.0 - targets)

        # Modulation factor (1 - p_t)^gamma
        modulating_factor = (1.0 - p_t).pow(self.gamma)

        # Focal loss
        focal_loss = alpha_t * modulating_factor * bce_loss

        if self.reduction == "mean":
            return focal_loss.mean()
        elif self.reduction == "sum":
            return focal_loss.sum()
        else:
            return focal_loss


class DiceLoss(nn.Module):
    """
    Soft Dice Loss for Binary Segmentation:
        DL = 1 - (2 * |P intersect Y| + smooth) / (|P| + |Y| + smooth)
        
    Directly optimizes the overlap / F1 score of the landslide mask.
    Because Dice Loss evaluates the global intersection, it is fundamentally invariant
    to the size of the negative background class, preventing the network from collapsing into all zeros.
    
    Args:
        smooth: Laplace smoothing term to prevent division by zero and stabilize training. Default: 1e-6.
        reduction: 'mean' across batch, or 'sum'.
    """

    def __init__(self, smooth: float = 1e-6, reduction: str = "mean"):
        super().__init__()
        self.smooth = smooth
        self.reduction = reduction

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Args:
            logits: Predicted raw logits of shape (B, 1, H, W) or (B, H, W).
            targets: Binary ground truth masks of same shape.
        """
        if logits.shape != targets.shape:
            targets = targets.view(logits.shape)

        # Convert logits to probabilities
        probs = torch.sigmoid(logits)

        # Flatten batch-wise per image: (B, -1)
        b = probs.shape[0]
        probs_flat = probs.view(b, -1)
        targets_flat = targets.view(b, -1)

        intersection = (probs_flat * targets_flat).sum(dim=1)
        cardinality = probs_flat.sum(dim=1) + targets_flat.sum(dim=1)

        dice_score = (2.0 * intersection + self.smooth) / (cardinality + self.smooth)
        dice_loss = 1.0 - dice_score

        if self.reduction == "mean":
            return dice_loss.mean()
        elif self.reduction == "sum":
            return dice_loss.sum()
        else:
            return dice_loss


class CombinedFocalDiceLoss(nn.Module):
    """
    Hybrid Loss combining Focal Loss and Soft Dice Loss:
        L_total = lambda_focal * L_focal + lambda_dice * L_dice
        
    - Focal Loss handles fine pixel-wise edge calibration and suppresses dominant background pixels.
    - Soft Dice Loss optimizes regional overlap and directly maximizes benchmark F1 / IoU metrics.
    Together they guarantee stable gradient flow even when landslide pixels constitute <1% of the patch.
    """

    def __init__(
        self,
        alpha: float = 0.75,
        gamma: float = 2.0,
        smooth: float = 1e-6,
        lambda_focal: float = 1.0,
        lambda_dice: float = 1.0,
    ):
        super().__init__()
        self.focal = FocalLoss(alpha=alpha, gamma=gamma, reduction="mean")
        self.dice = DiceLoss(smooth=smooth, reduction="mean")
        self.lambda_focal = lambda_focal
        self.lambda_dice = lambda_dice

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        loss_focal = self.focal(logits, targets)
        loss_dice = self.dice(logits, targets)
        return self.lambda_focal * loss_focal + self.lambda_dice * loss_dice
