# Indeed.com-Organisation-Review-Scraper

***
# About:
---
This tool was built simply because I could not find a currently functional tool for pulling Indeed.com and Seek.com organisational review data. This project also represents my first dive into scraping data from websites and it was a very valuable learning opportunity.

Data collected from Indeed.com & Seek.com for each organisation review:

* Rating: The 1-5 star rating.
* Position: The specified job title.
* Location: The specified location.
* Status: The Current or Former employment status.
* Year: The year in which the review was placed.
* Title: The title of the user review.
* Review: The text content of the user review.

On Seek.com location and status are not always provided and will be defined as Unknown if they don't exist for a given review. The built CSV is ordered by the following column headers: Organisation,Website,Year,Rating,Status,Location,Position,Title,Review. Note: If output_name matches an existing CSV file, new review data will be appended to that existing CSV file. 

Creation Date: 27/06/2021

***
# Usage:
--- 
## Single Indeed.com organisation review scrape:

organisation: The desired organisation name to appear in the CSV file
indeed_url: The correct url for the organisation reviews of a organisation on Indeed.com
output_name: Desired output CSV filename (excluding the .csv part)
indeed_country: The desired country/location code Indeed.com use

1: Call indeed_scrape(organisation, indeed_url, output_name, country) with correct string arguments.

```python
indeed_scrape("https://au.indeed.com/cmp/Indeed/reviews", "Indeed-Reviews", "AU")
```

## Single Seek.com organisation review scrape:

organisation: The desired organisation name to appear in the CSV file
seek_url: The correct url for the organisation reviews of a organisation on Seek.com
output_name: Desired output CSV filename (excluding the .csv part)

1: Call seek_scrape(organisation, seek_url, output_name)

```python
indeed_scrape("https://au.indeed.com/cmp/Indeed/reviews", "Indeed-Reviews", "AU")
```

## Multiple organisation review scrape:

1: Populate the organisations.json with the necessary variables based on if scraping from Indeed, Seek, or both.

Example: Scraping multiple of Indeed.com only.
```json
{
    "configs":
    [
        {
            "organisation": "Aldi",
            "indeed_url": "https://au.indeed.com/cmp/Aldi/reviews",
            "indeed_country": "AU"
        },
        {
            "organisation": "Kmart",
            "indeed_url": "https://au.indeed.com/cmp/Kmart/reviews",
            "indeed_country": "AU"
        }
    ]
}
```

Example: Scraping multiple of Seek.com only.
```json
{
    "configs":
    [
        {
            "organisation": "Aldi",
            "seek_url": "https://www.seek.com.au/companies/aldi-432489/reviews"
        },
        {
            "organisation": "Kmart",
            "seek_url": "https://www.seek.com.au/companies/kmart-432302/reviews"
        }
    ]
}
```

Example: Scraping multiple of Indeed.com and Seek.com combined.
```json
{
    "configs":
    [
        {
            "organisation": "Aldi",
            "indeed_url": "https://au.indeed.com/cmp/Aldi/reviews",
            "indeed_country": "AU",
            "seek_url": "https://www.seek.com.au/companies/aldi-432489/reviews"
        },
        {
            "organisation": "Kmart",
            "indeed_url": "https://au.indeed.com/cmp/Kmart/reviews",
            "indeed_country": "AU",
            "seek_url": "https://www.seek.com.au/companies/kmart-432302/reviews"
        }
    ]
}
```

websites: "Indeed" | "Seek" | "Both"
output_name: Desired output CSV filename (excluding the .csv part)
data: Alternative data to organisations.json (empty by default)

2: Call multi_review_scrape(websites, output_name, data).

```python
multi_review_scrape("both", "Reviews-Data")
```


***
# Acknowledgements:
---
This project was inspired and to an extent guided by the work of tim-sauchuk on a now broken Indeed.com scrape tool.
Link: https://github.com/tim-sauchuk/Indeed-Company-Review-Scraper

***
# Future:
---
Given this project was only developed for some research I have been conducting, future development of this tool is unlikely. If bugs are found, they will likely be fixed.

***
# License:
--- 
Mit License