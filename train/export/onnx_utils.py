import onnx
from onnx.helper import get_attribute_value

BASIC_FUSE_OPTIMIZATIONS = [
    "eliminate_identity",
    "fuse_consecutive_squeezes",
    "fuse_consecutive_transposes",
    "eliminate_nop_pad",
    "eliminate_nop_transpose",
    "eliminate_unused_initializer",
    "fuse_add_bias_into_conv",
    "fuse_bn_into_conv",
    "fuse_transpose_into_gemm",
]


def build_checker_context(ir_version=None, opset_version=None):
    import onnx.onnx_cpp2py_export.checker as C

    context = C.CheckerContext()
    context.ir_version = ir_version or onnx.IR_VERSION
    context.opset_imports = {"": opset_version or onnx.defs.onnx_opset_version()}

    return context


def get_attr_idx(op, name, with_value=True):
    for idx, attr in enumerate(op.attribute):
        if attr.name == name:
            if with_value:
                return idx, get_attribute_value(attr)
            else:
                return idx


def get_constant_node(model, node_id):
    for op_idx, op in enumerate(model.graph.node):
        if op.op_type == "Constant" and op.output[0] == node_id:
            return op_idx, op


def polish_model(model, optimize=False):
    """
    This function combines several useful utility functions together.
    """
    onnx.checker.check_model(model)
    onnx.helper.strip_doc_string(model)
    model = onnx.shape_inference.infer_shapes(model)
    if optimize:
        model = onnx.optimizer.optimize(model, BASIC_FUSE_OPTIMIZATIONS)
    onnx.checker.check_model(model)
    return model
