''' Created: 13/09/2023 '''

# NOTE: This Python file exists only to store configuration settings.

# General configurable options:
# ============================================================================

PICK_OUTPUT_NAME = False
''' Type: bool                                                              \n
    Description: If true launcher prompts you to specify a output name.     \n
    Default: True                                                           \n
'''
GENERATED_OUTPUT_NAME_BASE = 'result'
''' Type: str                                                               \n
    Description: Auto generated output filename base string.                \n
    Default: "result"                                                       \n
'''
RATE_LIMIT_DELAY = 2.5
''' Type: int                                                               \n
    Description: How many seconds to sleep to minimise website strain.       \n
    Default: 2                                                              \n
'''
WEBDRIVER_TIMEOUT = 20
''' Type: int                                                               \n
    Description: How many seconds to wait before webdriver timeout.          \n
    Default: 20                                                             \n
'''
DUMP_RAW_DATA = True
''' Type: bool                                                              \n
    Description: If true dumps all raw data blocks to output textfile.      \n
    Default: True                                                           \n
'''

# Warning, avoid modifying below options:
# ============================================================================

CONFIG_DIRECTORY = 'scrape_configs/'
''' Type: str                                                               \n
    Description: Location of scraper configuration JSON file directory.     \n
    Default: "scrape_configs/"                                              \n
'''
OUTPUT_DIRECTORY = 'output_files/'
''' Type: str                                                               \n
    Description: Directory location to save scraper results to file.        \n
    Default: "output_files/"                                                \n
'''
