''' Created: 13/09/2023 '''

# NOTE: This Python file exists only to store configuration settings.

# TODO: Move default settings to template, load settings such that custom settings.py can be created locally

# General configurable options:
PICK_OUTPUT_NAME = False
''' Type: bool, Default: False
    Description: If true launcher prompts you to specify a output name.
'''
GENERATED_OUTPUT_NAME_BASE = 'result'
''' Type: str, Default: "result"
    Description: Auto generated output filename base string.
'''
RATE_LIMIT_DELAY = 2
''' Type: int, Default: 2
    Description: How many seconds to sleep to minimise website strain.
'''
SELENIUM_TIMEOUT = 40
''' Type: int, Default: 20
    Description: How many seconds to wait before webdriver timeout.
'''
SELENIUM_LOGGING = False
''' Type: bool, default: False
    Description: If true enables selenium logs to stdout. 
'''
SELENIUM_HEADER = False
''' Type: bool, default: False
    Description: If true sets selenium browser to not be in headerless mode.
'''
DUMP_RAW_DATA = True
''' Type: bool, Default: True
    Description: If true dumps all raw data blocks to output textfile.
'''

# Warning, avoid modifying below options:
CONFIG_DIRECTORY = 'scrape_configs/'
''' Type: str, Default: "scrape_configs/"
    Description: Location of scraper configuration JSON file directory.
'''
OUTPUT_DIRECTORY = 'output_files/'
''' Type: str, Default: "output_files/"
    Description: Directory location to save scraper results to file.
'''
