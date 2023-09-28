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
from typing import List, Dict, Union

# Internal Dependencies
from utilities.custom_exceptions import ScraperExceptions as SE
from scrapers.BaseScraper import BaseValidators, BaseParsers, BaseNavigators
from settings import SELENIUM_TIMEOUT

class Validators(BaseValidators):

    url_pattern = r'https?://www\.seek\.com\.au/companies/.+/reviews'

    def validate_data_block(self, block: List) -> None:
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

    browser_lang = 'en-AU'
    text_pattern = r'^The good things$'
    text_idx = 25
    data_length = 29

    def extract_total_count(self, driver: WebDriver) -> int:
        total_element = driver.find_element(By.XPATH, '//strong[following-sibling::text()[contains(., "reviews sorted by")]]')
        total_str = total_element.text
        return int(total_str.strip())
    
    def extract_page_text(self, soup: BeautifulSoup) -> List[str]:
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
    
    def parse_data_block(self, block: List[str]) -> Dict[str, Union[int, str]]:
        def parse_location(location: str):
            state_mappings = {
                'VIC': ['VIC', 'Victoria'],
                'NSW': ['NSW', 'New South Wales'],
                'QLD': ['QLD', 'Queensland'],
                'SA': ['SA', 'South Australia'],
                'WA': ['WA', 'Western Australia'],
                'TAS': ['TAS', 'Tasmania'],
                'NT': ['NT', 'Northern Territory'],
                'ACT': ['ACT', 'Australian Capital Territory']
            }
            for key in state_mappings:
                state_mappings[key].extend([name.lower() for name in state_mappings[key]])
            postcode_match = re.search(r'(\s|^)(\d{4})$', location)
            postcode = postcode_match.group(2) if postcode_match else ''
            states_found = []
            for key, names in state_mappings.items():
                for name in names:
                    if name in location:
                        # Check for the exact word or the abbreviation bounded by non-word characters or start/end of string
                        if re.search(r'\b' + re.escape(name) + r'\b', location):
                            states_found.append(key)
                            break
            return location, ', '.join(states_found), postcode
        def parse_years_in_role(role_str: str) -> str:
            if 'Less than 1' in role_str:
                return '<1'
            elif 'More than 12' in role_str: 
                return '>12'
            elif 'to' in role_str:
                return role_str.split(' ')[0] + '-' + role_str.split(' ')[2]
            else:
                return ''
        ratings = [
            ('overall_rating', 0),
            ('benefits_perks_rating', 'Benefits & perks'),
            ('career_development_rating', 'Career development'),
            ('work_life_balance_rating', 'Work-life balance'),
            ('working_environment_rating', 'Working environment'),
            ('management_rating', 'Management'),
            ('diversity_equal_opportunity_rating', 'Diversity & equal opportunity')
        ]
        location_data = parse_location(block[-7])
        parsed_data = {key: int(block[block.index(val)+2][0] if isinstance(val, str) else block[val][0]) for key, val in ratings}
        parsed_data.update({
            'job_role': block[-9],
            'review_month': block[-8].split()[0],
            'review_year': int(block[-8].split()[1]),
            'review_location': location_data[0],
            'review_states': location_data[1],
            'review_postcode': location_data[2],
            'years_in_role': parse_years_in_role(block[-6]),
            'employment_status': 'Former' if 'former' in block[-6].lower() else 'Current' if 'current' in block[-6].lower() else '',
            'review_title': block[-5],
            'review_pros': block[-3],
            'review_cons': block[-1],
        })
        return parsed_data

class Navigators(BaseNavigators):

    @classmethod
    def grab_next_button(self, driver: WebDriver) -> WebElement:
        return driver.find_element(By.XPATH, '//a[@aria-label="Next"]')
    
    def check_next_page(self, driver: WebDriver) -> bool:
        next_button = self.grab_next_button(driver)
        return next_button.get_attribute('tabindex') != '-1'
    
    def grab_next_page(self, driver: WebDriver) -> bool:
        next_button = self.grab_next_button(driver)
        next_button.click()
        
    def wait_for_entry(self, driver: WebDriver) -> None:
        wait = WebDriverWait(driver, SELENIUM_TIMEOUT)
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next']")))

    def wait_for_page(self, driver: WebDriver) -> None:
        old_texts = [elem.text for elem in driver.find_elements(By.TAG_NAME, 'h3')]
        def page_has_changed(driver: webdriver.Chrome) -> bool:
            try:
                current_texts = [elem.text for elem in driver.find_elements(By.TAG_NAME, 'h3')]
                return current_texts != old_texts
            except StaleElementReferenceException:
                return False
        wait = WebDriverWait(driver, SELENIUM_TIMEOUT)
        wait.until(page_has_changed)
