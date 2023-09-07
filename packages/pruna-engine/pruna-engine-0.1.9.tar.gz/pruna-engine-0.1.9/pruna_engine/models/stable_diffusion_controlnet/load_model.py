import numpy as np
from .txt2img_pipeline import Txt2ImgPipeline
import random
import torch

from dataclasses import dataclass, field
from typing import List


@dataclass
class StableDiffusionConfig:
    version: str = "1.5"
    prompt: List[str] = field(default_factory=lambda: ['yellow,a bird, best quality, extremely detailed'])
    negative_prompt: List[str] = field(default_factory=lambda: ['blurry, poor quality, painting, worst quality, lowres, low quality'])
    repeat_prompt: int = 1
    height: int = 512
    width: int = 512
    denoising_steps: int = 20
    onnx_opset: int = 17
    onnx_dir: str = 'onnx'
    onnx_refit_dir: str = ''
    force_onnx_export: bool = False
    force_onnx_optimize: bool = False
    engine_dir: str = 'engine'
    force_engine_build: bool = False
    build_static_batch: bool = True
    build_dynamic_shape: bool = False
    build_enable_refit: bool = False
    build_preview_features: bool = False
    build_all_tactics: bool = False
    timing_cache: str = None
    num_warmup_runs: int = 5
    nvtx_profile: bool = False
    seed: int = None
    output_dir: str = 'output'
    hf_token: str = None
    verbose: bool = False
    scheduler: str = "DDIM"


def parseArgs():
    return StableDiffusionConfig()


def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)

def load_sd_controlnet_model(engine_dir, onnx_dir='onnx', max_batch_size=1):
    setup_seed(1000)
    args = parseArgs()

    # Assert tensorrt version
    import tensorrt as trt

    assert trt.__version__ == '8.6.0', f'Unexpected TensorRT version. Expected 8.6.0, but got {trt.__version__}'

    # Initialize demo
    demo = Txt2ImgPipeline(
        scheduler=args.scheduler,
        denoising_steps=args.denoising_steps,
        output_dir=args.output_dir,
        version=args.version,
        hf_token=args.hf_token,
        verbose=args.verbose,
        nvtx_profile=args.nvtx_profile,
        max_batch_size=max_batch_size)

    # Load TensorRT engines and pytorch modules
    demo.loadEngines(engine_dir, onnx_dir, args.onnx_opset,
        opt_batch_size=1, opt_image_height=args.height, opt_image_width=args.width, \
        force_export=args.force_onnx_export, force_optimize=args.force_onnx_optimize, \
        force_build=args.force_engine_build, \
        static_batch=args.build_static_batch, static_shape=not args.build_dynamic_shape, \
        enable_refit=args.build_enable_refit, enable_preview=args.build_preview_features, enable_all_tactics=args.build_all_tactics, \
        timing_cache=args.timing_cache, onnx_refit_dir=args.onnx_refit_dir)

    demo.loadResources(args.height, args.width, 1, args.seed)

    return demo