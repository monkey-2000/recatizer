import torch.nn as nn
import torch

from train.model.gem_layer import GeM
from train.configs.base_config import ModelConfig
from train.model import backbone
from train.model.arc_face_head import ArcMarginProduct
from train.model.heads.arc_face import ArcAdaptiveMarginProduct
import numpy as np

class HappyWhaleModel(nn.Module):
    def __init__(self, config: ModelConfig, device: torch.device):

        super(HappyWhaleModel, self).__init__()
        # Retrieve pretrained weights
        self.backbone = backbone.load_backbone(config.model_name, pretrained=True)
        self.forward_features = self.build_forward_features(config)
        self.arcface = ArcMarginProduct(in_features=config.embedding_size,
                                        out_features=config.num_classes,
                                        s=30.0, m=0.50, easy_margin=False, ls_eps=0.0, device=device)

    def build_forward_features(self, config: ModelConfig):
        forward_features = nn.Sequential()
        if config.pool_type == "adaptive":
            forward_features.add_module("pool", nn.AdaptiveAvgPool2d((1, 1)))
            forward_features.add_module("flatten", nn.Flatten())
        elif config.pool_type == "gem":
            forward_features.add_module(
                "pool", GeM(p=config.p, p_trainable=config.p_trainable)
            )
            forward_features.add_module("flatten", nn.Flatten())
        embedding_size = self.backbone.out_features
        if config.embedding_size > 0:
            embedding_size = config.embedding_size
            forward_features.add_module(
                "linear",
                nn.Linear(self.backbone.out_features, embedding_size, bias=True),
            )
        forward_features.add_module("normalize", nn.BatchNorm1d(embedding_size))
        forward_features.add_module("relu", torch.nn.PReLU())
        return forward_features


    def forward(self, images, labels, is_train: bool = True):
        features = self.backbone(images)
        embedding = self.forward_features(features)
        if is_train != None:
            out = self.arcface(embedding, labels)
            return {"out": out, "embedding": embedding}
        else:
            return {"embedding": embedding}