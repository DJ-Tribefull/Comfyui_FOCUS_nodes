import random

import nodes
import server
from enum import Enum
from aiohttp import web
from . import global_seed_FN

max_seed = 2**32 - 1  

class SeedGenerator:
    def __init__(self, base_value, seed_mode):

        self.base_value = base_value
        self.seed_mode = seed_mode

    def next(self):
        seed = self.base_value
        if not self.seed_mode:  # Randomize seed if not frozen
            self.base_value = random.randint(0, max_seed)
        
        # Return the updated seed
     
        return seed


def control_seed(v):

    seed_mode = v['inputs']['seed_mode']
    value = v['inputs']['value']

    # Update seed based on the seed_mode
    if not seed_mode:  # Randomize the seed
        value = random.randint(0, max_seed)

    # Update the node's value
    v['inputs']['value'] = value

    # Debugging log
    print(f"[control_seed] Updated seed: {value}, Seed mode: {'Frozen' if seed_mode else 'Randomized'}")

    return value

def prompt_seed_update(json_data):

    try:
        widget_idx_map = json_data['extra_data']['extra_pnginfo']['workflow']['widget_idx_map']
    except Exception:
        print(f"Exception in prompt seed update")  
        return False, None

    # First Pass: Find and process the GlobalSeedFN node
    seed_generator = None  # Initialize the seed generator
    value = None           # Initialize the global seed value
    seed_mode = None       # Initialize the seed mode
    randomize = False  # Initialize the randomize_all flag

    # Locate and process the GlobalSeedFN node
    for k, v in json_data['prompt'].items():
        if 'class_type' not in v:
            continue

        cls = v['class_type']
        if cls.lower() == 'global seed controller (focus nodes)'.lower():
            seed_mode = v['inputs']['seed_mode']
            randomize_all = v['inputs']['randomize']  # Capture the randomize_all state
            value = v['inputs']['value']

            # Update the seed value
            value = control_seed(v)  # Use `v` directly, as it's the node dictionary

            if value is not None:
                seed_generator = SeedGenerator(value, seed_mode)
            break  # Exit the loop once GlobalSeedFN is found and processed

    # If no GlobalSeedFN is found, exit early
    if value is None:
        raise ValueError("GlobalSeedFN node not found or failed to initialize.")

    # Second Pass: Process all other nodes
    for k, v in json_data['prompt'].items():
        # Replace $GlobalSeed.value$ in node inputs
        for k2, v2 in v['inputs'].items():
            if isinstance(v2, str) and '$GlobalSeed.value$' in v2:
                v['inputs'][k2] = v2.replace('$GlobalSeed.value$', str(value))

        # Skip nodes not in the widget index map or without relevant keys
        if k not in widget_idx_map or ('seed' not in widget_idx_map[k] and 'noise_seed' not in widget_idx_map[k]):
            continue

        # Priority: seed_mode > randomize
        if seed_mode:
            # Reuse the current seed (frozen state)
            if 'seed' in v['inputs']:
                if isinstance(v['inputs']['seed'], int):
                    v['inputs']['seed'] = v['inputs']['seed']  # Keep the current value

            if 'noise_seed' in v['inputs']:
                if isinstance(v['inputs']['noise_seed'], int):
                    v['inputs']['noise_seed'] = v['inputs']['noise_seed']  # Keep the current value

        else:
            # seed_mode == False
            if randomize:
                # Generate a unique random seed for each widget
                if 'seed' in v['inputs']:
                    if isinstance(v['inputs']['seed'], int):
                        v['inputs']['seed'] = random.randint(0, max_seed)

                if 'noise_seed' in v['inputs']:
                    if isinstance(v['inputs']['noise_seed'], int):
                        v['inputs']['noise_seed'] = random.randint(0, max_seed)
            else:
                # Use the shared seed from GlobalSeedFN
                if 'seed' in v['inputs']:
                    if isinstance(v['inputs']['seed'], int):
                        v['inputs']['seed'] = value

                if 'noise_seed' in v['inputs']:
                    if isinstance(v['inputs']['noise_seed'], int):
                        v['inputs']['noise_seed'] = value


    return value is not None


def workflow_seed_update(json_data):
    nodes = json_data['extra_data']['extra_pnginfo']['workflow']['nodes']
    widget_idx_map = json_data['extra_data']['extra_pnginfo']['workflow']['widget_idx_map']
    prompt = json_data['prompt']

    updated_seed_map = {}
    value = None

    # Sort nodes so 'Global Controller (Focus Nodes)' is processed first
    nodes.sort(key=lambda x: x['type'] != 'Global Seed Controller (Focus Nodes)')

    for node in nodes:
        node_id = str(node['id'])
        if node_id in prompt:
            if node['type'] == 'Global Seed Controller (Focus Nodes)':
                node['widgets_values'][2] = node['widgets_values'][0]
                node['widgets_values'][0] = prompt[node_id]['inputs']['value']
                value = prompt[node_id]['inputs']['value']

            elif node_id in widget_idx_map:
                widget_idx = None
                seed = None

                if 'noise_seed' in prompt[node_id]['inputs']:
                    seed = prompt[node_id]['inputs']['noise_seed']
                    widget_idx = widget_idx_map[node_id].get('noise_seed')
                elif 'seed' in prompt[node_id]['inputs']:
                    seed = prompt[node_id]['inputs']['seed']
                    widget_idx = widget_idx_map[node_id].get('seed')

                if widget_idx is not None:
                    node['widgets_values'][widget_idx] = seed
                    updated_seed_map[node_id] = seed


    # Send the updated data through the event
    server.PromptServer.instance.send_sync("fn-global-seed", {
        "value": value,
        "seed_map": updated_seed_map,
    })



def onprompt(json_data):
    print(f"onprompt triggered")  
    control_seed_valid = prompt_seed_update(json_data)
    if control_seed_valid:
        workflow_seed_update(json_data)
    
    print("onprompt triggered with data")
    return json_data


# Register the onprompt handler with the server
server.PromptServer.instance.add_on_prompt_handler(onprompt)
print(f"onprompt handler registered")


# Register the node
NODE_CLASS_MAPPINGS = {}