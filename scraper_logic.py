''' Created: 09/09/2023 '''

# External Dependencies
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import List

# Internal Dependencies
from scrapers.BaseScraper import GenericValidators
from utilities.exception_handler import ScraperExceptions as SE
from utilities.selenium_handler import BrowserManager
from utilities.config_handler import ScrapeConfig
from utilities.logger_handler import Log

def extract_data(page_html: str, config: ScrapeConfig) -> List[List[str]]:
    ''' Returns: List of lists of all reviews data scraped for current page.'''
    soup = BeautifulSoup(page_html, 'html.parser')
    texts = config.scraper.Parsers.extract_page_text(soup)
    indices = config.scraper.Parsers.extract_data_indices(texts)
    data_lists = []
    for idx in indices:
        data_bounds = config.scraper.Parsers.extract_data_bounds(idx)
        SE.handle_bad_data(GenericValidators.validate_data_bounds, config.data_strict, data_bounds, texts)
        data_block = config.scraper.Parsers.extract_data_block(texts, data_bounds)
        SE.handle_bad_data(config.scraper.Validators.validate_data_block, config.data_strict, data_block)
        data_lists.append(data_block)
    return data_lists

def scrape_data(driver: WebDriver, config: ScrapeConfig) -> List[List[str]]:
    ''' Returns: List of lists of all reviews data blocks scraped for current URL. '''
    pbar = tqdm(total=0)
    review_data = []
    while True:
        page_html = driver.page_source
        review_data.extend(extract_data(page_html, config))
        next_button = config.scraper.Navigators.grab_next_button(driver)
        if config.scraper.Navigators.check_next_page(next_button):
            pbar.update(1)
            next_button.click()
            SE.handle_bad_data(config.scraper.Navigators.wait_for_page, config.data_strict, driver)
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
            config.scraper.Navigators.wait_for_url(driver)
            review_data = scrape_data(driver, config)
            total_reviews = SE.handle_non_critical(config.scraper.Parsers.extract_total_reviews, config.data_strict, driver)
            SE.handle_bad_data(GenericValidators.validate_review_count, config.data_strict, len(review_data), total_reviews)
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
    except KeyboardInterrupt: # TODO: Fix
        Log.alert('Keyboard interrupt, aborting...')
    except ConnectionError:
        Log.alert('Internet connection failed, check internet and try again...')
    except (FileNotFoundError, SE.InvalidJsonFormat, SE.UnexpectedData, SE.BadScraper) as e:
        Log.alert(f'{e.args[0]}\n{config.scraper} scraper')
        Log.trace(e.__traceback__)
    except Exception as e:
        Log.error(f'Unexpected error, {config.scraper}, if persists open issue...\n{e}')
        Log.trace(e.__traceback__)

if __name__ == '__main__':
    Log.info('Debug test...')
    scrape_launch('scrape_configs/test.json', selenium_header=True)
