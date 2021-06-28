# Indeed.com-Organisation-Review-Scraper

***
About:
---
This tool was built simply because I could not find a currently functional tool for pulling Indeed.com organisational review data. This project also represents my first dive into scraping data from websites and it was a very valuable learning opportunity.

Data collected from Indeed.com for each organisation review:

* Rating: The 1-5 star rating.
* Position: The specified job title.
* Location: The specified location.
* Status: The Current or Former employment status.
* Year: The year in which the review was placed.
* Title: The title of the user review.
* Review: The text content of the user review.

The built CSV is ordered by the following column headers: Year,Rating,Status,Location,Position,Title,Review. Note: If a new CSV file with the same name as an existing one is created, it will replace the existing file.

Creation Date: 27/06/2021

***
Usage:
--- 
Single organisation review scrape:

1: Call review_scrape(url, outputName, country) with correct string arguments. Note: country must be the code Indeed.com use.

```python
review_scrape("https://au.indeed.com/cmp/Indeed/reviews", "Indeed-Reviews", "AU")
```

Multiple organisation review scrape:

1: Populate the organisations.json with the url, outputName, and country for each organisation being scraped.

```json
{
    "configs":
    [
        {
            "url": "https://au.indeed.com/cmp/Federal-Government/reviews",
            "name": "Indeed-Reviews",
            "country": "AU"
        },
        {
            "url": "https://au.indeed.com/cmp/Indeed/reviews",
            "name": "Federal-Government-Reviews",
            "country": "AU"
        }
    ]
}
```
    
2: Call multi_review_scrape().

```python
multi_review_scrape()
```
Note: You may provide your own data dictionary instead of providing None as a function call argument.

***
Acknowledgements:
---
This project was inspired and to an extent guided by the work of tim-sauchuk on a now broken Indeed.com scrape tool.
Link: https://github.com/tim-sauchuk/Indeed-Company-Review-Scraper

***
Future:
---
Given this project was only developed for some research I have been conducting, future development of this tool is unlikely. If bugs are found, they will likely be fixed.

***
License:
--- 
MIT LICENSE