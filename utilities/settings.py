''' Created: 13/09/2023 '''

# NOTE: Do not modify this file, modify the settings.yml created on first use.

# External Dependencies
import os
import yaml

# Internal Dependencies
from utilities.logger_formats import Log
from utilities.custom_exceptions import ScraperExceptions as SE

class Settings:
    ''' Purpose: Load and handle application settings '''

    def __init__(self):

        # General configurable options:
        # If true, the launcher prompts you to specify an output name.
        self.PICK_OUTPUT_NAME = False  # Type: bool, Default: False
        # Auto-generated output filename base string.
        self.GENERATED_OUTPUT_NAME_BASE = 'result'  # Type: str, Default: "result"
        # How many seconds to sleep to minimize website strain.
        self.RATE_LIMIT_DELAY = 2  # Type: int, Default: 2
        # How many seconds to wait before webdriver timeout.
        self.SELENIUM_LOGGING = False  # Type: bool, Default: False
        # If true, sets selenium browser to not be in headless mode.
        self.SELENIUM_HEADER = False  # Type: bool, Default: False
        # If true, dumps all raw data blocks to output textfile.
        self.DUMP_RAW_DATA = True  # Type: bool, Default: True
        # If true, on any suspect bad data issue, code will exit.
        self.DATA_STRICT = True # Type: bool, Default: True

        # Warning, avoid modifying the below options:
        # Location of scraper configuration JSON file directory.
        self.CONFIG_DIRECTORY = 'scrape_configs/'  # Type: str, Default: "scrape_configs/"
        # Directory location to save scraper results to file.
        self.OUTPUT_DIRECTORY = 'output_files/'  # Type: str, Default: "output_files/"

        # Load settings from settings.yml if it exists, or create it with default settings
        self.load_and_override_settings()

    def get_default_settings(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def load_and_override_settings(self):
        settings_yml_path = 'settings.yml'
        default_settings = self.get_default_settings()
        if os.path.exists(settings_yml_path):
            with open(settings_yml_path, 'r') as file:
                yaml_content = yaml.safe_load(file)
                # Override default settings with any custom settings
                for key, value in yaml_content.items():
                    if hasattr(self, key):
                        # Ensure the value type in YAML matches the type of the default setting
                        default_value = getattr(self, key)
                        if isinstance(value, type(default_value)):
                            setattr(self, key, value)
                        else:
                            raise SE.BadSettings(f"Type mismatch for setting {key}. Expected {type(default_value)}, but got {type(value)}.")
        else:
            # If settings.yml doesn't exist, create it with default values
            Log.info('Creating new local settings.yml')
            with open(settings_yml_path, 'w') as file:
                yaml.dump(default_settings, file, default_flow_style=False)
