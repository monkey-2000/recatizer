import json
import os
import tempfile
from argparse import ArgumentParser

import onnx
from onnx import shape_inference

from train.export.onnx_utils import polish_model


class ModelExporter:
    def __init__(self, rows_cols, channels, config_name, save_path=".", model_name="model", input_names=["x"]):
        self.rows, self.cols = json.loads(rows_cols)
        self.channels = int(channels)
        self.save_path = save_path
        self.model_name = model_name
        self.input_names = input_names
        self.model = None
        os.makedirs(save_path, exist_ok=True)
        self.outputs = []

    def load_onnx_model(self, model_path):
        self.model = onnx.load(model_path)

    def load_pytorch_model(self, model=None, weights_path=None, allow_random_weights=False, rename={}, verbose=True):
        import torch
        cpu_device = torch.device("cpu")

        try:
            if model is None:
                model = torch.load(weights_path, map_location=str(cpu_device))
            else:
                model_weights = torch.load(weights_path, map_location=str(cpu_device))["state_dict"]
                model_weights = {k: v for k, v in model_weights.items() if k in model.state_dict()}
                print("loaded weights: ", weights_path)
                model.load_state_dict(model_weights, strict=True)
        except (FileNotFoundError, AttributeError) as e:
            if not allow_random_weights:
                raise FileNotFoundError("Weights not found: " + str(e))

        # To be sure that model and weights on CPU
        model = model.to(cpu_device)
        model.eval()

        dummy_input = torch.randn(1, self.channels, self.rows, self.cols).cpu()

        with tempfile.NamedTemporaryFile() as tfh:
            torch.onnx.export(
                model,
                dummy_input,
                tfh,
                verbose=verbose,
                input_names=self.input_names,
                opset_version=9,
                keep_initializers_as_inputs=True,
            )
            model_new = onnx.load(tfh.name)
            self.model = polish_model(model_new)


    def save_onnx(self, opset_version=None):
        output_path = os.path.join(self.save_path, self.model_name + ".onnx")
        model = self.model
        model_with_shape = shape_inference.infer_shapes(model)
        onnx.save_model(model_with_shape, output_path)


    def build_trained_model(self):
        #load Model
        return model


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--task", type=str, help="Name of the task that will be run.", required=True)
    argparser.add_argument("--to", type=str, choices=("onnx", "dldt"), required=True)
    argparser.add_argument("--random_weights", type=str, required=False, default="0")
    argparser.add_argument("--config_name", type=str, required=False)
    argparser.add_argument("--save_path", type=str, help="Path to save", required=True)
    argparser.add_argument("--model_weights", type=str, help="model weights path", required=True)
    argparser.add_argument("--model_name", help="model name", required=True)

    argparser.add_argument("--rows_cols", type=str, required=True)
    argparser.add_argument("--channels", type=str, default=3)
    args = argparser.parse_args()

    exporter = ModelExporter(args.rows_cols, args.channels, args.config_name, save_path=args.save_path, model_name=args.model_name)
    model = exporter.build_trained_model()
    if args.to == "onnx":
        exporter.load_pytorch_model(model=model, weights_path=args.model_weights, allow_random_weights=args.random_weights)
        exporter.save_onnx()
    elif args.to == "dldt":
        exporter.load_onnx_model(args.model_weights)
        #to do dldt
