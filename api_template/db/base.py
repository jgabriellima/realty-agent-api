import importlib
import os
import pkgutil

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def load_models():
    """
    Dynamically imports all modules in the models package to ensure they are loaded.
    """
    package_dir = os.path.dirname(__file__)
    module_path = os.path.join(package_dir, "../models")

    # Dynamically load all modules in the 'models' directory
    for _, module_name, _ in pkgutil.iter_modules([module_path]):
        importlib.import_module(f"api_template.models.{module_name}")


# Call the loader to dynamically import all models when Base is imported
load_models()
