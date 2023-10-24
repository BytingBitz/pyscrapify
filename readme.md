# PyScrapify - Basic Web Scraper Framework

***
# About:

Note: Please ensure you read and understand the disclaimer contained within this readme file prior to any use of this repository.

**PyScrapify** is a robust web scraping framework built upon Selenium and BeautifulSoup. It simplifies the process of scraping data into a CSV format while providing comprehensive error handling. The framework is designed to streamline the creation of new web scrapers and leverage common scraping functionalities centrally, reducing the redundant boilerplate code often associated with building Python-based web scrapers from scratch.

Scrapers have three key functions, Validating, Parsing, and Navigating. The data Parser class forms the core logic of PyScrapify and is built to extract data based on four key assumptions: 

1. We can enter a given website at configured entry urls. 
2. We can create a function for converting each entry url and each of its subpages to a list of strings that includes desired data. 
3. We can regex match a string that when present indicates the presence of a desired block of strings.
4. We can expect the blocks of string we are extracting to be of a common format and length.

The core execution flow is initiated through `scraper_controller.py`, triggered via the `launcher.py` command-line interface.

***
# Usage:

This usage section covers configurations for existing scrapers, implementing new scrapers, and available framework settings.

## Using an Existing Scraper:

To use an existing scraper, follow these steps:

1. **Create a Configuration File**: Go to the `scrape_configs` directory and create a new JSON file. This file must contain:
    - The `scraper` key with the name of the scraper you want to use (check the `scrapers` directory for available options, BaseScraper is the parent class).
    - The `entries` key with an object of names and entry URLs for data extraction.

    Example configuration:
    ```json
    {
        "scraper": "Seek",
        "entries": {
            "Target Australia": "https://www.seek.com.au/companies/target-432304/reviews"
        }
    }
    ```

2. **Run the Scraper**: Execute `launcher.py` and select the configuration file you created when prompted in the command line interface. The scraper will process each entry URL defined in your configuration file.

## Creating a New Scraper:

Creating a new scraper is a more involved process, requiring coding. To first give some context to what you are doing when you implement a new scraper, you are defining siblings for the BaseScraper.py classes that specify expected values and implement expected methods. See an example implementation in the `Seek.py` scraper.

### Validators:

Implementing the scraper specific validator value and method below is recommended, though is not required. At the risk of bad data, bad urls, and unexpected errors, you can pass a url_pattern for any string and define validate_data_block to just pass.

Values:

* `url_pattern`: regex pattern to match to valid entry URLs. This pattern is used to verify all entry URLs in the configuration JSON.

Methods:

* `validate_data_block`: function that validates that an extracted data block is as expected, you should raise a SE.UnexpectedData('message') error if validation fails.

### Parsers:

Implementing the scraper specific parser values and methods is required. 
Values:

* `browser_lang`: language code string to be used by Selenium Chrome Driver browser session. See available language codes here: https://cloud.google.com/speech-to-text/docs/languages.
* `text_pattern`: regex pattern to match to strings in a list of strings extracted from page source. Should match all locations that have a block of relevant data.
* `text_idx`: integer value for howmany indexs into a data block the text_pattern string is expected to be.
* `data_length`: integer value for howmany indexs long a data block of relevant strings is expected to be. 


Methods:

* 

***

# Contribution:

We welcome new ideas and contributions. If you have ideas or wish to implement features, please open an issue.

# Disclaimer:

This tool has been developed solely for educational, research, and public interest purposes. Every user is advised that they are responsible for:

* Reviewing the Terms of Service (ToS) of the target website they intend to scrape. Do note, ToS can change over time and can be implicit or explicit.
* Checking any robots.txt file on the target website to ensure that scraping activities are permitted and align with the website's directives.
* Limiting scraping activities so as to not disrupt or overly burden the website's infrastructure.

By using this tool, users agree to follow all relevant guidelines, terms, and restrictions of the target website. They also acknowledge that the creators and maintainers of this repository neither endorse nor encourage any actions that could breach laws, regulations, or website terms. We are not liable for misuse of this tool or any consequences arising from its use. Website providers with concerns about the scraping functionality contained in this repository are encouraged to open an issue so we can work to resolve the concern.

Always use technology ethically and responsibly.

***
# Acknowledgements:

This project was originally just an employee employer review scraper for Indeed and Seek. At that time, this project was inspired and to an extent guided by the work of tim-sauchuk on a now broken Indeed.com scrape tool.
Link: https://github.com/tim-sauchuk/Indeed-Company-Review-Scraper

Additionally, McJeffr provided very valuable feedback that greatly helped in guiding this project originally.
Link: https://github.com/McJeffr

***
# Future:

It is hoped this repository can serve as a robust framework that enables easier setup of responsible scraping activities. We will continue to work on resolving bugs and improving the functionality of the core framework. Additionally, where appropriate, we will work to repair scrapers added to the official repository. Here are some goals for future versions:

Roadmap to `v1.1`

* Ensure Linux and Windows compatibility
* Move to more robust dependency manager
  
Roadmap to `v1.2`

* Explore making pyscrapify a pip package
* Explore approaches to simplify the creation of new scrapers

***
# License:

Copyright (c) [@Jamal135]

MIT License

<!-- github-only -->
[@Jamal135]: https://github.com/Jamal135