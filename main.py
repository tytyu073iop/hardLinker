import os
import argparse
import re

# Output: ['Hello ', '${name}', ', welcome to ', '${city}', '!']
def tokenize_template_string(text):
    # This pattern matches ${...} or splits on it
    pattern = r'(\$\{[^}]*\})'
    return re.split(pattern, text)

# Example usage:
# template = "Hello ${name}, welcome to ${city}!"
# replacements = {
#     'name': 'John',
#     'city': 'New York'
# }
def replace_template_variables(text, replacements):
    """
    Replace template variables in the format ${variable_name} with provided values.
    
    Args:
        text: The string containing template variables
        replacements: Dictionary of {variable_name: replacement_value}
    
    Returns:
        The string with variables replaced
    """
    def replacer(match):
        variable = match.group(1)  # Get the content between ${ and }
        return str(replacements.get(variable, match.group(0)))  # Replace or keep original if not found
    
    # Pattern matches ${...} and captures the content between braces
    pattern = r'\$\{([^}]*)\}'
    return re.sub(pattern, replacer, text)


parser = argparse.ArgumentParser(
    prog="hardlinker",
    description="hardlinks series related files",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("from_dir", nargs=1, type=str,
                    help="paths to directory of files to hardlink")
parser.add_argument("to_dir", nargs=1, type=str,
                    help="paths to directory of files where to hardlink")
parser.add_argument("new_name", nargs=1, type=str,
                    help="new name of files with seasons and episodes")
parser.add_argument("--regex", "-r", nargs=1, type=str, default='s(\\d+)e(\\d+)',
                    help="write regex to recognize season and episode(order cannot be changed) with (\\d+)")
parser.add_argument("--test", "-t" , help="if turned on, just outputs result path for each file", action='store_true')

args = parser.parse_args().__dict__
from_dir: str = args.pop("from_dir")[0]
to_dir: str = args.pop("to_dir")[0]
new_name: str = args.pop("new_name")[0]
is_test: bool = args.pop("test")
regex = args["regex"][0] if type(args["regex"]) == list else args["regex"]

is_any_file: bool = False
for video_file in os.listdir(from_dir):
    # Extract season/episode info
    match = re.search(re.compile(regex), video_file)
    if not match:
        continue

    is_any_file = True
        
    season, episode = match.groups()
    
    
    result = replace_template_variables(new_name, {'season' : season, 'episode' : episode})
    result_filePath = os.path.join(to_dir, result)

    if is_test:
        print(result_filePath)
        continue

    # Create hardlinks
    os.link(os.path.join(from_dir, video_file), result_filePath)

if not is_any_file:
    print("No files with compatiable format found")


