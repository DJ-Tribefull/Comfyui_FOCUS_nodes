import os
import csv
import re  # Regular expression module for text processing

class StyleInjectorFN:
    _last_refresh_time = None  # Tracks the last modification time of the focus_styles.csv file
    styles_by_category = {}  # Holds styles loaded from the CSV file

    @staticmethod
    def load_focusstyles_csv():
        # Dynamically determine the path to focus_styles.csv
        styles_path = os.path.abspath(os.path.join(__file__, "..", "..", "focus_styles", "focus_styles.csv"))

        styles_by_category = {}

        if not os.path.exists(styles_path):
            print(f"""Error. No focus_styles.csv found. Put the csv in the focus_styles folder. Expected location: {styles_path}.""")
            return {"Error": {"Error loading focus_styles.csv, check the console": ["", ""]}}

        try:
            with open(styles_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header:
                    print("focus_styles.csv is empty.")
                    return {"Error": {"Error: Empty CSV file": ["", ""]}}

                for row in reader:
                    if len(row) >= 4:
                        category = row[0].strip()
                        style_name = row[1].strip()
                        positive_prompt = row[2].strip()
                        negative_prompt = row[3].strip()

                        if category not in styles_by_category:
                            styles_by_category[category] = {}

                        # Ensure only valid data is added
                        styles_by_category[category][style_name] = [
                            positive_prompt,
                            negative_prompt,
                        ]
        except Exception as e:
            print(f"Error reading focus_styles.csv: {e}")
            return {"Error": {"Error loading focus_styles.csv, check the console": ["", ""]}}

        return styles_by_category

    @classmethod
    def refresh_styles(cls):
        # Dynamically determine the path to focus_styles.csv
        styles_path = os.path.abspath(os.path.join(__file__, "..", "..", "focus_styles", "focus_styles.csv"))

        if not os.path.exists(styles_path):
            print(f"focus_styles.csv file not found. Skipping refresh. Expected location: {styles_path}")
            return

        try:
            last_modified_time = os.path.getmtime(styles_path)
        except OSError as e:
            print(f"Error accessing focus_styles.csv: {e}")
            return

        if cls._last_refresh_time != last_modified_time:
            print("Detected changes in focus_styles.csv. Reloading styles...")
            cls.styles_by_category = cls.load_focusstyles_csv()
            cls._last_refresh_time = last_modified_time


    @classmethod
    def INPUT_TYPES(cls):
        """

        Returns:
            dict: A dictionary of required inputs, including dropdowns for categories
                  and styles, and inputs for positive and negative prompts.
        """
        cls.refresh_styles()  # Ensure the latest styles are loaded

        input_types = {
            "required": {
                "positive_in": ("STRING", {"default": "", "defaultInput": True}),  # Positive prompt input
                "negative_in": ("STRING", {"default": "", "defaultInput": True}),  # Negative prompt input
            }
        }

        # Add dropdowns for each category
        if cls.styles_by_category:
            input_types["required"].update({
                category: (list(styles.keys()),) for category, styles in cls.styles_by_category.items()
            })

        return input_types

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "execute"
    CATEGORY = "⚜️ Focus Nodes/Style"

    def execute(self, positive_in, negative_in, **kwargs):
        """
        Processes and concatenates prompts based on selected styles.

        Args:
            positive_in (str): The real positive prompt to replace {prompt}.
            negative_in (str): The real negative prompt to replace {prompt}.
            **kwargs: Key-value pairs where keys are categories and values are selected styles.

        Returns:
            tuple: The final positive and negative prompts after processing.
        """
        # Refresh styles every time the node runs
        self.refresh_styles()

        def process_prompt(current_prompt, before_prompt, after_prompt):
            """
            Processes the current prompt, splitting it at {prompt} and appending
            text to before and after parts.

            Args:
                current_prompt (str): The prompt to process.
                before_prompt (str): Text before {prompt}.
                after_prompt (str): Text after {prompt}.

            Returns:
                tuple: Updated before and after prompts.
            """
            if current_prompt.strip() == "{prompt}":
                return before_prompt, after_prompt
            if "{prompt}" in current_prompt:
                before, after = current_prompt.split("{prompt}", 1)
                before_prompt += before
                after_prompt += after.replace("{prompt}", "")
            else:
                after_prompt += current_prompt
            return before_prompt, after_prompt

        def finalize_prompt(before_prompt, after_prompt):
            """
            Combines before and after prompts, ensuring proper placement of {prompt}.

            Args:
                before_prompt (str): Text before {prompt}.
                after_prompt (str): Text after {prompt}.

            Returns:
                str: The final concatenated prompt.
            """
            if "{prompt}" in before_prompt or "{prompt}" in after_prompt:
                return before_prompt + after_prompt
            return before_prompt + "{prompt}" + after_prompt

        # Handle cases with no active styles
        if not kwargs:
            return positive_in, negative_in

        positive_before_prompt, positive_after_prompt = "", ""
        negative_before_prompt, negative_after_prompt = "", ""

        for category, style_name in kwargs.items():
            if category in self.styles_by_category and style_name in self.styles_by_category[category]:
                positive_prompt, negative_prompt = self.styles_by_category[category][style_name]
                positive_before_prompt, positive_after_prompt = process_prompt(
                    positive_prompt, positive_before_prompt, positive_after_prompt
                )
                negative_before_prompt, negative_after_prompt = process_prompt(
                    negative_prompt, negative_before_prompt, negative_after_prompt
                )

        concatenated_positive = finalize_prompt(positive_before_prompt, positive_after_prompt)
        concatenated_negative = finalize_prompt(negative_before_prompt, negative_after_prompt)

        # Replace single {prompt} with empty string if no other content exists
        concatenated_positive = "" if concatenated_positive.strip() == "{prompt}" else concatenated_positive
        concatenated_negative = "" if concatenated_negative.strip() == "{prompt}" else concatenated_negative

        # If no styles have been applied, pass inputs through unaltered
        if not concatenated_positive.strip():
            concatenated_positive = positive_in
        if not concatenated_negative.strip():
            concatenated_negative = negative_in

        # Replace {prompt} with positive_in and negative_in
        concatenated_positive = concatenated_positive.replace("{prompt}", positive_in)
        concatenated_negative = concatenated_negative.replace("{prompt}", negative_in)

        # Remove whitespace immediately preceding a comma
        concatenated_positive = re.sub(r'\s+,', ',', concatenated_positive)
        concatenated_negative = re.sub(r'\s+,', ',', concatenated_negative)

        # Ensure the first character is alphanumeric by removing leading whitespace and punctuation
        concatenated_positive = re.sub(r'^\W+', '', concatenated_positive)
        concatenated_negative = re.sub(r'^\W+', '', concatenated_negative)

        return concatenated_positive, concatenated_negative

NODE_CLASS_MAPPINGS = {
    "Style Injector (Focus Nodes)": StyleInjectorFN,
}