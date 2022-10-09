from train.configs.base_config import *
resnet18_config = Config(
    name="resnet18",
    image_size=(128,128),
    optimizer=OptimizerParams(epochs=5, lr=3e-4, wd=5e-4, type="adam", schedule=LearningSchedule(type="exponential", params={"gamma": 0.98})),
    task_config=TaskConfig(model_name="resnet18d"),
    save_folder="",
    dataset_config=DatasetConfig(batch_size=64, train_path="", val_path=""))