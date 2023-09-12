''' Created: 11/09/2023 '''

# Stores ScrapeConfig, class that builds all custom configuration for scraping.

# External Dependencies
import json
from typing import List

# Internal Dependencies
from scrapers.BaseScraper import GenericValidators
from utilities.scraper_builder import ScraperBuilder

class ScrapeConfig:
    ''' Purpose: Load specified scrape_config contents. '''
    def __init__(self, json_file_path: str, data_strict: bool, selenium_header: bool, selenium_logging: bool):
        self.data_strict = data_strict
        self.selenium_header = selenium_header
        self.selenium_logging = selenium_logging
        self.orgs = []
        GenericValidators.validate_file_exists(json_file_path)
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            # Dynamically build the scraper class based on the name provided
            scraper_name = data.get('scraper')
            self.scraper = ScraperBuilder.build(f'scrapers.{scraper_name}')
            GenericValidators.validate_json_structure(data)
            for name, url in data['orgs'].items():
                self.scraper.validators.validate_url(url)
                GenericValidators.validate_name(name)
                self.orgs.append({'name': name, 'url': url})
    def get_orgs(self) -> List:
        ''' Returns: List of organisation names and URLs. '''
        return [(org['name'], org['url']) for org in self.orgs]
    def string(self) -> str:
        ''' Returns: String of organisation names and URLs. '''
        return '\n'.join([f'{org["name"]}: {org["url"]}' for org in self.orgs])
