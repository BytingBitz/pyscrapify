# Indeed.com-Organisation-Review-Scraper

***
About:
---
This tool was built simply because I could not find an alternative currently functional tool that worked for pulling Indeed.com organisational reviews. This project also represents my first dive into scraping data from websites and it was a very valuable learning opportunity.

Data collected from Indeed.com for each organisation review:

* Rating: The 1-5 star rating entered.
* Position: The provided job title the individual worked.
* Location: The provided location the individual worked.
* Status: The provided Current or Former employment status.
* Year: The year in which the user placed the review.
* Title: The title the user gave their review.
* Review: The text content of the written review.

The built CSV is ordered by the following column headers: Year,Rating,Status,Location,Position,Title,Review. Note: If a new CSV file with the same name as an existing one is created, it will fully replace the existing file.

Creation Date: 27/06/2021

***
Usage:
--- 
Single organisation review scrape:

1: Call reviewScrape(url, outputName, country) with correct string arguments. Note: country must be the code Indeed.com use.

```python
reviewScrape("https://au.indeed.com/cmp/Indeed/reviews", "Indeed-Reviews", "AU")
```

Multiple organisation review scrape:

1: Populate the organisations.json with the url, outputName, and country for each organisation being scraped. Note: order matters, the first entry of urls matches to the first entry of names and countries respectively.

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
    
2: Call multiReviewScrape() with no provided arguments.

```python
multiReviewScrape()
```

***
Acknowledgements:
---
This project was inspired and to an extent guided by the work of tim-sauchuk on a now broken Indeed.com scrape tool.
Link: https://github.com/tim-sauchuk/Indeed-Company-Review-Scraper

***
Future:
---
Given this project was only developed for some business analysis I have been conducting, future development of this tool currently is unlikely. If bugs are found, will likely fix.

***
License:
--- 
MIT LICENSE