import os
from IPython.display import Markdown, display


def export_dldt(model_onnx_path, result_path, input_shape):

    input_shape_str = "[" + ",".join(map(str, input_shape)) + "]"
    mo_command = """mo
                     --input_model "{model_onnx_path}"
                     --input_shape "{input_shape}"
                     --data_type FP16
                     --output_dir "{result_path}"
                     """
    cmd = mo_command.format(
        model_onnx_path=model_onnx_path,
        result_path=result_path,
        input_shape=input_shape,
    )
    cmd = " ".join(cmd.split())
    print("Model Optimizer command to convert the ONNX model to OpenVINO:")
    display(Markdown(f"`{cmd}`"))

    print("Running DLDT converter: {}".format(cmd))
    os.system(cmd)
