import os
import importlib
import traceback

def generate_node_list():
    focus_nodes_dir = os.path.join(os.path.dirname(__file__), "focus_nodes")  # Path to the focus_nodes folder

    if not os.path.exists(focus_nodes_dir):
        print(f"Error: 'focus_nodes' folder not found at {focus_nodes_dir}.")
        return []

    # Construct list of all .py files in the folder (excluding __init__.py if it exists)
    node_files = [
        os.path.splitext(filename)[0]  # Remove the .py extension
        for filename in os.listdir(focus_nodes_dir)
        if filename.endswith(".py") and filename != "__init__.py"
    ]

    if not node_files:
        print(f"No valid modules found in 'focus_nodes'.")
    return node_files


# Generate the node list
node_list = generate_node_list()

# Initialize the unified NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS dictionaries
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Import each module and update mappings
for module_name in node_list:
    try:
        imported_module = importlib.import_module(f".focus_nodes.{module_name}", __name__)

        # Update NODE_CLASS_MAPPINGS
        if hasattr(imported_module, "NODE_CLASS_MAPPINGS"):
            NODE_CLASS_MAPPINGS.update(imported_module.NODE_CLASS_MAPPINGS)
        else:
            print(f"Warning: Module {module_name} does not contain NODE_CLASS_MAPPINGS.")

        # Dynamically generate NODE_DISPLAY_NAME_MAPPINGS
        for node_name in imported_module.NODE_CLASS_MAPPINGS.keys():
            NODE_DISPLAY_NAME_MAPPINGS[node_name] = f"⚜️ {node_name.replace(' (Focus Nodes)', '')}"

    except Exception as e:
        print(f"Error importing module {module_name}: {e}")
        traceback.print_exc()

WEB_DIRECTORY = "./js"

# Export mappings
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]