import torch.nn as nn
import timm
import torch

from train.model.gem_layer import GeM
from train.configs.base_config import ModelConfig
from train.model import backbone
from train.model.arc_face_head import ArcMarginProduct


class HappyWhaleModel(nn.Module):
    def __init__(self, config: ModelConfig, device: torch.device):

        super(HappyWhaleModel, self).__init__()
        # Retrieve pretrained weights
        self.backbone = backbone.load_backbone(config.model_name, pretrained=True)
        # Save the number features from the backbone
        ### different models have different numbers e.g. EffnetB3 has 1536
        backbone_features = self.backbone.out_features
        self.backbone.classifier = nn.Identity()  # ?????
        self.backbone.global_pool = nn.Identity()  # ?????
        self.gem = GeM()
        # Embedding layer (what we actually need)
        self.embedding = nn.Linear(backbone_features,config.embedding_size)

        self.arcface = ArcMarginProduct(in_features=config.embedding_size,
                                        out_features=config.num_classes,
                                        s=30.0, m=0.50, easy_margin=False, ls_eps=0.0, device=device)

    def forward(self, images, labels, is_train: bool = True):
        features = self.backbone(images)
        gem_pool = self.gem(features).flatten(1)
        embedding = self.embedding(gem_pool)
        if is_train != None:
            out = self.arcface(embedding, labels)
            return {"out": out, "embedding": embedding}
        else:
            return {"embedding": embedding}