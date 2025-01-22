import os
import torch
import numpy as np
import comfy.utils
import folder_paths
from comfy_extras.chainner_models import model_loading
from comfy import model_management
from PIL import Image



class FocusUpscaleFN:
    @classmethod
    def INPUT_TYPES(cls):
        resampling_methods = ["lanczos", "nearest", "bilinear", "bicubic"]
        return {
            "required": {
                "image": ("IMAGE",),
                "upscale_model": (folder_paths.get_filename_list("upscale_models"),),
                "scale_factor": ("FLOAT", {"default": 2, "min": 0.01, "max": 16.0, "step": 0.25}),
                "resampling_method": (resampling_methods,),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGE",)
    FUNCTION = "focus_upscale"
    CATEGORY = "⚜️ Focus Nodes/Image/Upscaling"

    @staticmethod
    def pil2tensor(image: Image.Image) -> torch.Tensor:
        return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

    @staticmethod
    def tensor2pil(image: torch.Tensor) -> Image.Image:
        return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

    @staticmethod
    def load_model(upscale_model: str) -> torch.nn.Module:
        model_path = folder_paths.get_full_path("upscale_models", upscale_model)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Upscale model not found at {model_path}")
        sd = comfy.utils.load_torch_file(model_path, safe_load=True)
        if "module.layers.0.residual_group.blocks.0.norm1.weight" in sd:
            sd = comfy.utils.state_dict_prefix_replace(sd, {"module.": ""})
        return model_loading.load_state_dict(sd).eval()

    @staticmethod
    def upscale_with_model(upscale_model: torch.nn.Module, image: torch.Tensor) -> torch.Tensor:
        device = model_management.get_torch_device()
        upscale_model.to(device)
        in_img = image.movedim(-1, -3).to(device)

        tile = 512
        overlap = 64
        oom = True

        while oom:
            try:
                steps = comfy.utils.get_tiled_scale_steps(
                    in_img.shape[3], in_img.shape[2], tile_x=tile, tile_y=tile, overlap=overlap
                )
                pbar = comfy.utils.ProgressBar(steps)
                s = comfy.utils.tiled_scale(
                    in_img,
                    lambda a: upscale_model(a),
                    tile_x=tile,
                    tile_y=tile,
                    overlap=overlap,
                    upscale_amount=upscale_model.scale,
                    pbar=pbar,
                )
                oom = False
            except model_management.OOM_EXCEPTION as e:
                tile //= 2
                if tile < 128:
                    raise RuntimeError("Tile size is too small to proceed.")
        upscale_model.cpu()
        return torch.clamp(s.movedim(-3, -1), min=0, max=1.0)

    @staticmethod
    def apply_resize_image(
        image: Image.Image,
        original_width: int,
        original_height: int,
        rounding_modulus: int,
        mode: str = "scale",
        supersample: str = "true",
        factor: int = 2,
        width: int = 1024,
        resample: str = "bicubic",
    ) -> Image.Image:
        if mode == "rescale":
            new_width, new_height = int(original_width * factor), int(original_height * factor)
        else:
            m = rounding_modulus
            original_ratio = original_height / original_width
            height = int(width * original_ratio)
            new_width = width if width % m == 0 else width + (m - width % m)
            new_height = height if height % m == 0 else height + (m - height % m)

        resample_filters = {"nearest": 0, "bilinear": 2, "bicubic": 3, "lanczos": 1}

        if supersample == "true":
            image = image.resize(
                (new_width * 8, new_height * 8),
                resample=Image.Resampling(resample_filters[resample]),
            )

        resized_image = image.resize(
            (new_width, new_height),
            resample=Image.Resampling(resample_filters[resample]),
        )

        return resized_image

    def focus_upscale(
        self,
        image: torch.Tensor,
        upscale_model: str,
        mode: str = "rescale",
        resampling_method: str = "lanczos",
        scale_factor: float = 2,
    ) -> tuple:
        # Load upscale model
        loaded_model = self.load_model(upscale_model)

        # Perform upscaling
        scaled_image = self.upscale_with_model(loaded_model, image)

        # Convert tensor to PIL to determine dimensions
        original_width, original_height = self.tensor2pil(image).size
        upscaled_width, upscaled_height = self.tensor2pil(scaled_image).size

        # Return if no rescale is needed
        if upscaled_width == original_width and scale_factor == 1:
            return (scaled_image,)

        # Resize the upscaled image
        resized_image = self.apply_resize_image(
            self.tensor2pil(scaled_image),
            original_width,
            original_height,
            rounding_modulus=8,
            mode=mode,
            supersample="true",
            factor=scale_factor,
            width=1024,
            resample=resampling_method,
        )

        # Convert back to tensor and return
        return (self.pil2tensor(resized_image),)
    
NODE_CLASS_MAPPINGS = {
    "FOCUS Upscale (Focus Nodes)": FocusUpscaleFN,
}
