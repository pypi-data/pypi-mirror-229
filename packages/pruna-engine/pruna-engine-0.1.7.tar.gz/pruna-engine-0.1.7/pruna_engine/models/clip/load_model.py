from pruna_engine.models.clip.clip_trt import CLIPTensorRTModel
from pruna_engine.models.clip.tokenization import Tokenizer

device = 'cuda'

def load_clip(engine_path):
    from packaging import version
    import tensorrt as trt

    assert version.parse(trt.__version__) < version.parse(
        "8.6.0"), f'TensorRT version should be less than 8.6.0, but got {trt.__version__}'

    model = CLIPTensorRTModel(engine_path=engine_path)
    model.start_engines()
    return model

def load_tokenizer():
    return Tokenizer()