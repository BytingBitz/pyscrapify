''' Created: 10/09/2023 '''

# External Dependencies
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from bs4 import BeautifulSoup
import re
from typing import List, Dict

# Internal Dependencies
from utilities.exception_handler import ScraperExceptions as SE
from scrapers.BaseScraper import BaseValidators, BaseParsers, BaseNavigators
from settings import WEBDRIVER_TIMEOUT

from time import sleep
# NOTE: need to handle TypeErrors

class Validators(BaseValidators):
    ''' Purpose: Contains all scraper specific validation logic. '''
    url_pattern = r'https?://www\.seek\.com\.au/companies/.+/reviews'
    @staticmethod
    def validate_data_block(block: List) -> None:
        try:
            # Verify that URL and year meet expected formats.
            year_pattern = re.compile(r"\d{4}")
            # Expected index of data point that contains 4 digit year.
            data_year_idx = 21
            if not year_pattern.match((block[data_year_idx].split()[1])):
                raise SE.UnexpectedData(f'Expected year at second block index:\n{block}')
            # Expected challenge text strings in review data block.
            challenge_text = 'The challenges'
            # Expected index of 'The challenges' text in data block.
            data_challenge_idx = 27
            if not block[data_challenge_idx] == challenge_text:
                raise SE.UnexpectedData(f'Expected challenge text at second last block index:\n{block}')
        except (IndexError, AttributeError):
            raise SE.UnexpectedData(f'Unexpected data format encountered:\n{block}')

class Parsers(BaseParsers):
    ''' Purpose: Stores all scraper logic for processing review data. '''
    @staticmethod
    def extract_total_reviews(driver: WebDriver) -> int:
        ''' Returns: Total number of reviews for particular organisation. '''
        total_element = driver.find_element(By.XPATH, '//strong[following-sibling::text()[contains(., "reviews sorted by")]]')
        total_str = total_element.text
        return int(total_str.strip())
    @staticmethod
    def extract_page_text(soup: BeautifulSoup) -> List[str]:
        ''' Returns: List of review element text extracted from page soup. '''
        elements = soup.find_all(
        lambda tag: (tag.name in ['span', 'h3']) or 
                    (tag.name == 'div' and 'out of 5' in tag.get('aria-label', ''))
        )
        result = []
        for element in elements:
            if element.name in ['span', 'h3']:
                result.append(element.get_text())
            else:
                result.append(element['aria-label'])
        return result
    @staticmethod
    def extract_data_indices(texts: List[str]) -> List[int]:
        ''' Returns: List of indices of relevant review data blocks in list. '''
        # Expected good text strings in review data block.
        good_text = 'The good things'
        return [i for i, x in enumerate(texts) if x == good_text]
    @staticmethod
    def extract_data_bounds(idx: int) -> Dict[str, int]:
        ''' Returns: Dict of start and end indexs for relevant review data in list. '''
        # Distance of 'The good things' text index from start of data block.
        data_start_offset =  25
        # Length of list data block per set of review data.
        data_length = 29 
        start_idx = idx - data_start_offset
        end_idx = idx + data_length - data_start_offset
        return {"start_idx": start_idx, "end_idx": end_idx}
    @staticmethod
    def extract_data_block(texts: List[str], data_bounds: Dict[str, int]) -> List[str]:
        ''' Returns: List block of review data from full list of text. '''
        return texts[data_bounds['start_idx']:data_bounds['end_idx']]

class Navigators(BaseNavigators):
    ''' Purpose: Stores all logic for navigating and loading webpages. '''
    @staticmethod
    def grab_next_button(driver: WebDriver) -> WebElement:
        ''' Returns: Next review page button element. '''
        return driver.find_element(By.XPATH, '//a[@aria-label="Next"]')
    @staticmethod
    def check_next_page(next_button: WebElement) -> bool:
        ''' Returns: Boolean True or False if there is a next review page. '''
        return next_button.get_attribute('tabindex') != '-1'
    @staticmethod
    def wait_for_url(driver: WebDriver) -> None:
        ''' Purpose: Waits for the webpage contents to load. '''
        wait = WebDriverWait(driver, WEBDRIVER_TIMEOUT)
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next']")))
    @staticmethod
    def wait_for_page(driver: WebDriver) -> None:
        ''' Waits for the review contents of the page to update. '''
        old_texts = [elem.text for elem in driver.find_elements(By.TAG_NAME, 'h3')]
        def page_has_changed(driver: webdriver.Chrome) -> bool:
            try:
                current_texts = [elem.text for elem in driver.find_elements(By.TAG_NAME, 'h3')]
                return current_texts != old_texts
            except StaleElementReferenceException:
                return False
        wait = WebDriverWait(driver, WEBDRIVER_TIMEOUT)
        wait.until(page_has_changed)
