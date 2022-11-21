import os

CONVERTER_CMD = """
    PYTHONPATH="/opt/intel/openvino_2021.2.185/deployment_tools/model_optimizer/:$PYTHONPATH" python3.8 /opt/intel/openvino_2021.2.185/deployment_tools/model_optimizer/mo.py \
        --input_model {model_onnx_path} --model_name {model_name} --output_dir {result_path} \
        --input_shape {input_shape} --log_level INFO
    """


def export_dldt(model_name, model_onnx_path, result_path, input_shape):
    dldt_root = "/opt/intel/openvino_2021.2.185"  # os.environ.get("DLDT_ROOT")

    if dldt_root is None or not os.path.exists(dldt_root):
        raise ValueError("You should install DLDT and define valid DLDT_ROOT environment variable!")

    input_shape_str = "[" + ",".join(map(str, input_shape)) + "]"

    cmd = CONVERTER_CMD.format(model_name=model_name, model_onnx_path=model_onnx_path, result_path=result_path, input_shape=input_shape_str)

    print("Running DLDT converter: {}".format(cmd))
    os.system(cmd)
