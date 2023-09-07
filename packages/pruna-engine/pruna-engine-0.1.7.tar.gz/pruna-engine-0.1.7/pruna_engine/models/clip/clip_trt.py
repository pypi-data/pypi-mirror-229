import os
from typing import Dict, Optional
import pickle

try:
    import tensorrt as trt
    from tensorrt.tensorrt import Logger, Runtime

    from pruna_engine.models.clip.trt_utils import load_engine, build_engine, save_engine
except ImportError:
    raise ImportError(
        "It seems that TensorRT is not yet installed. "
        "It is required when you declare TensorRT backend."
        "Please find installation instruction on "
        "https://docs.nvidia.com/deeplearning/tensorrt/install-guide/index.html"
    )
from pruna_engine.models.clip.pretrained_models import (
    _OPENCLIP_MODELS,
    _MULTILINGUALCLIP_MODELS,
)
from pruna_engine.models.clip.clip_model import BaseCLIPModel
from pruna_engine.models.clip.clip_onnx import _MODELS as ONNX_MODELS

_MODELS = [
    'RN50::openai',
    'RN50::yfcc15m',
    'RN50::cc12m',
    'RN101::openai',
    'RN101::yfcc15m',
    'RN50x4::openai',
    'ViT-B-32::openai',
    'ViT-B-32::laion2b_e16',
    'ViT-B-32::laion400m_e31',
    'ViT-B-32::laion400m_e32',
    'ViT-B-16::openai',
    'ViT-B-16::laion400m_e31',
    'ViT-B-16::laion400m_e32',
    # older version name format
    'RN50',
    'RN101',
    'RN50x4',
    # 'RN50x16',
    # 'RN50x64',
    'ViT-B/32',
    'ViT-B/16',
    # 'ViT-L/14',
    # 'ViT-L/14@336px',
]


class CLIPTensorRTModel(BaseCLIPModel):
    def __init__(
            self,
            engine_path: str,
            name: str = "ViT-B-32::openai",
    ):
        super().__init__(name)

        self._textual_path = os.path.join(
            engine_path,
            f'textual.{ONNX_MODELS[name][0][1]}.fp16.trt',
        )
        self._visual_path = os.path.join(
            engine_path,
            f'visual.{ONNX_MODELS[name][1][1]}.fp16.trt',
        )

    @staticmethod
    def get_model_name(name: str):
        if name in _OPENCLIP_MODELS:
            from pruna_engine.models.clip.openclip_model import OpenCLIPModel

            return OpenCLIPModel.get_model_name(name)
        elif name in _MULTILINGUALCLIP_MODELS:
            from pruna_engine.models.clip.mclip_model import MultilingualCLIPModel

            return MultilingualCLIPModel.get_model_name(name)

        return name

    def start_engines(self):
        trt_logger: Logger = trt.Logger(trt.Logger.ERROR)
        runtime: Runtime = trt.Runtime(trt_logger)
        self._textual_engine = load_engine(runtime, self._textual_path)
        self._visual_engine = load_engine(runtime, self._visual_path)

    def __call__(self, image_input, text_input, *args, **kwargs):
        visual_output = self.encode_image(image_input)
        textual_output = self.encode_text(text_input)
        return visual_output, textual_output

    def encode_image(self, image_input: Dict):
        (visual_output,) = self._visual_engine(image_input)
        return visual_output

    def encode_text(self, text_input: Dict):
        (textual_output,) = self._textual_engine(text_input)
        return textual_output

    def save_model(self, filepath):
        """Saves the model to the specified file."""
        model_info = {
            "_textual_path": self._textual_path,
            "_visual_path": self._visual_path,
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_info, f)

    def load_model(self, filepath):
        """Loads the model from the specified file."""
        with open(filepath, 'rb') as f:
            model_info = pickle.load(f)

        self._textual_path = model_info["_textual_path"]
        self._visual_path = model_info["_visual_path"]

        # Start TensorRT engines
        self.start_engines()
