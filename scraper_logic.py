''' Created: 09/09/2023 '''

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
from tqdm import tqdm
from utility import Log, InvalidJsonFormat, UnexpectedData
import json, os, re
import importlib

# NOTE: All website scrapers build off of BaseScraper.
from scrapers.base_scraper import BaseScraper

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
            raise InvalidJsonFormat('JSON is missing the "scraper" key...')
        if 'orgs' not in data:
            raise InvalidJsonFormat('JSON is missing the "orgs" key...')
        scraper = data['scraper']
        if not isinstance(scraper, str):
            raise InvalidJsonFormat('The JSON "scraper" value must be a string.')
        GenericValidators.validate_file_exists(f'scrapers/{scraper}.py')
        if not isinstance(data['orgs'], dict):
            raise InvalidJsonFormat('The JSON "orgs" value must be a dictionary.')
    @staticmethod
    def validate_name(name: str):
        ''' Purpose: Validates the given name. '''
        name_pattern = re.compile(r'^[a-zA-Z0-9\s\-.,()]+$')
        if not name_pattern.match(name):
            raise InvalidJsonFormat(f'JSON contains invalid name format: {name}')
    @staticmethod
    def validate_review_count(actual_reviews: int, expected_reviews: int):
        ''' Purpose: Validates if number scraped reviews matches expected number. '''
        if actual_reviews != expected_reviews:
            raise UnexpectedData(f'Expected {expected_reviews}, got {actual_reviews}...')

def get_scraper(name: str) -> BaseScraper:
    ''' Dynamically overrides BaseScraper with selected scraper. '''
    module = importlib.import_module(f'scrapers.{name}')
    for attr_name in dir(module):
        attr_value = getattr(module, attr_name)
        if callable(attr_value) or isinstance(attr_value, type):
            setattr(BaseScraper, attr_name, attr_value)
    return BaseScraper
    # TODO: Find more effective scraper loader that cuts down on duplicate/redundant code, this is also a little hacky.

class ScrapeConfig:
    ''' Purpose: Load specified scrape_config contents. '''
    def __init__(self, json_file_path: str, data_strict: bool, selenium_header: bool, selenium_logging: bool):
        self.Scraper = BaseScraper
        self.data_strict = data_strict
        self.selenium_header = selenium_header
        self.selenium_logging = selenium_logging
        self.orgs = []
        GenericValidators.validate_file_exists(json_file_path)
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            GenericValidators.validate_json_structure(data)
            self.Scraper = get_scraper(data.get('scraper'))
            for name, url in data['orgs'].items():
                self.Scraper.Validators.validate_url(url)
                GenericValidators.validate_name(name)
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

def handle_non_critical(func, config: ScrapeConfig, *args, **kwargs):
    ''' Purpose: Handles non-critical functions given data_strict setting. '''
    try:
        return func(*args, **kwargs)
    except Exception as e:
        Log.alert(f'Failed to get value!\n{e}')
        if config.data_strict:
            raise UnexpectedData('Settings on data_strict True, aborting...')
        else:
            Log.warn(f'Settings on data_strict False, proceeding...')
            return None

def handle_bad_data(func, config: ScrapeConfig, *args, **kwargs):
    ''' Purpose: Handles bad data given data_strict setting. '''
    try:
        func(*args, **kwargs)
    except UnexpectedData as e:
        Log.alert(f'Potential bad data!\n{e.args[0]}')
        if config.data_strict:
            raise UnexpectedData('Settings on data_strict True, aborting...')
        else:
            Log.warn(f'Settings on data_strict False, proceeding...')

def extract_data(page_html: str, config: ScrapeConfig) -> list[list]:
    ''' Returns: List of lists of all reviews data scraped for current page.'''
    soup = BeautifulSoup(page_html, 'html.parser')
    texts = config.Scraper.Parser.extract_page_text(soup)
    indices = config.Scraper.Parser.extract_data_indices(texts)
    data_lists = []
    for idx in indices:
        data_bounds = config.Scraper.Parser.extract_data_bounds(idx)
        handle_bad_data(config.Scraper.Validators.validate_data_bounds, config, data_bounds, texts)
        data_block = config.Scraper.Parser.extract_data_block(texts, data_bounds)
        handle_bad_data(config.Scraper.Validators.validate_data_block, config, data_block)
        data_lists.append(data_block)
    return data_lists

def scrape_data(driver: WebDriver, config: ScrapeConfig) -> list[list]:
    ''' Returns: List of lists of all reviews data blocks scraped for current URL. '''
    pbar = tqdm(total=0)
    review_data = []
    while True:
        page_html = driver.page_source
        review_data.extend(extract_data(page_html, config))
        next_button = config.Scraper.Navigator.grab_next_button(driver)
        if config.Scraper.Navigator.check_next_page(next_button):
            pbar.update(1)
            next_button.click()
            handle_bad_data(config.Scraper.Navigator.wait_for_next_page, config, driver)
        else:
            pbar.close()
            break
    Log.status(f'Extracted {len(review_data)} reviews')
    return review_data

def scrape_website(driver: WebDriver, config: ScrapeConfig):
    ''' Purpose: Control Selenium to extract organisation reviews across pages. '''
    failed = []
    for name, url in config.get_orgs():
        Log.status(f'Scraping {name}')
        try:
            driver.get(url)
            config.Scraper.Navigator.wait_for_url(driver)
            review_data = scrape_data(driver, config)
            total_reviews = handle_non_critical(config.Scraper.Parser.extract_total_reviews, config, driver)
            handle_bad_data(GenericValidators.validate_review_count, config, len(review_data), total_reviews)
            # TODO: add code to save data, use Failed lists
        except TimeoutException:
            Log.alert(f'Failed to get {name}, check URL or internet...\n{url}')
            failed.append(name)
            continue

def scrape_launch(scrape_file: str, data_strict:bool = True, selenium_header: bool = False, selenium_logging: bool = False):
    ''' Purpose: Manages the scraping of all Seek websites from provided config file. '''
    try:
        config = ScrapeConfig(scrape_file, data_strict, selenium_header, selenium_logging)
        with BrowserManager(header=selenium_header, logging=selenium_logging) as driver:
            Log.info(f'Loaded {scrape_file} contents:\n{config.string()}')
            scrape_website(driver, config)
        Log.status('Scraping executed successfully')
    except KeyboardInterrupt:
        Log.alert('Keyboard interrupt, aborting...')
    except ConnectionError:
        Log.alert('Internet connection failed, check internet and try again...')
    except (FileNotFoundError, InvalidJsonFormat, UnexpectedData, NotImplementedError) as e:
        Log.alert(f'{e.args[0]}, {config.Scraper} scraper')
        Log.trace(e.__traceback__)
    except Exception as e:
        Log.error(f'Unexpected error, {config.Scraper}, if persists open issue...\n{e}')
        Log.trace(e.__traceback__)

if __name__ == '__main__':
    Log.info('Debug test...')
    scrape_launch('scrape_configs/test.json', selenium_header=True)
