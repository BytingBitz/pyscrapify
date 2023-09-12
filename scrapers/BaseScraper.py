''' Created: 10/09/2023 '''

# External Dependencies
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from bs4 import BeautifulSoup
import re, json, os
from abc import ABC, abstractmethod
from typing import List, Dict
from abc import ABC, abstractmethod

# Internal Dependencies
from utilities.exception_handler import ScraperExceptions as SE

class BaseValidators(ABC):
    ''' Base class for scraper-specific validators. '''
    url_pattern: str  # To be overridden in scraper-specific subclasses
    @classmethod
    def validate_url(cls, url: str) -> None:
        if cls.url_pattern is None:
            raise NotImplementedError('URL pattern not set for this scraper.')
        if not re.compile(cls.url_pattern).match(url):
            raise SE.InvalidJsonFormat(f'JSON contains invalid URL format: {url}')
    @staticmethod
    @abstractmethod
    def validate_data_block(block: List) -> None:
        ''' Purpose: Validates the given data block. '''

class BaseParsers(ABC):
    @staticmethod
    @abstractmethod
    def extract_total_reviews(driver: WebDriver) -> int:
        ''' Returns: Total number of reviews for a particular organisation. '''
    @staticmethod
    @abstractmethod
    def extract_page_text(soup: BeautifulSoup) -> List[str]:
        ''' Returns: List of review element text extracted from page soup. '''
    @staticmethod
    @abstractmethod
    def extract_data_indices(texts: List[List[str]]) -> List[int]:
        ''' Returns: List of indices of relevant review data blocks in list. '''
    @staticmethod
    @abstractmethod
    def extract_data_bounds(idx: int) -> Dict[str, int]:
        ''' Returns: Dict of start and end indices for relevant review data in list. '''
    @staticmethod
    @abstractmethod
    def extract_data_block(texts: List[List[str]], data_bounds: Dict[str, int]) -> List[str]:
        ''' Returns: List block of review data from a full list of text. '''

class BaseNavigators(ABC):
    @staticmethod
    @abstractmethod
    def grab_next_button(driver: WebDriver) -> WebElement:
        ''' Returns: Next review page button element. '''
    @staticmethod
    @abstractmethod
    def check_next_page(next_button: WebElement) -> bool:
        ''' Returns: Boolean True or False if there is a next review page. '''
    @staticmethod
    @abstractmethod
    def wait_for_url(driver: WebDriver) -> None:
        ''' Purpose: Waits for the webpage contents to load. '''
    @staticmethod
    @abstractmethod
    def wait_for_page(driver: WebDriver) -> None:
        ''' Waits for the review contents of the page to update. '''

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
