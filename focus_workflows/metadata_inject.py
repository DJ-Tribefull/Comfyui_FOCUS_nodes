import os
import json
from PIL import Image, PngImagePlugin


def add_workflow_metadata_to_png(input_file, output_file, workflow_json_file):

    # Load the PNG image
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    try:
        img = Image.open(input_file)
    except Exception as e:
        print(f"Error opening input PNG file: {e}")
        return

    # Load the workflow JSON
    if not os.path.exists(workflow_json_file):
        print(f"Error: Workflow JSON file '{workflow_json_file}' not found.")
        return

    try:
        with open(workflow_json_file, "r", encoding="utf-8") as f:
            workflow_json = json.load(f)
    except UnicodeDecodeError as e:
        print(f"Error reading workflow JSON file due to encoding issues: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file: {e}")
        return
    except Exception as e:
        print(f"Unexpected error reading workflow JSON file: {e}")
        return

    # Convert JSON to a string for metadata
    try:
        workflow_metadata = json.dumps(workflow_json)
    except Exception as e:
        print(f"Error serializing workflow JSON: {e}")
        return

    # Add metadata to the PNG
    meta = PngImagePlugin.PngInfo()
    meta.add_text("workflow", workflow_metadata)

    try:
        img.save(output_file, "PNG", pnginfo=meta)
        print(f"Workflow metadata successfully added to '{output_file}'.")
    except Exception as e:
        print(f"Error saving output PNG file: {e}")
        return


if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(__file__)

    # Define file paths
    input_png = os.path.join(script_dir, "addworkflow.png")
    output_png = os.path.join(script_dir, "output_with_metadata.png")
    workflow_json_file = os.path.join(script_dir, "addworkflow.json")

    # Add workflow metadata to the PNG
    add_workflow_metadata_to_png(input_png, output_png, workflow_json_file)
