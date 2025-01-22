"""
Module: wildcard_processor_FN.py
Purpose: Implements a custom ComfyUI node for processing wildcard text inputs.
"""

import os
import re
import numpy as np
import logging

logger = logging.getLogger(__name__)

class WildcardProcessor:
    def __init__(self, wildcard_path=None):
        # Dynamically determine the path to the focus_wildcards folder
        self.wildcards_path = wildcard_path or os.path.abspath(os.path.join(__file__, "..", "..", "focus_wildcards"))

        # Ensure the wildcard path exists or create it
        if not os.path.exists(self.wildcards_path):
            logger.warning(f"[WildcardProcessor] The wildcard path '{self.wildcards_path}' does not exist. Creating it now.")
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
                        logger.error(f"Failed to read wildcard file '{file}': {e}")

    def refresh_wildcards(self):
        """Refreshes the wildcard list only if .txt files have changed."""
        # Dynamically determine the path to focus_wildcards
        self.wildcards_path = os.path.abspath(os.path.join(__file__, "..", "..", "focus_wildcards"))

        # Ensure the wildcard path exists
        if not os.path.exists(self.wildcards_path):
            logger.error(f"[WildcardProcessor] The wildcard path '{self.wildcards_path}' does not exist.")
            return

        try:
            # Get current state of all .txt files in the folder
            current_files = {
                file.path: os.path.getmtime(file.path)
                for file in os.scandir(self.wildcards_path)
                if file.name.endswith('.txt')
            }

            # Check if there are any changes
            if current_files != self._last_refresh_state:
                self._last_refresh_state = current_files
                self.read_wildcards()

        except Exception as e:
            logger.error(f"Error during wildcard refresh: {e}")

    def replace_wildcards(self, string, seed=None):
        """Replaces wildcard placeholders in a string with random values."""
        rng = np.random.default_rng(seed)

        def replace_match(match):
            key = self.wildcard_normalize(match.group(1))
            if key in self._wildcard_dict:
                return rng.choice(self._wildcard_dict[key])
            else:
                logger.warning(f"Wildcard key '{key}' not found in dictionary.")
                return f"!!__{key}__"

        pattern = r"__([\w.\-+/\\]+?)__"
        return re.sub(pattern, replace_match, string)


class WildcardProcessorFN:
    def __init__(self, wildcard_path=None):
        self.processor = WildcardProcessor(wildcard_path)
        self.cached_result = None

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

        if freeze_wildcards and self.cached_result is not None:
            return (self.cached_result,)

        try:
            self.cached_result = self.processor.replace_wildcards(prompt_input, seed)
        except Exception as e:
            logger.error(f"Error during wildcard replacement: {e}")
            return (prompt_input,)

        return (self.cached_result,)


# Register the node
NODE_CLASS_MAPPINGS = {
    "Wildcard Processor (Focus Nodes)": WildcardProcessorFN,
}
