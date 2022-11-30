from train.configs.base_config import *
tf_efficientnet_b0_kaggle = Config(
    name="tf_efficientnet_b0_kaggle",
    image_size=(512,512),
    optimizer=OptimizerParams(epochs=100, lr=3e-4, wd=5e-4, eps=1e-8, type="Adam", schedule=LearningSchedule(type="exponential", params={"gamma": 0.98})),
    task_config=TaskConfig(model_name="tf_efficientnet_b0"),
    save_folder="/kaggle/working",
    dataset_config=DatasetConfig(batch_size=16, base_path="/kaggle/input/cats-dataset/cats_dataset", train_path="/kaggle/working/recatizer/data/processed/cat_individual_database.csv", val_path="/kaggle/working/recatizer/data/processed/cat_individual_database.csv"),
    model_config=ModelConfig(model_name="tf_efficientnet_b0",
                             embedding_size=512, num_classes=509,
                             path_to_save="/kaggle/working/models", resume_checkpoint="",
                             pool_config=PoolConfig(type="gem", params={"p":3, "p_trainable":False}),
                             head_config=HeadConfig(type="adaptive_arcface", params={"m": 0.2, "s": 20.0, "k": 3, "margin_coef_id": 0.27126,
                                                                                     "margin_power_id": -0.364399, "margin_cons_id": 0.05, "init": "uniform"}))
)