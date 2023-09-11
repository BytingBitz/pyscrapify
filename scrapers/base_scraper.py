''' Created: 10/09/2023 '''

# External Dependencies
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from bs4 import BeautifulSoup
import importlib, re, json, os

# Internal Dependencies
from utilities.handle_exceptions import ScraperExceptions as SE

class BaseScraperModule:
    class Validators:
        ''' Purpose: Contains all scraper specific validation logic. '''
        # Expect: r'expression' to validate loaded url. 
        url_pattern: str = None
    class Navigators:
        def wait_for_url(driver: WebDriver):
            ''' Purpose: Waits for the webpage contents to load. '''
            raise NotImplementedError('wait_for_url method has not been implemented in the derived scraper class.')

class Scraper:
    ''' Base scraper class that all specific scraper implementations should inherit from. '''
    def __init__(self, scraper_name: str):
        try: # Dynamically import the scraper module
            self.Scraper = importlib.import_module(f'scrapers.{scraper_name}')
        except ImportError:
            raise NotImplementedError(f"No module named {scraper_name}")
        self.validators = self.Validators(self.Scraper)
        self.parsers = self.Parsers(self.Scraper)
        self.navigators = self.Navigators(self.Scraper)
    
    class Validators:
        ''' Purpose: Contains all scraper validation logic. '''
        def __init__(self, scraper: BaseScraperModule):
            self.scraper = scraper
        
        def validate_url(self, url: str):
            ''' Purpose: Validates URL against scraper Validators.url_pattern regex. '''
            try:
                url_pattern = self.scraper.Validators.url_pattern
            except AttributeError:
                raise NotImplementedError('validate_url method has not been implemented in the derived scraper class.')
            if not re.compile(url_pattern).match(url):
                raise SE.InvalidJsonFormat(f'JSON contains invalid URL format: {url}')
            print('I Worked!')

        @staticmethod
        def validate_data_block(block: list):
            ''' Purpose: Validates the given data block. '''
            raise NotImplementedError('validate_data_block method has not been implemented in the derived scraper class.')

    class Parsers:
        def __init__(self, scraper: BaseScraperModule):
            self.scraper = scraper

        @staticmethod
        def extract_total_reviews(driver: WebDriver) -> int:
            ''' Returns: Total number of reviews for particular organisation. '''
            raise NotImplementedError('extract_total_reviews method has not been implemented in the derived scraper class.')
        @staticmethod
        def extract_page_text(soup: BeautifulSoup) -> list[str]:
            ''' Returns: List of review element text extracted from page soup. '''
            raise NotImplementedError('extract_page_text method has not been implemented in the derived scraper class.')
        @staticmethod
        def extract_data_indices(texts: list[list]) -> list[int]:
            ''' Returns: List of indices of relevant review data blocks in list. '''
            raise NotImplementedError('extract_data_indices method has not been implemented in the derived scraper class.')
        @staticmethod
        def extract_data_bounds(idx: int) -> dict[str, int]:
            ''' Returns: Dict of start and end indexs for relevant review data in list. '''
            raise NotImplementedError('extract_data_bounds method has not been implemented in the derived scraper class.')
        @staticmethod
        def extract_data_block(texts: list[list], data_bounds: dict[str, int]) -> list[str]:
            ''' Returns: List block of review data from full list of text. '''
            raise NotImplementedError('extract_data_block method has not been implemented in the derived scraper class.')

    class Navigators:
        def __init__(self, scraper: BaseScraperModule):
            self.scraper = scraper

        @staticmethod
        def grab_next_button(driver: WebDriver) -> WebElement:
            ''' Returns: Next review page button element. '''
            raise NotImplementedError('grab_next_button method has not been implemented in the derived scraper class.')
        @staticmethod
        def check_next_page(next_button: WebElement) -> bool:
            ''' Returns: Boolean True or False if there is a next review page. '''
            raise NotImplementedError('check_next_page method has not been implemented in the derived scraper class.')
        @staticmethod
        def wait_for_url(driver: WebDriver):
            ''' Purpose: Waits for the webpage contents to load. '''
            raise NotImplementedError('wait_for_url method has not been implemented in the derived scraper class.')
        @staticmethod
        def wait_for_next_page(driver: WebDriver):
            ''' Waits for the review contents of the page to update. '''
            raise NotImplementedError('wait_for_next_page method has not been implemented in the derived scraper class.')

    class GenericValidators:
        ''' Purpose: Contains all generic validation logic. '''
        @staticmethod
        def validate_file_exists(file_path: str):
            ''' Purpose: Validates that file exists. '''
            if not os.path.exists(file_path):
                raise FileNotFoundError(f'{file_path} does not exist.')
        @staticmethod
        def validate_json_structure(data: json):
            ''' Purpose: Validates JSON file is structured as expected. '''
            if 'scraper' not in data:
                raise SE.InvalidJsonFormat('JSON is missing the "scraper" key...')
            if 'orgs' not in data:
                raise SE.InvalidJsonFormat('JSON is missing the "orgs" key...')
            scraper = data['scraper']
            if not isinstance(scraper, str):
                raise SE.InvalidJsonFormat('The JSON "scraper" value must be a string.')
            Scraper.GenericValidators.validate_file_exists(f'scrapers/{scraper}.py')
            if not isinstance(data['orgs'], dict):
                raise SE.InvalidJsonFormat('The JSON "orgs" value must be a dictionary.')
        @staticmethod
        def validate_name(name: str):
            ''' Purpose: Validates the given name. '''
            name_pattern = re.compile(r'^[a-zA-Z0-9\s\-.,()]+$')
            if not name_pattern.match(name):
                raise SE.InvalidJsonFormat(f'JSON contains invalid name format: {name}')
        @staticmethod
        def validate_data_bounds(data_bounds: dict[str, int], texts: list[list]):
            ''' Purpose: Validates if the data is within list bounds. '''
            if not (data_bounds['start_idx'] >= 0 and data_bounds['end_idx'] < len(texts)):
                raise SE.UnexpectedData(f'Expected data block goes out of bounds:\n{texts}')
        @staticmethod
        def validate_review_count(actual_reviews: int, expected_reviews: int):
            ''' Purpose: Validates if number scraped reviews matches expected number. '''
            if actual_reviews != expected_reviews:
                raise SE.UnexpectedData(f'Expected {expected_reviews}, got {actual_reviews}...')
