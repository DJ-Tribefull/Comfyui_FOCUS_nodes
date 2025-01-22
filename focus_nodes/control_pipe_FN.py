class ControlPipeFN:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "Control_Pipe": ("DICTIONARY",),
            },
        }

    RETURN_TYPES = (
        "INT", "INT", "INT", "FLOAT", "FLOAT", "DICTIONARY", "BOOLEAN",
    )
    RETURN_NAMES = (
        "Total Steps", "Stage 1 End", "Stage 2 Start", "Stage 1 CFG", "Stage 2 CFG", "Style", "Freeze Wildcards",
    )
    FUNCTION = "unpack"
    CATEGORY = "⚜️ Focus Nodes/Utility"

    @staticmethod
    def unpack(Control_Pipe):
        # Extract values from the control pipe dictionary
        clip = Control_Pipe.get("Clip")
        total_steps = Control_Pipe.get("Total_Steps", 0)
        stage_1_end = Control_Pipe.get("Stage_1_End_Step", 0)
        stage_2_start = Control_Pipe.get("Stage_2_Start_Step", 0)
        stage_1_cfg = Control_Pipe.get("Stage_1_CFG", 0.0)
        stage_2_cfg = Control_Pipe.get("Stage_2_CFG", 0.0)
        style = Control_Pipe.get("style", {})
        freeze_wildcards = Control_Pipe.get("Freeze_Wildcards",)

        return total_steps, stage_1_end, stage_2_start, stage_1_cfg, stage_2_cfg, style, freeze_wildcards


# Register the node
NODE_CLASS_MAPPINGS = {
    "Control Pipe (Focus Nodes)": ControlPipeFN,
}