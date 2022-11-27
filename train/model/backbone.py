import timm
from timm.models.efficientnet import EfficientNet
from timm.models.resnet import ResNet

from .backbones.base import BackboneBase
from .backbones.efficientnet import EfficientNetBackbone
from .backbones.resnet import ResNetBackbone


def load_backbone(
    base_model: str,
    pretrained: bool,
    in_chans: int = 3,
) -> BackboneBase:
    """Load backbone model given a base model architecture type.
    Args:
        base_model: Base model architecture type.
        pretrained: Load pretrained weights if True.
    Returns:
        The backbone model wrapped with BackboneBase.
    """

    model = timm.create_model(base_model, pretrained=pretrained, in_chans=in_chans)

    # Determine which BackboneBase class to use
    if isinstance(model, ResNet):
        backbone = ResNetBackbone(model)
    elif isinstance(model, EfficientNet):
        backbone = EfficientNetBackbone(model)
    else:
        raise RuntimeError("Unable to determine backbone type")

    return backbone
