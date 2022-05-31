# Pull all reviews data from Indeed & Seek for specific organisations using provided arguments.
# Creation Date: 27/06/2021

from scraperCode import indeed_scrape, seek_scrape, multi_scrape

# Scrape one organisation from Indeed:
#indeed_scrape("Indeed", "https://au.indeed.com/cmp/Indeed/reviews", "Indeed-Reviews", "AU")

# Scrape one organisation from Seek:
#seek_scrape("Google", "https://www.seek.com.au/companies/google-433216/reviews", "Google-Reviews")

# Scrape multiple reviews from Indeed and/or Seek (see readme to set organisations.json):
# websites: "Indeed" | "Seek" | "Both"
multi_scrape("Both", "QLD-Reviews-Data")
