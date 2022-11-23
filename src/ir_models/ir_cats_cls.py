from openvino.runtime import Core

class CatIrClassificator:
    def __init__(self, ir_path: str):
        ie = Core()
        model_ir = ie.read_model(model=ir_path)
        self.model = ie.compile_model(model=model_ir, device_name="CPU")
        self.outputs = self.model.output(0)

    def predict(self, input_image):
        res_ir = self.model([input_image])[self.outputs]
        return res_ir
