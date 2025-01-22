import comfy.model_management as model_management
import gc
import torch

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class ModelUnloaderFN:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any_type": (any,),  # This is the passthrough value
                "enable": ("BOOLEAN", {"default": True}),
            },
            "optional": {"model_to_unload": (any,)},
        }

    RETURN_TYPES = (any,)
    RETURN_NAMES = ("passthrough",)
    FUNCTION = "doit"
    CATEGORY = "⚜️ Focus Nodes/Memory Management"
    
    @classmethod
    def VALIDATE_INPUTS(s, **kwargs):
        return True


    def doit(self, enable, **kwargs):
        if not enable:
            print("Model unloading disabled. Skipping operation.")
            return list(kwargs.values())  # Passthrough without modifications

        print("Unload Model:")
        
        loaded_models = model_management.loaded_models()
        if kwargs.get("model_to_unload") in loaded_models:
            print(" - Model found in memory, unloading...")
            loaded_models.remove(kwargs.get("model_to_unload"))
        
        else:
            model = kwargs.get("model_to_unload")
            if type(model) == dict:
                keys = [(key, type(value).__name__) for key, value in model.items()]
                for key, model_type in keys:
                    if key == 'model_to_unload':
                        print(f"Unloading model of type {model_type}")
                        del model[key]
                        # Emptying the cache after this should free the memory.
                      
        model_management.free_memory(1e30, model_management.get_torch_device(), loaded_models)
        model_management.soft_empty_cache(True)
        
        try:

            gc.collect()
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

        except Exception as e:
            print(f"   - Failed to clear cache: {e}")

        return list(kwargs.values())

NODE_CLASS_MAPPINGS = {"Model Unloader (Focus Nodes)": ModelUnloaderFN}