''' Created: 10/09/2023 '''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from utility import Log, InvalidJsonFormat, UnexpectedData, WEBDRIVER_TIMEOUT
import re

class Constants:
    ''' Purpose: Stores commonly used scraper specific constants. '''
    url_pattern = re.compile(r'https?://www\.seek\.com\.au/companies/.+/reviews')
    name_pattern = re.compile(r'^[a-zA-Z0-9\s\-.,()]+$')
    year_pattern = re.compile(r"\d{4}")
    data_start_offset, data_length, data_year_idx, data_challenge_idx = 5, 9, 1, 7

class Validators:
    ''' Purpose: Contains all scraper validation logic. '''
    @staticmethod
    def validate_url(url: str):
        ''' Purpose: Raises exception if invalid Seek URL. '''
        if not Constants.url_pattern.match(url):
            raise InvalidJsonFormat(f'JSON contains invalid URL format: {url}')
    @staticmethod
    def validate_name(name: str):
        ''' Purpose: Raises exception if invalid organisation name. '''
        if not Constants.name_pattern.match(name):
            raise InvalidJsonFormat(f'JSON contains invalid name format: {name}')
    @staticmethod
    def validate_data_bounds(data_bounds: dict, texts: list):
        ''' Purpose: Raises exception if data appears to leave texts bounds. '''
        if not (data_bounds['start_idx'] >= 0 and data_bounds['end_idx'] < len(texts)):
            raise UnexpectedData(f'Expected data block goes out of bounds:\n{texts}')
    @staticmethod
    def validate_data_block(block: list):
        if not Constants.year_pattern.match((block[Constants.data_year_idx].split()[1])):
            raise UnexpectedData(f'Expected year at second block index:\n{block}')
        if not block[Constants.data_challenge_idx] == 'The challenges':
            raise UnexpectedData(f'Expected challenge text at second last block index:\n{block}')

class Parser:
    ''' Purpose: Stores all scraper logic for processing review data. '''
    @staticmethod
    def extract_total_reviews(driver: webdriver.Chrome):
        ''' Returns: Total number of reviews for particular organisation. '''
        total_element = driver.find_element(By.XPATH, '//strong[following-sibling::text()[contains(., "reviews sorted by")]]')
        total_str = total_element.text
        return int(total_str.strip())
    @staticmethod
    def extract_page_text(soup: BeautifulSoup) -> list:
        ''' Returns: Relevant review element text extracted from page soup. '''
        return [element.get_text() for element in soup.find_all(['span', 'h3'])]
    @staticmethod
    def extract_data_indices(texts: list):
        ''' Returns: List of indices of relevant review data in texts. '''
        return [i for i, x in enumerate(texts) if x == 'The good things']
    @staticmethod
    def extract_data_bounds(idx: int) -> dict:
        ''' Returns: Dict of start and end indexs for all relevant review data. '''
        start_idx = idx - Constants.data_start_offset
        end_idx = idx + Constants.data_length - Constants.data_start_offset
        return {"start_idx": start_idx, "end_idx": end_idx}
    @staticmethod
    def extract_data_block(texts: list, data_bounds: dict):
        ''' Returns: List block of review data from full list of text. '''
        return texts[data_bounds['start_idx']:data_bounds['end_idx']]

class Navigator:
    ''' Purposes: Stores all logic for navigating and loading webpages. '''
    @staticmethod
    def grab_next_button(driver: webdriver.Chrome):
        ''' Returns: Next review page button element. '''
        return driver.find_element(By.XPATH, '//a[@aria-label="Next"]')
    @staticmethod
    def check_next_page(next_button: webdriver.Remote._web_element_cls) -> bool:
        ''' Returns: Boolean True or False if there is a next review page. '''
        return next_button.get_attribute('tabindex') != '-1'
    @staticmethod
    def wait_for_url(driver: webdriver.Chrome):
        ''' Purpose: Waits for the webpage contents to load. '''
        wait = WebDriverWait(driver, WEBDRIVER_TIMEOUT)
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next']"))) # Seek specific
    @staticmethod
    def wait_for_next_page(driver: webdriver.Chrome, data_strict: bool):
        ''' Waits for the review contents of the page to update. '''
        old_texts = [elem.text for elem in driver.find_elements(By.TAG_NAME, 'h3')]
        def page_has_changed(driver: webdriver.Chrome) -> bool:
            try:
                current_texts = [elem.text for elem in driver.find_elements(By.TAG_NAME, 'h3')]
                return current_texts != old_texts
            except StaleElementReferenceException:
                return False
        try:
            wait = WebDriverWait(driver, WEBDRIVER_TIMEOUT)
            wait.until(page_has_changed)
        except TimeoutException:
            Log.alert(f'Potential bad data!\nPage changed but review content did not...')
            if data_strict:
                Log.warn(f'Settings on data_strict True, aborting...')
                raise UnexpectedData
            else:
                Log.warn(f'Settings on data_strict False, proceeding...')
                pass
