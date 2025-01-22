import torch
from .sdxl_preprocess_FN import SDXLPreprocessFN
from .style_injector_FN import StyleInjectorFN
from .wildcard_processor_FN import WildcardProcessorFN

class SDXLAllInOneFN:
    def __init__(self):
        self.preprocessor = SDXLPreprocessFN()
        self.style_injector = StyleInjectorFN()
        self.wildcard_processor = WildcardProcessorFN()

    @classmethod
    def INPUT_TYPES(cls):
        # Fetch wildcard inputs and remove 'prompt_input'
        wildcard_inputs = WildcardProcessorFN.INPUT_TYPES()["required"]
        if "prompt_input" in wildcard_inputs:
            del wildcard_inputs["prompt_input"]

        return {
            "required": {              
                "resolution": ([
                    "704x1408 (0.5)", "704x1344 (0.52)", "768x1344 (0.57)", "768x1280 (0.6)",
                    "832x1216 (0.68)", "832x1152 (0.72)", "896x1152 (0.78)", "896x1088 (0.82)",
                    "960x1088 (0.88)", "960x1024 (0.94)", "1024x1024 (1.0)", "1024x960 (1.07)",
                    "1088x960 (1.13)", "1088x896 (1.21)", "1152x896 (1.29)", "1152x832 (1.38)",
                    "1216x832 (1.46)", "1280x768 (1.67)", "1344x768 (1.75)", "1344x704 (1.91)",
                    "1408x704 (2.0)", "1472x704 (2.09)", "1536x640 (2.4)", "1600x640 (2.5)",
                    "1664x576 (2.89)", "1728x576 (3.0)"
                ], {"default": "832x1216 (0.68)"}),
                "upscale_factor": ("INT", {"default": 2, "min": 1, "max": 8}),
                "positive_in": ("STRING", {"multiline": True, "default": "", "dynamicPrompts": True, "defaultInput": True}),
                "negative_in": ("STRING", {"multiline": True, "default": "", "dynamicPrompts": True, "defaultInput": True}),
                "clip": ("CLIP",),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096}),
                "style": ("DICTIONARY",),
                **wildcard_inputs,
            }
        }

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", "LATENT", "STRING", "STRING")
    RETURN_NAMES = ("positive", "negative", "LATENT", "+ prompt", "- prompt")
    FUNCTION = "execute"
    CATEGORY = "⚜️ Focus Nodes/Conditioning"

    def execute(self, resolution, upscale_factor, positive_in, negative_in, clip, batch_size, style=None, **wildcard_inputs):
        # Validate 'style' input
        if style is None or not isinstance(style, dict):
            style = {}

        # Step 1: Process the positive_in using WildcardProcessorFN
        processed_positive = self.wildcard_processor.process(
            prompt_input=positive_in,
            **wildcard_inputs
        )[0]  # Extract the processed string

        # Initialize styled prompts
        styled_positive = processed_positive
        styled_negative = negative_in

        # Apply styles from the style dictionary
        for category, selected_style in style.items():
            if category in self.style_injector.styles_by_category:
                temp_positive, temp_negative = self.style_injector.execute(
                    positive_in=styled_positive,
                    negative_in=styled_negative,
                    **{category: selected_style}
                )
                styled_positive = temp_positive
                styled_negative = temp_negative

        # Step 3: Pass styled prompts to SDXLPreprocessFN
        conditioning_positive, conditioning_negative, latent = self.preprocessor.execute(
            clip=clip,
            resolution=resolution,
            batch_size=batch_size,
            upscale_factor=upscale_factor,
            positive_in=styled_positive,
            negative_in=styled_negative
        )

        return conditioning_positive, conditioning_negative, latent, styled_positive, styled_negative

NODE_CLASS_MAPPINGS = {
    "SDXL All-In-One (Focus Nodes)": SDXLAllInOneFN,
}