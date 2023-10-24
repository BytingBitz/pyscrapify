''' Created: 11/09/2023 '''

# Stores ScrapeConfig, class that builds all custom configuration for scraping.

# External Dependencies
import json
from typing import List

# Internal Dependencies
from utilities.generic_validators import GenericValidators

class Config:
    ''' Purpose: Load specified scrape_config contents. '''
    def __init__(self, config_file: str):
        self.orgs = []
        config_path = f'scrape_configs/{config_file}'
        GenericValidators.validate_file_exists(config_path)
        with open(config_path, 'r') as file:
            data = json.load(file)
            GenericValidators.validate_json_structure(data)
            self.scraper_name = data.get('scraper')
            seen_urls = set()
            for name, url in data['entries'].items():
                GenericValidators.validate_name(name)
                if url not in seen_urls:
                    self.orgs.append({'name': name, 'url': url})
                    seen_urls.add(url)
    def get_lines(self) -> List:
        ''' Returns: List of organisation names and URLs. '''
        return [(org['name'], org['url']) for org in self.orgs]
    def string(self) -> str:
        ''' Returns: String of organisation names and URLs. '''
        return '\n'.join([f'{org["name"]}: {org["url"]}' for org in self.orgs])
