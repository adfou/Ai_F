### Scraper ###
"""A set of helper functions to be used to scrape data from internet"""

# Import modules
import pandas as pd
from GoogleNews import GoogleNews

# Scraping
def scrape_data(country, period):
    """Function to scrape data from countey on google"""

    # Get news
    news = GoogleNews(period=period)
    news.search(country)
    #date = news.get_links()
    results = news.result()
    
    print(results)
    # Store the news on dataframe
    data = pd.DataFrame.from_dict(results)
    
    # Store only title
    newshort = pd.DataFrame({'Title':data['title']})

    # Return the data
    return newshort,results
    

