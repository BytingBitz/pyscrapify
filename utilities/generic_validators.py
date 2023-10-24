''' Created: 14/09/2023 '''

# External Dependencies:
from typing import Dict, List
import re, os, json

# Internal Dependencies:
from utilities.custom_exceptions import ScraperExceptions as SE

class GenericValidators:
    ''' Purpose: Contains all generic validation logic. '''
    @staticmethod
    def validate_file_exists(file_path: str):
        ''' Purpose: Validates that file exists at given file_path. '''
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'{file_path} does not exist.')
    @staticmethod
    def validate_json_structure(data: json):
        ''' Purpose: Validates JSON configuration file is structured as expected. '''
        if 'scraper' not in data:
            raise SE.InvalidConfigFile('JSON is missing the "scraper" key...')
        if 'entries' not in data:
            raise SE.InvalidConfigFile('JSON is missing the "entries" key...')
        scraper = data['scraper']
        if not isinstance(scraper, str):
            raise SE.InvalidConfigFile('The JSON "scraper" value must be a string.')
        if scraper == 'BaseScraper':
            raise SE.InvalidConfigFile('The value "BaseScraper" is not a valid scraper.')
        GenericValidators.validate_file_exists(f'scrapers/{scraper}.py')
        if not isinstance(data['entries'], dict):
            raise SE.InvalidConfigFile('The JSON "entries" value must be a dictionary.')
    @staticmethod
    def validate_name(name: str):
        ''' Purpose: Validates the given name. '''
        name_pattern = re.compile(r'^[a-zA-Z0-9\s\-.,()\'&#]+$')
        if not name_pattern.match(name):
            raise SE.InvalidConfigFile(f'JSON contains invalid name format: {name}')
    @staticmethod
    def validate_data_bound(data_bound: Dict[str, int], texts: List[List]):
        ''' Purpose: Validates if the data is within list bounds. '''
        if not (data_bound['start_idx'] >= 0 and data_bound['end_idx'] < len(texts)):
            raise SE.UnexpectedData(f'Expected data block goes out of bounds:\n{texts}')
    @staticmethod
    def validate_data_count(actual_count: int, expected_count: int):
        ''' Purpose: Validates if number scraped data blocks matches expected number. '''
        if actual_count != expected_count:
            raise SE.UnexpectedData(f'Expected {expected_count}, got {actual_count}...')
    @staticmethod
    def validate_for_overlap(data_bounds: List[Dict[str, int]], new_data_bound: Dict[str, int]):
        ''' Purpose: Validates if there is any overlaps in the ranges of any data bounds. '''
        if any(existing_bound['start_idx'] < new_data_bound['end_idx'] and existing_bound['end_idx'] > new_data_bound['start_idx'] for existing_bound in data_bounds):
            raise SE.UnexpectedData("Overlapping data bounds detected.")
