''' Created: 09/09/2023 '''

# External Dependencies
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
from tqdm import tqdm

# Internal Dependencies
from utilities.handle_exceptions import ScraperExceptions as SE
from utilities.load_config import ScrapeConfig
from utilities.logging import Log

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

def extract_data(page_html: str, config: ScrapeConfig) -> list[list]:
    ''' Returns: List of lists of all reviews data scraped for current page.'''
    soup = BeautifulSoup(page_html, 'html.parser')
    texts = config.Scraper.parsers.extract_page_text(soup)
    indices = config.Scraper.parsers.extract_data_indices(texts)
    data_lists = []
    for idx in indices:
        data_bounds = config.Scraper.parsers.extract_data_bounds(idx)
        SE.handle_bad_data(config.Scraper.GenericValidators.validate_data_bounds, config.data_strict, data_bounds, texts)
        data_block = config.Scraper.parsers.extract_data_block(texts, data_bounds)
        SE.handle_bad_data(config.Scraper.validators.validate_data_block, config.data_strict, data_block)
        data_lists.append(data_block)
    return data_lists

def scrape_data(driver: WebDriver, config: ScrapeConfig) -> list[list]:
    ''' Returns: List of lists of all reviews data blocks scraped for current URL. '''
    pbar = tqdm(total=0)
    review_data = []
    while True:
        page_html = driver.page_source
        review_data.extend(extract_data(page_html, config))
        next_button = config.Scraper.navigators.grab_next_button(driver)
        if config.Scraper.navigators.check_next_page(next_button):
            pbar.update(1)
            next_button.click()
            SE.handle_bad_data(config.Scraper.navigators.wait_for_next_page, config.data_strict, driver)
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
            config.Scraper.navigators.wait_for_url(driver)
            review_data = scrape_data(driver, config)
            total_reviews = SE.handle_non_critical(config.Scraper.parsers.extract_total_reviews, config.data_strict, driver)
            SE.handle_bad_data(config.Scraper.GenericValidators.validate_review_count, config.data_strict, len(review_data), total_reviews)
            # TODO: add code to save data, use Failed lists
        except TimeoutException:
            Log.alert(f'Failed to get {name}, check URL or internet...\n{url}')
            failed.append(name)
            continue

def scrape_launch(scrape_file: str, data_strict:bool = True, selenium_header: bool = False, selenium_logging: bool = False):
    ''' Purpose: Manages the scraping of all pages from provided config file. '''
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
    except (FileNotFoundError, SE.InvalidJsonFormat, SE.UnexpectedData, NotImplementedError) as e:
        Log.alert(f'{e.args[0]}, {config.Scraper} scraper')
        Log.trace(e.__traceback__)
    except Exception as e:
        Log.error(f'Unexpected error, {config.Scraper}, if persists open issue...\n{e}')
        Log.trace(e.__traceback__)

if __name__ == '__main__':
    Log.info('Debug test...')
    scrape_launch('scrape_configs/test.json', selenium_header=True)
