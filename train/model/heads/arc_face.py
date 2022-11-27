import math

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import Parameter
from torch import Tensor


class ArcMarginProduct(nn.Module):
    r"""Implement of large margin arc distance: :
    Args:
        in_features: size of each input sample
        out_features: size of each output sample
        s: norm of input feature
        m: margin
        cos(theta + m)
    """

    def __init__(
        self,
        in_features,
        out_features,
        s=30.0,
        m=0.30,
        easy_margin=False,
        use_penalty=True,
        initialization="xavier",
        device: torch.device = torch.device("cuda"),
    ):
        super(ArcMarginProduct, self).__init__()
        self.device = device
        self.in_features = in_features
        self.out_features = out_features
        self.s = s
        self.m = m
        self.weight = Parameter(torch.FloatTensor(out_features, in_features))
        if initialization == "xavier":
            nn.init.xavier_uniform_(self.weight)
        elif initialization == "uniform":
            stdv = 1.0 / math.sqrt(self.weight.size(1))
            self.weight.data.uniform_(-stdv, stdv)
        else:
            assert 0 == 1

        self.easy_margin = easy_margin
        self.cos_m = math.cos(m)
        self.sin_m = math.sin(m)
        self.th = math.cos(math.pi - m)
        self.mm = math.sin(math.pi - m) * m
        self.use_penalty = use_penalty

    def forward(self, input, label=None):
        # --------------------------- cos(theta) & phi(theta) ---------------------------
        if label is None:
            assert not self.use_penalty
        cosine = F.linear(F.normalize(input), F.normalize(self.weight))
        if not self.use_penalty:
            return self.s * cosine
        sine = torch.sqrt((1.0 - torch.pow(cosine, 2)).clamp(0, 1))
        phi = cosine * self.cos_m - sine * self.sin_m
        if self.easy_margin:
            phi = torch.where(cosine > 0, phi, cosine)
        else:
            phi = torch.where(cosine.float() > self.th, phi, cosine.float() - self.mm)
        # --------------------------- convert label to one-hot ---------------------------
        # one_hot = torch.zeros(cosine.size(), requires_grad=True, device='cuda')
        one_hot = torch.zeros(cosine.size(), device=self.device)
        one_hot.scatter_(1, label.view(-1, 1).long(), 1)
        # -------------torch.where(out_i = {x_i if condition_i else y_i) -------------
        output = (one_hot * phi) + (
            (1.0 - one_hot) * cosine
        )  # you can use torch.where if your torch.__version__ is 0.4
        output *= self.s

        return output, cosine


class ArcAdaptiveMarginProduct(nn.Module):
    def __init__(
        self,
        in_features,
        out_features,
        margins,
        s=30.0,
        k=1,
        initialization="xavier",
        device: torch.device = torch.device("cuda"),
    ):
        super(ArcAdaptiveMarginProduct, self).__init__()
        self.in_features = in_features
        self.device = device
        self.out_features = out_features
        self.s = s
        self.margins = margins
        self.k = k
        self.weight = Parameter(torch.FloatTensor(out_features * k, in_features))
        if initialization == "xavier":
            nn.init.xavier_uniform_(self.weight)
        elif initialization == "uniform":
            stdv = 1.0 / math.sqrt(self.weight.size(1))
            self.weight.data.uniform_(-stdv, stdv)
        else:
            assert 0 == 1

    def forward(self, input: Tensor, labels: Tensor):
        # subcenter
        cosine_all = F.linear(F.normalize(input), F.normalize(self.weight))
        cosine_all = cosine_all.view(-1, self.out_features, self.k)
        cosine, _ = torch.max(cosine_all, dim=2)
        sine = torch.sqrt(1.0 - torch.pow(cosine, 2))

        ms = self.margins[labels.clone().cpu().numpy()]
        cos_m = torch.from_numpy(np.cos(ms)).float().to(self.device)
        sin_m = torch.from_numpy(np.sin(ms)).float().to(self.device)
        th = torch.from_numpy(np.cos(math.pi - ms)).float().to(self.device)
        mm = torch.from_numpy(np.sin(math.pi - ms) * ms).float().to(self.device)

        labels = F.one_hot(labels, self.out_features).float()

        phi = cosine * cos_m.view(-1, 1) - sine * sin_m.view(-1, 1)
        phi = torch.where(cosine > th.view(-1, 1), phi, cosine - mm.view(-1, 1))
        output = (labels * phi) + ((1.0 - labels) * cosine)
        output *= self.s

        return output, cosine
