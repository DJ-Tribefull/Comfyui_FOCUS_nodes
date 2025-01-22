import os
import torch
import math
import comfy.model_management
import comfy.sd
from comfy.cli_args import args

class SDXLPreprocessFN:
    def __init__(self):
        self.device = comfy.model_management.intermediate_device()
        
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "resolution": (["704x1408 (0.5)","704x1344 (0.52)","768x1344 (0.57)","768x1280 (0.6)","832x1216 (0.68)","832x1152 (0.72)","896x1152 (0.78)","896x1088 (0.82)","960x1088 (0.88)","960x1024 (0.94)","1024x1024 (1.0)","1024x960 (1.07)","1088x960 (1.13)","1088x896 (1.21)","1152x896 (1.29)","1152x832 (1.38)","1216x832 (1.46)","1280x768 (1.67)","1344x768 (1.75)","1344x704 (1.91)","1408x704 (2.0)","1472x704 (2.09)","1536x640 (2.4)","1600x640 (2.5)","1664x576 (2.89)","1728x576 (3.0)",], {"default": "832x1216 (0.68)"}),
            "upscale_factor": ("INT", {"default": 2, "min": 1, "max": 8}),
            "positive_in": ("STRING", {"multiline": True, "default": "", "dynamicPrompts": True, "defaultInput": True,}),
            "negative_in": ("STRING", {"multiline": True, "default": "", "dynamicPrompts": True, "defaultInput": True,}),
            "clip": ("CLIP", ),
            "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096}),
            }}

    RETURN_TYPES = ("CONDITIONING","CONDITIONING","LATENT",)
    RETURN_NAMES = ("positive", "negative","LATENT",)
    FUNCTION = "execute"
    CATEGORY = "⚜️ Focus Nodes/Conditioning"

    def execute(self, clip, resolution, batch_size, upscale_factor, positive_in, negative_in):
        crop_w = 0
        crop_h = 0
        res_wide, res_tall  = map(int, resolution.split(" ")[0].split("x"))
        width = int(res_wide)
        height = int(res_tall)
        target_width = int(width*upscale_factor)
        target_height = int(height*upscale_factor)
        text_g_pos = text_l_pos = positive_in
        text_g_neg = text_l_neg = negative_in
        
        latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)

        tokens_pos = clip.tokenize(text_g_pos)
        tokens_pos["l"] = clip.tokenize(text_l_pos)["l"]
        if len(tokens_pos["l"]) != len(tokens_pos["g"]):
            empty_pos = clip.tokenize("")
            while len(tokens_pos["l"]) < len(tokens_pos["g"]):
                tokens_pos["l"] += empty_pos["l"]
            while len(tokens_pos["l"]) > len(tokens_pos["g"]):
                tokens_pos["g"] += empty_pos["g"]
        cond_pos, pooled_pos = clip.encode_from_tokens(tokens_pos, return_pooled=True)

        tokens_neg = clip.tokenize(text_g_neg)
        tokens_neg["l"] = clip.tokenize(text_l_neg)["l"]
        if len(tokens_neg["l"]) != len(tokens_neg["g"]):
            empty_neg = clip.tokenize("")
            while len(tokens_neg["l"]) < len(tokens_neg["g"]):
                tokens_neg["l"] += empty_neg["l"]
            while len(tokens_pos["l"]) > len(tokens_pos["g"]):
                tokens_neg["g"] += empty_neg["g"]
        cond_neg, pooled_neg = clip.encode_from_tokens(tokens_neg, return_pooled=True)

        return (
            [[cond_pos, {
                "pooled_output": pooled_pos,
                "width": width,
                "height": height,
                "crop_w": crop_w,
                "crop_h": crop_h,
                "target_width": target_width,
                "target_height": target_height
            }]],
            [[cond_neg, {
                "pooled_output": pooled_neg,
                "width": width,
                "height": height,
                "crop_w": crop_w,
                "crop_h": crop_h,
                "target_width": target_width,
                "target_height": target_height
            }]],
            {"samples":latent},
        )
        
NODE_CLASS_MAPPINGS = {
    "SDXL Preprocess (Focus Nodes)": SDXLPreprocessFN,
}