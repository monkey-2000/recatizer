from train.configs.base_config import *
tf_efficientnet_b0_config_gc = Config(
    name="tf_efficientnet_b0_gc",
    image_size=(128,128),
    optimizer=OptimizerParams(epochs=5, lr=3e-4, wd=5e-4, eps=1e-8, type="Adam", schedule=LearningSchedule(type="exponential", params={"gamma": 0.98})),
    task_config=TaskConfig(model_name="tf_efficientnet_b0"),
    save_folder="",
    dataset_config=DatasetConfig(batch_size=16, base_path="/content/gdrive/MyDrive/cats_dataset", train_path="/content/gdrive/MyDrive/recatizer/data/processed/cat_individual_database.csv", val_path="/content/gdrive/MyDrive/recatizer/data/processed/cat_individual_database.csv"),
    model_config=ModelConfig(model_name="tf_efficientnet_b0",
                             embedding_size=512, num_classes=509,
                             path_to_save="/content/gdrive/MyDrive/dev/models", resume_checkpoint="",
                             pool_config=PoolConfig(type="gem", params={"p":3, "p_trainable":False}),
                             head_config=HeadConfig(type="adaptive_arcface", params={"m": 0.2, "s": 20.0, "k": 3, "margin_coef_id": 0.27126,
                                                                                     "margin_power_id": -0.364399, "margin_cons_id": 0.05, "init": "uniform"}))
)