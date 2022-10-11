from train.configs.base_config import *
tf_efficientnet_b0_config = Config(
    name="tf_efficientnet_b0",
    image_size=(128,128),
    optimizer=OptimizerParams(epochs=5, lr=3e-4, wd=5e-4, eps=1e-8, type="Adam", schedule=LearningSchedule(type="exponential", params={"gamma": 0.98})),
    task_config=TaskConfig(model_name="tf_efficientnet_b0"),
    save_folder="",
    dataset_config=DatasetConfig(batch_size=16, base_path="/Users/alinatamkevich/dev/datasets/cats_dataset", train_path="/Users/alinatamkevich/dev/recatizer/data/processed/cat_individual_database.csv", val_path="/Users/alinatamkevich/dev/recatizer/data/processed/cat_individual_database.csv"),
    model_config=ModelConfig(model_name="tf_efficientnet_b0",
                             embedding_size=512, num_classes=517,
                             path_to_save="/Users/alinatamkevich/dev/models", resume_checkpoint="",
                             pool_type="gem", p=3, p_trainable=False)
)