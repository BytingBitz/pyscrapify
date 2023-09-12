''' Created: 12/09/2023 '''

# External Dependencies
import importlib
from scrapers.BaseScraper import BaseValidators, BaseParsers, BaseNavigators

# Internal Dependencies
from utilities.exception_handler import ScraperExceptions as SE

class Scraper:
    ''' Purpose: Resulting expected class returned by ScraperBuilder.build(module_name) for use. '''
    def __init__(self, validators: BaseValidators, parsers: BaseParsers, navigators: BaseNavigators):
        self.validators = validators
        self.parsers = parsers
        self.navigators = navigators

class ScraperBuilder:
    @staticmethod
    def build(module_name: str) -> Scraper:
        ''' Returns: Constructed instance of Scraper with the module_name Validators, Parsers, and Navigators.
            Builds selected scraper, which inherits additional logic from BaseScraper. '''
        module = importlib.import_module(module_name)
        required_classes = ['Validators', 'Parsers', 'Navigators']
        instances = {}
        for attr_name in required_classes:
            if not hasattr(module, attr_name):
                raise SE.BadScraper(f'Module {module_name} does not contain required scraper class {attr_name}.')
            class_ref = getattr(module, attr_name)
            instances[attr_name] = class_ref()
        return Scraper(instances['Validators'], instances['Parsers'], instances['Navigators'])
