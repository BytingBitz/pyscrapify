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
from typing import List

# Internal Dependencies
from utilities.custom_exceptions import ScraperExceptions as SE
from scrapers.BaseScraper import BaseValidators, BaseParsers, BaseNavigators
from settings import WEBDRIVER_TIMEOUT

class Validators(BaseValidators):
    url_pattern = r'https?://www\.seek\.com\.au/companies/.+/reviews'
    @staticmethod
    def validate_data_block(block: List) -> None:
        try:
            year_pattern = re.compile(r"\d{4}")
            data_year_idx = 21
            if not year_pattern.match((block[data_year_idx].split()[1])):
                raise SE.UnexpectedData(f'Expected year at second block index:\n{block}')
            challenge_text = 'The challenges'
            data_challenge_idx = 27
            if not block[data_challenge_idx] == challenge_text:
                raise SE.UnexpectedData(f'Expected challenge text at second last block index:\n{block}')
        except (IndexError, AttributeError):
            raise SE.UnexpectedData(f'Unexpected data format encountered:\n{block}')

class Parsers(BaseParsers):
    text_pattern = r'The good things'
    text_idx = 25
    data_length = 29
    @staticmethod
    def extract_total_count(driver: WebDriver) -> int:
        total_element = driver.find_element(By.XPATH, '//strong[following-sibling::text()[contains(., "reviews sorted by")]]')
        total_str = total_element.text
        return int(total_str.strip())
    @staticmethod
    def extract_page_text(soup: BeautifulSoup) -> List[str]:
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

class Navigators(BaseNavigators):
    @staticmethod
    def grab_next_button(driver: WebDriver) -> WebElement:
        return driver.find_element(By.XPATH, '//a[@aria-label="Next"]')
    @staticmethod
    def check_next_page(next_button: WebElement) -> bool:
        return next_button.get_attribute('tabindex') != '-1'
    @staticmethod
    def wait_for_entry(driver: WebDriver) -> None:
        wait = WebDriverWait(driver, WEBDRIVER_TIMEOUT)
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next']")))
    @staticmethod
    def wait_for_page(driver: WebDriver) -> None:
        old_texts = [elem.text for elem in driver.find_elements(By.TAG_NAME, 'h3')]
        def page_has_changed(driver: webdriver.Chrome) -> bool:
            try:
                current_texts = [elem.text for elem in driver.find_elements(By.TAG_NAME, 'h3')]
                return current_texts != old_texts
            except StaleElementReferenceException:
                return False
        wait = WebDriverWait(driver, WEBDRIVER_TIMEOUT)
        wait.until(page_has_changed)
