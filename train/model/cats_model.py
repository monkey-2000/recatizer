import torch.nn as nn
import torch

from train.model.gem_layer import GeM
from train.configs.base_config import ModelConfig
from train.model import backbone
from train.model.arc_face_head import ArcMarginProduct
from train.model.heads.arc_face import ArcAdaptiveMarginProduct
import numpy as np

class HappyWhaleModel(nn.Module):
    def __init__(self, config: ModelConfig, device: torch.device, id_class_nums: np.ndarray):

        super(HappyWhaleModel, self).__init__()
        # Retrieve pretrained weights
        self.id_class_nums = id_class_nums
        self.device = device
        self.backbone = backbone.load_backbone(config.model_name, pretrained=True)
        self.forward_features, embedding_size = self.build_forward_features(config)
        self.arcface = self.build_head(config, embedding_size)
        # ArcMarginProduct(in_features=config.embedding_size,
        #                                 out_features=config.num_classes,
        #                                 s=30.0, m=0.50, easy_margin=False, ls_eps=0.0, device=device)

    def build_forward_features(self, config: ModelConfig):
        forward_features = nn.Sequential()
        if config.pool_config.type == "adaptive":
            forward_features.add_module("pool", nn.AdaptiveAvgPool2d((1, 1)))
            forward_features.add_module("flatten", nn.Flatten())
        elif config.pool_config.type == "gem":
            forward_features.add_module(
                "pool", GeM(p=config.pool_config.params["p"], p_trainable=config.pool_config.params["p_trainable"])
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
        return forward_features, embedding_size

    def build_head(self, config: ModelConfig, embedding_size: int):
        margins = (
                np.power(self.id_class_nums, config.head_config.params["margin_power_id"]) * config.head_config.params["margin_coef_id"]
                + config.head_config.params["margin_cons_id"]
        )

        if margins.shape[0] * 2 == config.num_classes:
            margins = np.hstack([margins, margins])

        head = ArcAdaptiveMarginProduct(
            embedding_size,
            config.num_classes,
            margins=margins,
            s=config.head_config.params["s"],
            k=config.head_config.params["k"],
            initialization=config.head_config.params["init"],
            device=self.device
        )
        return head
    def forward(self, images, labels, is_train: bool = True):
        features = self.backbone(images)
        embedding = self.forward_features(features)
        if is_train != None:
            logits_margin, logits = self.arcface(embedding, labels)
            return {"logits_margin": logits_margin, "logits": logits, "embedding": embedding}
        else:
            return {"embedding": embedding}