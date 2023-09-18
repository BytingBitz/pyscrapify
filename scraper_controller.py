''' Created: 09/09/2023 '''

# External Dependencies
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup
from pprint import pformat
from tqdm import tqdm
from typing import List
from time import sleep
import csv

# Internal Dependencies
from utilities.generic_validators import GenericValidators
from utilities.scraper_builder import ScraperBuilder, Scraper
from utilities.custom_exceptions import ScraperExceptions as SE
from utilities.selenium_handler import BrowserManager
from utilities.config_builder import Config
from utilities.logger_formats import Log
from settings import OUTPUT_DIRECTORY, DUMP_RAW_DATA, RATE_LIMIT_DELAY, SELENIUM_HEADER, SELENIUM_LOGGING

# NOTE: All scraper methods originate from the scraper specified via scraper_name in
#       the configuration JSON provided to scrape_launch or inherited from BaseScraper. 

def save_data(scraper: Scraper, config: Config, data_blocks: List[List[str]]):
    ''' Purpose: Saves parsed data to a csv file output. Optionally will also dump raw
        data_blocks list of list of strings to a dump.txt file as well. '''
    if DUMP_RAW_DATA:
        with open(f'{OUTPUT_DIRECTORY}{config.output_name}.dump.txt', 'a+', encoding='utf-8', newline='') as file:
            file.write(pformat(data_blocks))
    with open(f'{OUTPUT_DIRECTORY}{config.output_name}.csv', 'a+', encoding='utf-8',newline='') as file:
        fieldnames = scraper.parsers.parse_data_block(data_blocks[0]).keys()
        writer = csv.DictWriter(file, quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
        if file.tell() == 0:
            Log.info(f'Constructed CSV fieldnames:\n{fieldnames}')
            writer.writeheader()
        for block in data_blocks:
            parsed_data = scraper.parsers.parse_data_block(block)
            if set(fieldnames) != set(parsed_data.keys()):
                raise SE.UnexpectedData('Fieldnames and parsed_data keys do not match!')
            writer.writerow(parsed_data)

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
    try:
        while True:
            page_html = driver.page_source
            review_data.extend(extract_data(page_html, scraper, config))
            next_button = scraper.navigators.grab_next_button(driver) # TODO: Fix requiring next_button, maybe no next?
            if scraper.navigators.check_next_page(next_button):
                pbar.update(1)
                next_button.click()
                SE.handle_bad_data(scraper.navigators.wait_for_page, config.data_strict, driver)
                sleep(RATE_LIMIT_DELAY)
            else:
                break
    finally:
        pbar.close()
    Log.status(f'Extracted {len(review_data)} reviews')
    return review_data

def scrape_website(driver: WebDriver, scraper: Scraper, config: Config):
    ''' Purpose: Control Selenium to extract organisation reviews across pages. '''
    for name, entry_url in config.get_orgs(): # TODO: Move to agnostic function/variable naming
        Log.status(f'Scraping {name}')
        scraper.validators.validate_url(entry_url)
        driver.get(entry_url)
        scraper.navigators.wait_for_entry(driver)
        data_blocks = scrape_data(driver, scraper, config)
        total_blocks = SE.handle_non_critical(scraper.parsers.extract_total_count, config.data_strict, driver)
        SE.handle_bad_data(GenericValidators.validate_review_count, config.data_strict, len(data_blocks), total_blocks)
        save_data(scraper, config, data_blocks)
        sleep(RATE_LIMIT_DELAY)

def scrape_launch(config_file: str, output_name: str, data_strict:bool = True, selenium_header: bool = SELENIUM_HEADER, selenium_logging: bool = SELENIUM_LOGGING):
    ''' Purpose: Manages the scraping of all pages from provided config file. '''
    try:
        config = Config(config_file, output_name, data_strict, selenium_header, selenium_logging)
        scraper = ScraperBuilder.build(f'scrapers.{config.scraper_name}')
        with BrowserManager(language=scraper.parsers.browser_lang, header=selenium_header, logging=selenium_logging) as driver:
            Log.info(f'Loaded {config_file} contents:\n{config.string()}')
            scrape_website(driver, scraper, config)
        Log.status('Scraping executed successfully')
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except (FileNotFoundError, NotImplementedError, TimeoutError, ConnectionError, SE.InvalidConfigFile, SE.UnexpectedData, SE.BadScraper) as e:
        Log.alert(f'{e.args[0]}\nScraper:{config.scraper_name} {type(e).__name__}')
        if isinstance(e, (NotImplementedError, SE.UnexpectedData, SE.BadScraper)):
            Log.trace(e.__traceback__)
    except Exception as e:
        Log.error(f'Unexpected error: could be internet...\nscraper:{config.scraper_name} {type(e).__name__}\n{e}')
        Log.trace(e.__traceback__)
        Log.dump(config)
