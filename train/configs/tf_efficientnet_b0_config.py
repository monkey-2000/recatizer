from dotenv import load_dotenv
import os

from train.configs.base_config import *


load_dotenv()
database_path = os.environ.get('CAT_INDIVIDUALS_DS_PATH', '/Users/alinatamkevich/dev/datasets/cats_dataset')
project_dir = os.environ.get('PROJECT_DIR', '/Users/alinatamkevich/dev/recatizer')


tf_efficientnet_b0_config = Config(
    name="tf_efficientnet_b0",
    image_size=(256,256),
    optimizer=OptimizerParams(epochs=100, lr=3e-4, wd=5e-4, eps=1e-8, type="Adam", schedule=LearningSchedule(type="exponential", params={"gamma": 0.98})),
    task_config=TaskConfig(model_name="tf_efficientnet_b0"),
    #save_folder="/Users/alinatamkevich/dev/models",
    save_folder = project_dir+"models",
    dataset_config=DatasetConfig(batch_size=16,
                                 base_path=database_path,
                                 train_path=project_dir+ "/data/processed/train.csv",
                                 val_path=project_dir +  "/data/processed/val.csv"),
    model_config=ModelConfig(model_name="tf_efficientnet_b0",
                             embedding_size=512, num_classes=509,
                             path_to_save=os.path.join(os.path.dirname(project_dir), "models"), resume_checkpoint="",
                             pool_config=PoolConfig(type="gem", params={"p":3, "p_trainable":False}),
                             head_config=HeadConfig(type="adaptive_arcface", params={"m": 0.2, "s": 20.0, "k": 3, "margin_coef_id": 0.27126,
                                                                                     "margin_power_id": -0.364399, "margin_cons_id": 0.05, "init": "uniform"}))
)