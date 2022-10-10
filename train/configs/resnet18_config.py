from train.configs.base_config import *
resnet18_config = Config(
    name="resnet18",
    image_size=(128,128),
    optimizer=OptimizerParams(epochs=5, lr=3e-4, wd=5e-4, type="adam", schedule=LearningSchedule(type="exponential", params={"gamma": 0.98})),
    task_config=TaskConfig(model_name="resnet18d"),
    save_folder="",
    dataset_config=DatasetConfig(batch_size=6, base_path="/Users/alinatamkevich/dev/datasets/cats_dataset", train_path="/Users/alinatamkevich/dev/recatizer/data/processed/cat_individual_database.csv", val_path="/Users/alinatamkevich/dev/recatizer/data/processed/cat_individual_database.csv"),
    model_config=ModelConfig(model_name="tf_efficientnet_b0", embedding_size=512, num_classes=516, path_to_save="/Users/alinatamkevich/dev/models")
)