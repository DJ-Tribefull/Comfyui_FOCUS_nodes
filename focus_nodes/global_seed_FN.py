class GlobalSeedFN:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "value": ("INT", {"default": 123456789, "min": 0, "max": 0xffffffffffffffff}),
                "seed_mode": ("BOOLEAN", {"default": False, "label_on": "seed_frozen", "label_off": "seed_random"}),
                "last_seed": ("STRING", {"default": ""}),
                "randomize": ("BOOLEAN", {"default": False, "label_on": "all_random", "label_off": "shared_seed"}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "doit"

    CATEGORY = "⚜️ Focus Nodes/Utility"

    OUTPUT_NODE = True

    def doit(self, **kwargs):
        return {}
    
NODE_CLASS_MAPPINGS = {
    "Global Seed Controller (Focus Nodes)": GlobalSeedFN,
}