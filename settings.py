''' Created: 13/09/2023 '''

# NOTE: This Python file exists only to store configuration settings.
#       Currently most settings will not be validated.

# str: Location of scraper configuration JSON files.
CONFIG_DIRECTORY = 'scrape_configs/'
# Location to save scraper results to file.
OUTPUT_DIRECTORY = 'output_files/'

# int: Howmany seconds to wait before timeout. 
WEBDRIVER_TIMEOUT = 20

# bool: If true dumps raw data blocks to output textfile.
DUMP_RAW_DATA = True # TODO: Implement
# bool: If true launcher prompts you to specify output names.
PICK_OUTPUT_NAME = False
# int: Request delay to minimise website strain.
RATE_LIMIT_DELAY = 2 # TODO: Implement

