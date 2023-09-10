''' Created: 09/09/2023 '''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from utility import Log
import re
from contextlib import contextmanager
import os

URL_PATTERN = re.compile(r'https?://www\.seek\.com\.au/companies/.+/reviews')
NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-.,()]+$')
YEAR_PATTERN = re.compile(r"\d{4}")

WEBDRIVER_TIMEOUT = 20
DATA_START_OFFSET = 5
DATA_LENGTH = 9
DATA_YEAR_IDX = 1
DATA_GOOD_TEXT = 'The good things'
DATA_CHALLENGE_TEXT = 'The challenges'
DATA_CHALLENGE_IDX = 7

class InvalidJsonFormat(Exception):
    pass

class UnexpectedData(Exception):
    pass

def create_browser(header: bool = False, logging: bool = False) -> webdriver:
    ''' Returns: Created Selenium Chrome browser session. '''
    options = webdriver.ChromeOptions()
    if not header:
        Log.info('Running Selenium driver without header...')
        options.add_argument('--headless')
    if not logging:
        Log.info('Disabled Selenium driver logging...')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=options)
    return driver

@contextmanager
def managed_browser(header: bool = False, logging: bool = False) -> webdriver:
    driver = create_browser(header, logging)
    try:
        yield driver
    finally:
        Log.status('Ending Selenium driver...')
        driver.quit()

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
                if not URL_PATTERN.match(url):
                    raise InvalidJsonFormat(f'JSON contains invalid URL format: {url}')
                if not NAME_PATTERN.match(name):
                    raise InvalidJsonFormat(f'JSON contains invalid name format: {name}')
                self.orgs.append({'name': name, 'url': url})
    def get_orgs(self) -> list:
        ''' Returns: List of organisation names and URLs. '''
        return [(org['name'], org['url']) for org in self.orgs]
    def string(self) -> str:
        ''' Returns: String of organisation names and URLs. '''
        return '\n'.join([f'{org["name"]}: {org["url"]}' for org in self.orgs])

def extract_data(page_html: str, data_strict: bool) -> list:
    ''' Returns: List of lists of all reviews data scraped for current page.'''
    soup = BeautifulSoup(page_html, 'html.parser')
    texts = [element.get_text() for element in soup.find_all(['span', 'h3'])]
    data = []
    # Finds 'The good things' in all texts then extracts from each index.
    indices = [i for i, x in enumerate(texts) if x == DATA_GOOD_TEXT]
    # Expect: ['position', 'month year', 'location', 'time in role, employee status', 'title', 'The good things', 'pros', 'The challenges', 'cons']
    for idx in indices:
        try:
            start_idx = idx - DATA_START_OFFSET
            end_idx = idx + DATA_LENGTH - DATA_START_OFFSET
            if not (start_idx >= 0 and end_idx < len(texts)):
                raise UnexpectedData(f'Expected data block goes out of bounds:\n{texts}')
            block = texts[start_idx:end_idx]
            if not YEAR_PATTERN.match((block[DATA_YEAR_IDX].split()[1])):
                raise UnexpectedData(f'Expected year at second block index:\n{block}')
            if not block[DATA_CHALLENGE_IDX + 1] == DATA_CHALLENGE_TEXT:
                raise UnexpectedData(f'Expected challenge text at second last block index:\n{block}')
            data.append(block)
        except UnexpectedData as e:
            Log.alert(f'Potential bad data!\n{e.args[0]}')
            if data_strict:
                Log.warn(f'Settings on data_strict True, aborting...')
                raise UnexpectedData
            else:
                Log.warn(f'Settings on data_strict False, proceeding...')
                pass
    return data

def next_page(next_button: webdriver.Remote._web_element_cls) -> bool:
    ''' Returns: Boolean True or False if next page is accessible. '''
    return next_button.get_attribute("tabindex") != "-1"

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
        current_texts = [elem.text for elem in driver.find_elements(*self.locator)]
        return current_texts != self.old_texts
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
    ''' Returns: List of lists of all reviews data scraped for current URL. '''
    pbar = tqdm(total=0)
    review_data = []
    while True:
        page_html = driver.page_source
        review_data.extend(extract_data(page_html, data_strict))
        next_button = driver.find_element(By.XPATH, "//a[@aria-label='Next']")
        if next_page(next_button):
            pbar.update(1)
            with wait_for_change(driver, data_strict, (By.TAG_NAME, 'h3')):
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
            wait.until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next']")))
            review_data = scrape_data(driver, data_strict)
            review_element = driver.find_element(By.XPATH, f"//a[contains(@href, '{url.split('/')[-2]}')]")
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
    ''' Purpose: Creates driver and data objects for scraping. '''
    try:
        with managed_browser(header=selenium_header, logging=selenium_logging) as driver:
            config_json = Config_JSON(scrape_file)
            Log.info(f'Loaded {scrape_file} contents:\n{config_json.string()}')
            scrape_seek(driver, config_json, data_strict)
    except KeyboardInterrupt:
        Log.warn('Keyboard interrupt, aborting...')
    except (FileNotFoundError, InvalidJsonFormat) as e:
        Log.alert(f'{e.args[0]}\nFailed to load {scrape_file}, aborting...')
    except UnexpectedData as e:
        Log.trace(e.__traceback__)
    except Exception as e:
        Log.alert(f'Unexpected error occurred...\n{e}')
        Log.trace(e.__traceback__)

if __name__ == '__main__':
    Log.info('Debug test...')
    scrape_launch('scrape_configs/test.json', selenium_header=True)
