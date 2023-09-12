import importlib
from scrapers.BaseScraper import BaseValidators, BaseParsers, BaseNavigators

class Scraper:
    def __init__(self, validators: BaseValidators, parsers: BaseParsers, navigators: BaseNavigators):
        self.validators = validators
        self.parsers = parsers
        self.navigators = navigators

class ScraperBuilder:
    @staticmethod
    def build(module_name: str) -> Scraper:
        """Constructs and returns an instance of Scraper with the module's Validator, Parser, and Navigator."""
        module = importlib.import_module(module_name)

        if not hasattr(module, 'Validators') or not hasattr(module, 'Parsers') or not hasattr(module, 'Navigators'):
            raise ImportError(f"Module {module_name} does not contain required scraper classes.")

        validators = getattr(module, 'Validators')
        parsers = getattr(module, 'Parsers')
        navigators = getattr(module, 'Navigators')

        validators_instance = validators()
        parsers_instance = parsers()
        navigators_instance = navigators()

        return Scraper(validators_instance, parsers_instance, navigators_instance)
