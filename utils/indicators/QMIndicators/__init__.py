import os
import importlib
import pkgutil

# Get the current directory path
package_dir = os.path.dirname(__file__)

# Loop through all Python files in the directory
for _, module_name, _ in pkgutil.iter_modules([package_dir]):
    if module_name == "__init__":
        continue

    # Construct the full module name
    module_full_name = f"{__name__}.{module_name}"

    # Import the module
    module = importlib.import_module(module_full_name)

    # Get all the attributes of the module
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        # Check if the attribute is a class and not a built-in type
        if isinstance(attribute, type):
            globals()[attribute.__name__] = attribute
