import importlib
import inspect
import os
import sys

from api_template.external.core.base import BaseHandler


def autodiscover_handlers(handler_directory: str):
    """
    Autodiscover all handler classes that inherit from BaseHandler in the given directory.
    :param handler_directory: The path to the handlers' directory.
    :return: List of discovered handler classes.
    """
    handler_classes = []

    # Add the parent directory of the handler_directory to sys.path
    parent_dir = os.path.dirname(os.path.dirname(handler_directory))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    for root, dirs, files in os.walk(handler_directory):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                # Derive the module name from the file path
                module_path = os.path.relpath(os.path.join(root, file), start=parent_dir)
                # Construct the full module name
                full_module_name = (
                    module_path.replace("/", ".")
                    .replace("\\", ".")
                    .replace(".py", "")
                    .replace("...", "api_template.external.")
                )
                try:
                    # Dynamically import the module
                    module = importlib.import_module(full_module_name)

                    # Inspect the module for classes that inherit from BaseHandler
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseHandler) and obj != BaseHandler:
                            handler_classes.append(obj)
                except ImportError as e:
                    print(f"Error importing {full_module_name}: {e}")

    return handler_classes
