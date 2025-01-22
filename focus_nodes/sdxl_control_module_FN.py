from ctypes.wintypes import BOOLEAN
from .style_injector_FN import StyleInjectorFN

class SDXLControlModuleFN:

    @classmethod
    def INPUT_TYPES(cls):
        # Dynamically fetch styles from StyleInjectorFN
        StyleInjectorFN.refresh_styles()
        dynamic_styles = {
            category: (list(styles.keys()), {"default": ""})
            for category, styles in StyleInjectorFN.styles_by_category.items()
        }

        return {
            "required": {              
                "Total_Steps": ("INT", {"default": 30, "min": 0, "max": 100}),
                "Stage_1_End_Step": ("INT", {"default": 20, "min": 1, "max": 100}),
                "Stage_2_Start_Step": ("INT", {"default": 21, "min": 1, "max": 100}),
                "Stage_1_CFG": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 100.0}),
                "Stage_2_CFG": ("FLOAT", {"default": 7.5, "min": 0.0, "max": 100.0}),
                **dynamic_styles,
                "Freeze_Wildcards": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("DICTIONARY",)
    RETURN_NAMES = ("Control Pipe",)
    FUNCTION = "doit"
    CATEGORY = "⚜️ Focus Nodes/Utility"

    @staticmethod
    def doit(Total_Steps, Stage_1_End_Step, Stage_2_Start_Step, Stage_1_CFG, Stage_2_CFG, Freeze_Wildcards, **dynamic_inputs):
        # Combine fixed inputs into a dictionary
        control_pipe = {
            "Total_Steps": Total_Steps,
            "Stage_1_End_Step": Stage_1_End_Step,
            "Stage_2_Start_Step": Stage_2_Start_Step,
            "Stage_1_CFG": Stage_1_CFG,
            "Stage_2_CFG": Stage_2_CFG,
            "Freeze_Wildcards": Freeze_Wildcards,
        }

        # Add dynamic style selections to the dictionary
        style = {
            category: style
            for category, style in dynamic_inputs.items()
            if category in StyleInjectorFN.styles_by_category
        }

        control_pipe["style"] = style

        return (control_pipe,)


# Register the node
NODE_CLASS_MAPPINGS = {
    "SDXL Control Module (Focus Nodes)": SDXLControlModuleFN,
}