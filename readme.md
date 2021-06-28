# Indeed.com-Organisation-Review-Scraper 1

***
About:
---
    Data collected from Indeed.com for each organisation review:
    "*" Rating: The 1-5 star rating entered.
    "*" Position: The provided job title the individual worked.
    "*" Location: The provided location the individual worked.
    "*" Status: The provided Current or Former employment status.
    "*" Year: The year in which the user placed the review.
    "*" Title: The title the user gave their review.
    "*" Review: The text content of the written review.

    Structure of the resulting CSV file per organisation scrape:
    The built CSV is ordered by the following column headers:
    Year,Rating,Status,Location,Position,Title,Review
    Note: If a new CSV file with the same name as an existing one
    is created, it will fully replace the existing file.

***
Usage:
--- 
    Single organisation review scrape:

    1: Call reviewScrape(url, outputName, country) with correct
    string arguments. Note: country must be the code Indeed use.

    Example:

    ```python
    reviewScrape("https://au.indeed.com/cmp/Indeed/reviews", "Indeed-Reviews", "AU")
    ```

    Multiple organisation review scrape:

    1: Populate the organisations.json with the url, outputName,
    and country for each organisation being scraped. Note, order
    matters.

    ```json
    { 
        "urls": [
            "https://au.indeed.com/cmp/Indeed/reviews",
            "https://au.indeed.com/cmp/Federal-Government/reviews"
        ],
        "names" : [
            "Indeed-Reviews",
            "Federal-Government-Reviews"
        ],
        "countries" : [
            "AU",
            "AU"
        ]
    }
    ```
    
    2: Call multiReviewScrape()

    ```python
    multiReviewScrape()
    ```

***
Acknowledgements:
---
    This project was inspired and to an extent guided by the work
    of tim-sauchuk on a now broken Indeed.com scrape tool.
    Link: https://github.com/tim-sauchuk/Indeed-Company-Review-Scraper

***
Future:
---
    Given this project was only developed for some business analysis
    I have been conducting, future development of this tool currently
    is unlikely. If bugs are found, will likely fix.

***
License:
--- 
    MIT LICENSE