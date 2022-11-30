from train.configs.base_config import Config
from train.configs.tf_efficientnet_b0_config import tf_efficientnet_b0_config
from train.configs.tf_efficientnet_b0_config_gc import tf_efficientnet_b0_config_gc
from train.configs.tf_efficientnet_b0_config_kaggle import tf_efficientnet_b0_kaggle

mapping = {tf_efficientnet_b0_config.name: tf_efficientnet_b0_config,
           tf_efficientnet_b0_config_gc.name: tf_efficientnet_b0_config_gc,
           tf_efficientnet_b0_kaggle.name: tf_efficientnet_b0_kaggle}
def load(congig_name: str) -> Config:
    return mapping.get(congig_name)
