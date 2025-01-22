import os
import folder_paths
import comfy.sd

class KSamplerSettingsFN:
    
    CATEGORY = "⚜️ Focus Nodes/Utility"
    
    RETURN_TYPES = (folder_paths.get_filename_list("checkpoints"),
                    comfy.samplers.KSampler.SAMPLERS,
                    comfy.samplers.KSampler.SCHEDULERS,
                    )
    
    RETURN_NAMES = ("Checkpoint", "Sampler", "Scheduler",)
    
    FUNCTION = "get_data"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"ckpt_name": (folder_paths.get_filename_list("checkpoints"),),
                             "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                             "scheduler_name": (comfy.samplers.KSampler.SCHEDULERS,),
                             }
                }

    def get_data(self, ckpt_name, sampler_name, scheduler_name):
        return (ckpt_name, sampler_name, scheduler_name,)

NODE_CLASS_MAPPINGS = {
    "KSampler Settings (Focus Nodes)": KSamplerSettingsFN,
}