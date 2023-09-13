''' Created: 13/09/2023 '''

# NOTE: This Python file exists only to store configuration settings.

# ===================== Configurable scraper constants =====================

PICK_OUTPUT_NAME = False
''' Type: bool
    Description: If true launcher prompts you to specify a output name.
    Default: True
'''
GENERATED_OUTPUT_NAME_BASE = 'result'
''' Type: str
    Description: Auto generated output filename base string.
    Default: "result"
'''
RATE_LIMIT_DELAY = 2 # TODO: Implement
''' Type: int
    Description: Howmany seconds to sleep to minimise website strain.
    Default: 2
'''
WEBDRIVER_TIMEOUT = 20
''' Type: int
    Description: Howmany seconds to wait before webdriver timeout.
    Default: 20
'''
DUMP_RAW_DATA = True # TODO: Implement
''' Type: bool
    Description: If true dumps all raw data blocks to output textfile. 
    Default: True
'''

# ===================== Constants requiring careful modification =====================

CONFIG_DIRECTORY = 'scrape_configs/'
''' Type: str 
    Description: Location of scraper configuration JSON file directory.
    Default: "scrape_configs/"
'''
OUTPUT_DIRECTORY = 'output_files/'
''' Type: str
    Description: Directory location to save scraper results to file.
    Default: "output_files/"
'''
