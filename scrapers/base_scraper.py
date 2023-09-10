''' Created: 10/09/2023 '''

from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from bs4 import BeautifulSoup

class BaseScraper:
    ''' Base scraper class that all specific scraper implementations should inherit from. '''

    class Validators:
        ''' Purpose: Contains all scraper validation logic. '''
        @staticmethod
        def validate_url(url: str):
            ''' Purpose: Validates the given URL. '''
            raise NotImplementedError('validate_url method has not been implemented in the derived scraper class.')
        @staticmethod
        def validate_data_bounds(data_bounds: dict[str, int], texts: list[list]):
            ''' Purpose: Validates if the data is within list bounds. '''
            raise NotImplementedError('validate_data_bounds method has not been implemented in the derived scraper class.')
        @staticmethod
        def validate_data_block(block: list):
            ''' Purpose: Validates the given data block. '''
            raise NotImplementedError('validate_data_block method has not been implemented in the derived scraper class.')

    class Parser:
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

    class Navigator:
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
