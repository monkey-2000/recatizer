import json
import os
import tempfile
from argparse import ArgumentParser

import onnx
import torch
from onnx import shape_inference

from train.export.export_dldt import export_dldt
from train.export.model_builder import ModelBuilder
from train.export.onnx_utils import polish_model
from train.model.cats_model import HappyWhaleModel


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

        # try:
        #     if model is None:
        #         model = torch.load(weights_path, map_location=str(cpu_device))
        #     else:
        #         model_weights = torch.load(weights_path, map_location=str(cpu_device))["state_dict"]
        #         model_weights = {k: v for k, v in model_weights.items() if k in model.state_dict()}
        #         print("loaded weights: ", weights_path)
        #         model.load_state_dict(model_weights, strict=True)
        # except (FileNotFoundError, AttributeError) as e:
        #     if not allow_random_weights:
        #         raise FileNotFoundError("Weights not found: " + str(e))

        # To be sure that model and weights on CPU
        model = model.to(cpu_device)
        model.eval()

        dummy_input = torch.unsqueeze(torch.randn(1, self.channels, self.rows, self.cols).cpu(), dim=0)

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
        return model_with_shape, output_path


    def export_dldt(self, onnx_model_path: str):
        input_shape = [1, 1, self.channels, self.rows, self.cols]
        export_dldt(onnx_model_path, self.save_path, input_shape=input_shape)


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--to", type=str, choices=("onnx", "dldt"), default="onnx")
    argparser.add_argument("--random_weights", type=str, required=False, default="0")
    argparser.add_argument("--config_name", type=str, default="tf_efficientnet_b0")
    argparser.add_argument("--save_path", type=str, help="Path to save", default="/Users/alinatamkevich/dev/models")
    argparser.add_argument("--model_weights", type=str, help="model weights path", default="/Users/alinatamkevich/dev/models/tf_efficientnet_b0_last")
    argparser.add_argument("--model_name", help="model name", default="classificator")

    argparser.add_argument("--rows_cols", type=str, default="[128, 128]")
    argparser.add_argument("--channels", type=str, default=3)
    args = argparser.parse_args()

    exporter = ModelExporter(args.rows_cols, args.channels, args.config_name, save_path=args.save_path, model_name=args.model_name)
    model = ModelBuilder(args.config_name, args.model_name).build_trained_model()
    exporter.load_pytorch_model(model=model, weights_path=args.model_weights, allow_random_weights=args.random_weights)

    #onnx
    model_with_shape, onnx_output_path = exporter.save_onnx()

    #openvino
    exporter.export_dldt(onnx_output_path)
