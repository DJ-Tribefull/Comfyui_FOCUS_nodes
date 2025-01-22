from .style_injector_FN import StyleInjectorFN

class StyleSelectorFN:
    def __init__(self):
        self.style_injector = StyleInjectorFN()

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
                **dynamic_styles
            }
        }

    RETURN_TYPES = ("DICTIONARY",)
    RETURN_NAMES = ("styles",)
    FUNCTION = "execute"
    CATEGORY = "⚜️ Focus Nodes/Style"

    def execute(self, **dynamic_inputs):
        # Collect all valid categories and styles
        styles = {
            category: style
            for category, style in dynamic_inputs.items()
            if category in StyleInjectorFN.styles_by_category
        }

        return (styles,)

NODE_CLASS_MAPPINGS = {
    "Style Selector (Focus Nodes)": StyleSelectorFN,
}