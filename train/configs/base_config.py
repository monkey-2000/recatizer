from dataclasses import dataclass, field
from typing import Dict


@dataclass
class LearningSchedule:
    type: str
    params: Dict[str, float]


@dataclass
class OptimizerParams:
    type: str
    epochs: int
    lr: float
    wd: float
    eps: float
    schedule: LearningSchedule

@dataclass
class TaskConfig:
    model_name: str

@dataclass
class DatasetConfig:
    batch_size: int
    train_path: str
    base_path: str
    val_path: str

@dataclass
class HeadConfig:
    type: str
    params: Dict[str, float]
@dataclass
class PoolConfig:
    type: str
    params: Dict[str, float]


@dataclass
class ModelConfig:
    embedding_size: int
    model_name: str
    num_classes: int
    path_to_save: str
    resume_checkpoint: str
    head_config: HeadConfig
    pool_config: PoolConfig


@dataclass
class Config:
    name: str
    save_folder: str
    image_size: (int, int)
    optimizer: OptimizerParams
    task_config: TaskConfig
    dataset_config: DatasetConfig
    model_config: ModelConfig
