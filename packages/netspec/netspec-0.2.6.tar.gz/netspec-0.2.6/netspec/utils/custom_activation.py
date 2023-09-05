from typing import Optional
import torch.nn as nn
import torch.functional as F
import torch


class Slimy(nn.Module):
    def __init__(self):
        super().__init__()

        self.alpha = nn.Parameter(torch.ones(1))

        self.beta = nn.Parameter(torch.ones(1))

    def forward(self, x):

        return torch.multiply(
            torch.add(
                self.beta,
                torch.multiply(
                    torch.sigmoid(torch.multiply(self.alpha, x)),
                    (1.0 - self.beta),
                ),
            ),
            x,
        )
