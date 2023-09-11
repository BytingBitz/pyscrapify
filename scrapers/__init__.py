import os
import importlib

# Loop over all the files in the directory that contain this __init__.py
for file_name in os.listdir(os.path.dirname(__file__)):
    # Exclude __init__.py and other non-python files
    if file_name.endswith('.py') and file_name != '__init__.py':
        module_name = file_name[:-3]  # remove the .py
        importlib.import_module(f".{module_name}", package=__name__)
