import torch.nn as nn
import timm
from gem_layer import GeM

class HappyWhaleModel(nn.Module):
    def __init__(self, modelName, numClasses, noNeurons, embeddingSize):

        super(HappyWhaleModel, self).__init__()
        # Retrieve pretrained weights
        self.backbone = timm.create_model(modelName, pretrained=True)
        # Save the number features from the backbone
        ### different models have different numbers e.g. EffnetB3 has 1536
        backbone_features = self.backbone.classifier.in_features
        self.backbone.classifier = nn.Identity()  # ?????
        self.backbone.global_pool = nn.Identity()  # ?????
        self.gem = GeM()
        # Embedding layer (what we actually need)
        self.embedding = nn.Sequential(nn.Linear(backbone_features, noNeurons),
                                       nn.BatchNorm1d(noNeurons),
                                       nn.ReLU(),
                                       nn.Dropout(p=0.2),

                                       nn.Linear(noNeurons, embeddingSize),
                                       nn.BatchNorm1d(embeddingSize),
                                       nn.ReLU(),
                                       nn.Dropout(p=0.2))
        self.arcface = ArcMarginProduct(in_features=embeddingSize,
                                        out_features=numClasses,
                                        s=30.0, m=0.50, easy_margin=False, ls_eps=0.0)

    def forward(self, image, is_train: bool = True):

        features = self.backbone(image)
        # flatten transforms from e.g.: [3, 1536, 1, 1] to [3, 1536]
        gem_pool = self.gem(features).flatten(1)
        embedding = self.embedding(gem_pool)
        if is_train != None:
            out = self.arcface(embedding, is_train)
            return out, embedding
        else:
            return embedding