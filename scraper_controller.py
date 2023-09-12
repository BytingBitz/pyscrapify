''' Created: 09/09/2023 '''

# External Dependencies
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import List

# Internal Dependencies
from scrapers.BaseScraper import GenericValidators
from utilities.scraper_builder import ScraperBuilder, Scraper
from utilities.exception_handler import ScraperExceptions as SE
from utilities.selenium_handler import BrowserManager
from utilities.config_builder import Config
from utilities.logger_formats import Log

# NOTE: All scraper methods originate from the scraper specified via scraper_name in
#       the configuration JSON provided to scrape_launch or inherited from BaseScraper. 

def extract_data(page_html: str, scraper: Scraper, config: Config) -> List[List[str]]:
    ''' Returns: List of data blocks for page. This function transforms a page_html 
        into a list of text which should contain desired data. From here it creates 
        a list of locations of desired data blocks within this. For each location 
        it then builds data bounds and extracts that block of data to a list of 
        data blocks, where a data block is a list of strings of desired data. '''
    soup = BeautifulSoup(page_html, 'html.parser')
    texts = scraper.parsers.extract_page_text(soup)
    indices = scraper.parsers.extract_data_indices(texts)
    data_lists = []
    for idx in indices:
        data_bounds = scraper.parsers.extract_data_bounds(idx)
        SE.handle_bad_data(GenericValidators.validate_data_bounds, config.data_strict, data_bounds, texts)
        data_block = scraper.parsers.extract_data_block(texts, data_bounds)
        SE.handle_bad_data(scraper.validators.validate_data_block, config.data_strict, data_block)
        data_lists.append(data_block)
    return data_lists

def scrape_data(driver: WebDriver, scraper: Scraper, config: Config) -> List[List[str]]:
    ''' Returns: List of data blocks for entry_url. '''
    pbar = tqdm(total=0)
    review_data = []
    while True:
        page_html = driver.page_source
        review_data.extend(extract_data(page_html, scraper, config))
        next_button = scraper.navigators.grab_next_button(driver) # TODO: Fix requiring next_button, maybe no next?
        if scraper.navigators.check_next_page(next_button):
            pbar.update(1)
            next_button.click()
            SE.handle_bad_data(scraper.navigators.wait_for_page, config.data_strict, driver)
        else:
            pbar.close()
            break
    Log.status(f'Extracted {len(review_data)} reviews')
    return review_data

def scrape_website(driver: WebDriver, scraper: Scraper, config: Config):
    ''' Purpose: Control Selenium to extract organisation reviews across pages. '''
    failed = []
    for name, entry_url in config.get_orgs(): # TODO: Move to agnostic function/variable naming
        Log.status(f'Scraping {name}')
        scraper.validators.validate_url(entry_url)
        try:
            driver.get(entry_url)
            scraper.navigators.wait_for_url(driver)
            review_data = scrape_data(driver, scraper, config)
            total_reviews = SE.handle_non_critical(scraper.parsers.extract_total_reviews, config.data_strict, driver)
            SE.handle_bad_data(GenericValidators.validate_review_count, config.data_strict, len(review_data), total_reviews)
            # TODO: add code to save data, use Failed lists
        except TimeoutException:
            Log.alert(f'Failed to get {name}, check URL or internet...\n{entry_url}')
            failed.append(name)
            continue

def scrape_launch(scrape_file: str, data_strict:bool = True, selenium_header: bool = False, selenium_logging: bool = False):
    ''' Purpose: Manages the scraping of all pages from provided config file. '''
    try:
        config = Config(scrape_file, data_strict, selenium_header, selenium_logging)
        scraper = ScraperBuilder.build(f'scrapers.{config.scraper_name}')
        with BrowserManager(header=selenium_header, logging=selenium_logging) as driver:
            Log.info(f'Loaded {scrape_file} contents:\n{config.string()}')
            scrape_website(driver, scraper, config)
        Log.status('Scraping executed successfully')
    except KeyboardInterrupt: # TODO: Fix
        Log.alert('Keyboard interrupt, aborting...')
    except ConnectionError:
        Log.alert('Internet connection failed, check internet and try again...')
    except (FileNotFoundError, SE.InvalidJsonFormat, SE.UnexpectedData, SE.BadScraper) as e:
        Log.alert(f'{e.args[0]}\n{config.scraper_name} scraper')
        Log.trace(e.__traceback__)
    except Exception as e:
        Log.error(f'Unexpected error, {config.scraper_name}, if persists open issue...\n{e}')
        Log.trace(e.__traceback__)

if __name__ == '__main__':
    Log.info('Debug test...')
    scrape_launch('scrape_configs/test.json', selenium_header=True)
