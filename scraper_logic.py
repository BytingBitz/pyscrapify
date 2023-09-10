''' Created: 09/09/2023 '''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from utility import Log, InvalidJsonFormat, UnexpectedData
import re
import os

WEBDRIVER_TIMEOUT = 20
DATA_START_OFFSET = 5 # Seek specific
DATA_LENGTH = 9 # Seek specific
DATA_YEAR_IDX = 1 # Seek specific
DATA_GOOD_TEXT = 'The good things' # Seek specific
DATA_CHALLENGE_TEXT = 'The challenges' # Seek specific
DATA_CHALLENGE_IDX = 7 # Seek specific

class SeekConstants:
    ''' Purpose: Stores commonly used Seek specific constants. '''
    url_pattern = re.compile(r'https?://www\.seek\.com\.au/companies/.+/reviews')
    name_pattern = re.compile(r'^[a-zA-Z0-9\s\-.,()]+$')
    year_pattern = re.compile(r"\d{4}")
    data_start_offset, data_length, data_year_idx, data_challenge_idx = 5, 9, 1, 7
    data_good_text, data_challenge_text = 'The good things', 'The challenges'

class SeekValidators:
    ''' Purpose: Contains all Seek specific validation logic. '''
    @staticmethod
    def validate_url(url: str):
        ''' Purpose: Raises exception if invalid Seek URL. '''
        if not SeekConstants.url_pattern.match(url):
            raise InvalidJsonFormat(f'JSON contains invalid URL format: {url}')
    @staticmethod
    def validate_name(name: str):
        ''' Purpose: Raises exception if invalid organisation name. '''
        if not SeekConstants.name_pattern.match(name):
            raise InvalidJsonFormat(f'JSON contains invalid name format: {name}')
    @staticmethod
    def validate_data_bounds(data_bounds: dict, texts: list):
        ''' Purpose: Raises exception if data appears to leave texts bounds. '''
        if not (data_bounds['start_idx'] >= 0 and data_bounds['end_idx'] < len(texts)):
            raise UnexpectedData(f'Expected data block goes out of bounds:\n{texts}')
    @staticmethod
    def validate_data_block(block: list):
        if not SeekConstants.year_pattern.match((block[SeekConstants.data_year_idx].split()[1])):
            raise UnexpectedData(f'Expected year at second block index:\n{block}')
        if not block[SeekConstants.data_challenge_idx] == SeekConstants.data_challenge_text:
            raise UnexpectedData(f'Expected challenge text at second last block index:\n{block}')

class SeekParser:
    ''' Purpose: Stores all logic for processing Seek review data. '''
    @staticmethod
    def extract_page_text(soup: BeautifulSoup) -> list:
        ''' Returns: Relevant review element text extracted from page soup. '''
        return [element.get_text() for element in soup.find_all(['span', 'h3'])]
    @staticmethod
    def extract_data_indices(texts: list):
        ''' Returns: List of indices of relevant review data in texts. '''
        return [i for i, x in enumerate(texts) if x == DATA_GOOD_TEXT]
    @staticmethod
    def extract_data_bounds(idx: int) -> dict:
        ''' Returns: Dict of start and end indexs for all relevant review data. '''
        start_idx = idx - SeekConstants.data_start_offset
        end_idx = idx + SeekConstants.data_length - SeekConstants.data_start_offset
        return {"start_idx": start_idx, "end_idx": end_idx}
    @staticmethod
    def extract_data_block(texts: list, data_bounds: dict):
        ''' Returns: List block of review data from full list of text. '''
        return texts[data_bounds['start_idx']:data_bounds['end_idx']]

class SeekNavigator:
    ''' Purposes: Stores all logic for navigating and loading Seek webpages. '''
    def grab_next_button(driver: webdriver.Chrome):
        ''' Returns: Next review page button element. '''
        return driver.find_element(By.XPATH, '//a[@aria-label="Next"]')
    def check_next_page(next_button: webdriver.Remote._web_element_cls) -> bool:
        ''' Returns: Boolean True or False if there is a next review page. '''
        return next_button.get_attribute("tabindex") != "-1" # Seek specific

class Config_JSON:
    ''' Purpose: Load specified scrape_config contents. '''
    def __init__(self, json_file_path):
        self.orgs = []
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f'{json_file_path} does not exist.')
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            if 'orgs' not in data:
                raise InvalidJsonFormat('JSON is missing the "orgs" key...')
            for name, url in data['orgs'].items():
                SeekValidators.validate_url(url)
                SeekValidators.validate_name(name)
                self.orgs.append({'name': name, 'url': url})
    def get_orgs(self) -> list:
        ''' Returns: List of organisation names and URLs. '''
        return [(org['name'], org['url']) for org in self.orgs]
    def string(self) -> str:
        ''' Returns: String of organisation names and URLs. '''
        return '\n'.join([f'{org["name"]}: {org["url"]}' for org in self.orgs])

class BrowserManager:
    def __init__(self, header: bool = False, logging: bool = False):
        self.header = header
        self.logging = logging
    def create_browser(self) -> webdriver:
        ''' Returns: Created Selenium Chrome browser session. '''
        options = webdriver.ChromeOptions()
        if not self.header:
            Log.info('Running Selenium driver without header...')
            options.add_argument('--headless')
        if not self.logging:
            Log.info('Disabled Selenium driver logging...')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options)
        return driver
    def __enter__(self):
        self.driver = self.create_browser()
        return self.driver
    def __exit__(self, *_):
        Log.info('Ending Selenium driver...')
        self.driver.quit()

def extract_data(page_html: str, data_strict: bool) -> list:
    ''' Returns: List of lists of all reviews data scraped for current page.'''
    soup = BeautifulSoup(page_html, 'html.parser')
    texts = SeekParser.extract_page_text(soup)
    indices = SeekParser.extract_data_indices(texts)
    data_list = []
    for idx in indices:
        try:
            data_bounds = SeekParser.extract_data_bounds(idx)
            SeekValidators.validate_data_bounds(data_bounds, texts)
            data_block = SeekParser.extract_data_block(texts, data_bounds)
            SeekValidators.validate_data_block(data_block)
            data_list.append(data_block)
        except UnexpectedData as e:
            Log.alert(f'Potential bad data!\n{e.args[0]}')
            if data_strict:
                Log.warn(f'Settings on data_strict True, aborting...')
                raise UnexpectedData
            else:
                Log.warn(f'Settings on data_strict False, proceeding...')
                pass
    return data_list

class wait_for_change(object):
    ''' Purpose: Verifies new reviews have loaded by span text changes. '''
    def __init__(self, driver: webdriver.Chrome, data_strict: bool, element_locator):
        self.driver = driver
        self.locator = element_locator
        self.data_strict = data_strict
    def __enter__(self):
        self.old_texts = [elem.text for elem in self.driver.find_elements(*self.locator)]
        return self
    def content_has_changed(self, driver: webdriver.Chrome) -> bool:
        try:
            current_texts = [elem.text for elem in driver.find_elements(*self.locator)]
            return current_texts != self.old_texts
        except StaleElementReferenceException:
            return False
    def __exit__(self, *_):
        try:
            wait = WebDriverWait(self.driver, WEBDRIVER_TIMEOUT)
            wait.until(lambda driver: self.content_has_changed(driver))
        except TimeoutException:
            Log.alert(f'Potential bad data!\nPage changed but review content did not...')
            if self.data_strict:
                Log.warn(f'Settings on data_strict True, aborting...')
                raise UnexpectedData
            else:
                Log.warn(f'Settings on data_strict False, proceeding...')
                pass

def scrape_data(driver: webdriver.Chrome, data_strict: bool) -> list:
    ''' Returns: List of lists of all reviews data blocks scraped for current URL. '''
    pbar = tqdm(total=0)
    review_data = []
    while True:
        page_html = driver.page_source
        review_data.extend(extract_data(page_html, data_strict))
        next_button = SeekNavigator.grab_next_button(driver)
        if SeekNavigator.check_next_page(next_button):
            pbar.update(1)
            with wait_for_change(driver, data_strict, (By.TAG_NAME, 'h3')): # Seek specific
                next_button.click()
        else:
            pbar.close()
            break
    Log.status(f'Extracted {len(review_data)} reviews')
    return review_data

def scrape_seek(driver: webdriver.Chrome, config_json: Config_JSON, data_strict: bool):
    ''' Purpose: Control Selenium to extract organisation reviews across pages. '''
    failed = []
    for name, url in config_json.get_orgs():
        Log.status(f'Scraping {name}')
        try:
            driver.get(url)
            wait = WebDriverWait(driver, WEBDRIVER_TIMEOUT)
            wait.until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next']"))) # Seek specific
            review_data = scrape_data(driver, data_strict)
            review_element = driver.find_element(By.XPATH, f"//a[contains(@href, '{url.split('/')[-2]}')]") # Seek specific
            total_reviews = int(review_element.text.split()[0])
            if len(review_data) != total_reviews:
                Log.alert(f'Expected {total_reviews}, got {len(review_data)} for {name}, check internet...')
                failed.append(name)
                continue
            # add code to save data
        except TimeoutException:
            Log.alert(f'Failed to get {name}, check URL or internet...\n{url}')
            failed.append(name)
            continue

def scrape_launch(scrape_file: str, data_strict:bool = True, selenium_header: bool = False, selenium_logging: bool = False):
    ''' Purpose: Manages the scraping of all Seek websites from provided config file. '''
    try:
        with BrowserManager(header=selenium_header, logging=selenium_logging) as driver:
            config_json = Config_JSON(scrape_file)
            Log.info(f'Loaded {scrape_file} contents:\n{config_json.string()}')
            scrape_seek(driver, config_json, data_strict)
    except KeyboardInterrupt:
        Log.warn('Keyboard interrupt, aborting...')
    except (FileNotFoundError, InvalidJsonFormat) as e:
        Log.alert(f'{e.args[0]}\nFailed to load {scrape_file}, aborting...')
    except UnexpectedData as e:
        Log.trace(e.__traceback__) # Consider joining and generalising with above errors
    except Exception as e:
        Log.alert(f'Unexpected error occurred...\n{e}')
        Log.trace(e.__traceback__)

if __name__ == '__main__':
    Log.info('Debug test...')
    scrape_launch('scrape_configs/test.json', selenium_header=True)
