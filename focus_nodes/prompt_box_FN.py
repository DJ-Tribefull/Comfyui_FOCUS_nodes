from . import wildcard_processor_FN

class PromptBoxFN:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        wildcard_list = ["Available Wildcards"] + list(wildcard_processor_FN.WildcardProcessor().wildcard_dict.keys())
        return {
            "required": {
                "text": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "dynamicPrompts": True,
                    }
                ),
                "wildcard_categories": (
                    wildcard_list,
                    {
                        "default": "Explore",
                        "tooltip": "This dropdown is a list of all available .txt files in your focus_wildcards folder",
                    }
                ),
            }
        }


    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "wildcard_selector"
    CATEGORY = "⚜️ Focus Nodes/Text"

    @staticmethod
    def wildcard_selector(text, wildcard_categories):
        if wildcard_categories and wildcard_categories != "Select a Wildcard":
            wildcard = f""
            if wildcard not in text:  # Prevent duplicates
                text += f" {wildcard}"
        return text,

    @staticmethod
    def reload_wildcards():
        """Refresh the wildcard dictionary."""
        wildcard_processor_FN.WildcardProcessor().refresh_wildcards()
        
NODE_CLASS_MAPPINGS = {
    "Prompt Box (Focus Nodes)": PromptBoxFN,
}