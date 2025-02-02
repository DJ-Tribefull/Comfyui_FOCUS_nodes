
"""
Module: wildcard_processor_FN.py
Purpose: Implements a custom ComfyUI node for processing wildcard text inputs.
"""

import os
import re
import numpy as np

class WildcardProcessor:
    def __init__(self, wildcard_path=None):
        # Dynamically determine the path to the focus_wildcards folder
        self.wildcards_path = wildcard_path or os.path.abspath(os.path.join(__file__, "..", "..", "focus_wildcards"))

        # Ensure the wildcard path exists or create it
        if not os.path.exists(self.wildcards_path):
            print(f"[WildcardProcessor] The wildcard path '{self.wildcards_path}' does not exist. Creating it now.")
            os.makedirs(self.wildcards_path, exist_ok=True)

        self._wildcard_dict = {}
        self._last_refresh_state = {}
        self.read_wildcards()

    @property
    def wildcard_dict(self):
        """Returns a copy of the wildcard dictionary."""
        return self._wildcard_dict.copy()

    def wildcard_normalize(self, key):
        """Normalize wildcard keys for consistency."""
        return key.replace("\\", "/").replace(' ', '-').lower()

    def read_wildcards(self):
        """Reads wildcard .txt files into a dictionary."""
        self._wildcard_dict = {}
        for root, _, files in os.walk(self.wildcards_path):
            for file in files:
                if file.endswith('.txt'):
                    key = self.wildcard_normalize(os.path.splitext(file)[0])
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            self._wildcard_dict[key] = [
                                line.strip() for line in f if line.strip() and not line.startswith('#')
                            ]
                    except Exception as e:
                        print(f"Failed to read wildcard file '{file}': {e}")

    def replace_wildcards(self, string, seed=None, cached_wildcards=None):
        """Replaces wildcard placeholders in a string with random values, using a cache if provided."""
        rng = np.random.default_rng(seed)
        wildcard_cache = cached_wildcards if cached_wildcards is not None else {}

        def replace_match(match):
            key = self.wildcard_normalize(match.group(1))
            if key in wildcard_cache:
                return wildcard_cache[key]
            elif key in self._wildcard_dict:
                replacement = rng.choice(self._wildcard_dict[key])
                wildcard_cache[key] = replacement  # Store it for future use
                return replacement
            else:
                print(f"Wildcard key '{key}' not found in dictionary.")
                return f"!!__{key}__"

        pattern = r"__([\w.\-+/\\]+?)__"
        return re.sub(pattern, replace_match, string), wildcard_cache


class WildcardProcessorFN:
    def __init__(self, wildcard_path=None):
        self.processor = WildcardProcessor(wildcard_path)
        self.cached_result = None
        self.cached_wildcards = None  # Stores wildcard values when freeze_wildcards is True

    @classmethod
    def INPUT_TYPES(cls):
        """Defines the input types for the ComfyUI node."""
        return {
            "required": {
                "freeze_wildcards": ("BOOLEAN", {"default": False}),
                "prompt_input": ("STRING", {"multiline": True, "defaultInput": True,}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    CATEGORY = "⚜️ Focus Nodes/Text"
    FUNCTION = "process"

    def process(self, prompt_input, seed=None, freeze_wildcards=False):
        """Processes the input text by replacing wildcards."""
        if not prompt_input.strip():
            return ("",)

        if freeze_wildcards:
            if self.cached_result is not None and self.cached_wildcards is not None:
                return (self.processor.replace_wildcards(prompt_input, seed, self.cached_wildcards)[0],)

        try:
            processed_result, self.cached_wildcards = self.processor.replace_wildcards(prompt_input, seed)
            self.cached_result = processed_result
        except Exception as e:
            print(f"Error during wildcard replacement: {e}")
            return (prompt_input,)

        return (self.cached_result,)


# Register the node
NODE_CLASS_MAPPINGS = {
    "Wildcard Processor (Focus Nodes)": WildcardProcessorFN,
}
