''' Created: 10/09/2023 '''

from typing import List, Dict
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from bs4 import BeautifulSoup

class BaseScraper:
    ''' Base scraper class that all specific scraper implementations should inherit from. '''

    class Validators:
        ''' Purpose: Contains all scraper validation logic. '''
        @staticmethod
        def validate_url(url: str):
            ''' Validates the given URL. '''
            raise NotImplementedError('validate_url method has not been implemented in the derived scraper class.')
        @staticmethod
        def validate_name(name: str):
            ''' Validates the given name. '''
            raise NotImplementedError('validate_name method has not been implemented in the derived scraper class.')
        @staticmethod
        def validate_data_bounds(data_bounds: dict, texts: list):
            ''' Validates if the data is within the text bounds. '''
            raise NotImplementedError('validate_data_bounds method has not been implemented in the derived scraper class.')
        @staticmethod
        def validate_data_block(block: list):
            ''' Validates the given data block. '''
            raise NotImplementedError('validate_data_block method has not been implemented in the derived scraper class.')

    class Parser:
        @staticmethod
        def extract_total_reviews(driver: WebDriver) -> int:
            ''' Extracts the total number of reviews from the page. '''
            raise NotImplementedError('extract_total_reviews method has not been implemented in the derived scraper class.')
        @staticmethod
        def extract_page_text(soup: BeautifulSoup) -> List[str]:
            ''' Extracts the relevant review element text from the page content. '''
            raise NotImplementedError('extract_page_text method has not been implemented in the derived scraper class.')
        @staticmethod
        def extract_data_indices(texts: list) -> List[int]:
            ''' Extracts the indices of the relevant review data from the text list. '''
            raise NotImplementedError('extract_data_indices method has not been implemented in the derived scraper class.')
        @staticmethod
        def extract_data_bounds(idx: int) -> Dict[str, int]:
            ''' Extracts the bounds for the relevant review data from the text list. '''
            raise NotImplementedError('extract_data_bounds method has not been implemented in the derived scraper class.')
        @staticmethod
        def extract_data_block(texts: list, data_bounds: dict) -> List[str]:
            ''' Extracts a block of review data from the full text list. '''
            raise NotImplementedError('extract_data_block method has not been implemented in the derived scraper class.')

    class Navigator:
        @staticmethod
        def grab_next_button(driver: WebDriver) -> WebElement:
            ''' Grabs the next page button on the review page. '''
            raise NotImplementedError('grab_next_button method has not been implemented in the derived scraper class.')
        @staticmethod
        def check_next_page(next_button: WebElement) -> bool:
            ''' Checks if there's a next review page. '''
            raise NotImplementedError('check_next_page method has not been implemented in the derived scraper class.')
        @staticmethod
        def wait_for_url(driver: WebDriver):
            ''' Waits until the page has fully loaded. '''
            raise NotImplementedError('wait_for_url method has not been implemented in the derived scraper class.')
        @staticmethod
        def wait_for_next_page(driver: WebDriver, data_strict: bool):
            ''' Waits until the review contents of the next page have been loaded. '''
            raise NotImplementedError('wait_for_next_page method has not been implemented in the derived scraper class.')
