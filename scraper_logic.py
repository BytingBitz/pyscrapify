''' Created: 09/09/2023 '''

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from utility import Log, InvalidJsonFormat, UnexpectedData
import os
import importlib

from scrapers.base_scraper import BaseScraper

class ScrapeConfig:
    ''' Purpose: Load specified scrape_config contents. '''
    @staticmethod
    def get_scraper(name: str) -> BaseScraper:
        ''' Dynamically overrides BaseScraper with selected scraper. '''
        module = importlib.import_module(f'scrapers.{name}')
        for attr_name in dir(module):
            attr_value = getattr(module, attr_name)
            if callable(attr_value) or isinstance(attr_value, type):
                setattr(BaseScraper, attr_name, attr_value)
        return BaseScraper
    def __init__(self, json_file_path: str, data_strict: bool, selenium_header: bool, selenium_logging: bool):
        self.data_strict = data_strict
        self.selenium_header = selenium_header
        self.selenium_logging = selenium_logging
        self.Scraper = BaseScraper
        self.orgs = []
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f'{json_file_path} does not exist.')
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            if 'scraper' not in data:
                raise InvalidJsonFormat('JSON is missing the "scraper" key...')
            self.Scraper = self.get_scraper(data.get('scraper'))
            if 'orgs' not in data:
                raise InvalidJsonFormat('JSON is missing the "orgs" key...')
            for name, url in data['orgs'].items():
                self.Scraper.Validators.validate_url(url)
                self.Scraper.Validators.validate_name(name)
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

def extract_data(page_html: str, Config: ScrapeConfig) -> list[list]:
    ''' Returns: List of lists of all reviews data scraped for current page.'''
    soup = BeautifulSoup(page_html, 'html.parser')
    texts = Config.Scraper.Parser.extract_page_text(soup)
    indices = Config.Scraper.Parser.extract_data_indices(texts)
    data_list = []
    for idx in indices:
        try:
            data_bounds = Config.Scraper.Parser.extract_data_bounds(idx)
            Config.Scraper.Validators.validate_data_bounds(data_bounds, texts)
            data_block = Config.Scraper.Parser.extract_data_block(texts, data_bounds)
            Config.Scraper.Validators.validate_data_block(data_block)
            data_list.append(data_block)
        except UnexpectedData as e:
            Log.alert(f'Potential bad data!\n{e.args[0]}')
            if Config.data_strict:
                Log.warn(f'Settings on data_strict True, aborting...')
                raise UnexpectedData
            else:
                Log.warn(f'Settings on data_strict False, proceeding...')
                pass
    return data_list

def scrape_data(driver: webdriver.Chrome, Config: ScrapeConfig) -> list[list]:
    ''' Returns: List of lists of all reviews data blocks scraped for current URL. '''
    pbar = tqdm(total=0)
    review_data = []
    while True:
        page_html = driver.page_source
        review_data.extend(extract_data(page_html, Config))
        next_button = Config.Scraper.Navigator.grab_next_button(driver)
        if Config.Scraper.Navigator.check_next_page(next_button):
            pbar.update(1)
            next_button.click()
            Config.Scraper.Navigator.wait_for_next_page(driver, Config.data_strict)
        else:
            pbar.close()
            break
    Log.status(f'Extracted {len(review_data)} reviews')
    return review_data

def scrape_website(driver: webdriver.Chrome, Config: ScrapeConfig):
    ''' Purpose: Control Selenium to extract organisation reviews across pages. '''
    failed = []
    for name, url in Config.get_orgs():
        Log.status(f'Scraping {name}')
        try:
            driver.get(url)
            Config.Scraper.Navigator.wait_for_url(driver)
            review_data = scrape_data(driver, Config)
            total_reviews = Config.Scraper.Parser.extract_total_reviews(driver)
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
        Config = ScrapeConfig(scrape_file, data_strict, selenium_header, selenium_logging)
        with BrowserManager(header=selenium_header, logging=selenium_logging) as driver:
            Log.info(f'Loaded {scrape_file} contents:\n{Config.string()}')
            scrape_website(driver, Config)
        Log.status('Scraping executed successfully')
    except KeyboardInterrupt:
        Log.warn('Keyboard interrupt, aborting...')
    except ConnectionError:
        Log.alert('Internet connection failed, check internet and try again...')
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
