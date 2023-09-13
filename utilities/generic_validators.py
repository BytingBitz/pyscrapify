''' Created: 14/09/2023 '''

# External Dependencies:
from typing import Dict, List
import re, os, json

# Internal Dependencies:
from utilities.exception_handler import ScraperExceptions as SE

# TODO: make generic validators language agnostic. 

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
            raise SE.InvalidJsonFormat('JSON is missing the "scraper" key...')
        if 'orgs' not in data:
            raise SE.InvalidJsonFormat('JSON is missing the "orgs" key...')
        scraper = data['scraper']
        if not isinstance(scraper, str):
            raise SE.InvalidJsonFormat('The JSON "scraper" value must be a string.')
        if scraper == 'BaseScraper':
            raise SE.InvalidJsonFormat('The value "BaseScraper" is not a valid scraper.')
        GenericValidators.validate_file_exists(f'scrapers/{scraper}.py')
        if not isinstance(data['orgs'], dict):
            raise SE.InvalidJsonFormat('The JSON "orgs" value must be a dictionary.')
    @staticmethod
    def validate_name(name: str):
        ''' Purpose: Validates the given name. '''
        name_pattern = re.compile(r'^[a-zA-Z0-9\s\-.,()]+$')
        if not name_pattern.match(name):
            raise SE.InvalidJsonFormat(f'JSON contains invalid name format: {name}')
    @staticmethod
    def validate_data_bounds(data_bounds: Dict[str, int], texts: List[List]):
        ''' Purpose: Validates if the data is within list bounds. '''
        if not (data_bounds['start_idx'] >= 0 and data_bounds['end_idx'] < len(texts)):
            raise SE.UnexpectedData(f'Expected data block goes out of bounds:\n{texts}')
    @staticmethod
    def validate_review_count(actual_reviews: int, expected_reviews: int):
        ''' Purpose: Validates if number scraped reviews matches expected number. '''
        if actual_reviews != expected_reviews:
            raise SE.UnexpectedData(f'Expected {expected_reviews}, got {actual_reviews}...')
