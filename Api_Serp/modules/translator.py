### Transloter ###
"""A set of helper functions to be used to transalte sentece from arabic to english"""

# Import modules 
from deep_translator import GoogleTranslator

# Tanslate from arabic to english
def translate_to_english(arabic_sentence):
    """Function used to translte sentence from arabic to english"""
    # Translte from arabic to english
    english_sentence = GoogleTranslator(source="ar", target="en").translate(arabic_sentence) 
    # Return the reults
    return english_sentence

# Tanslate from english to arabic
def translate_to_arabic(english_sentence):
    """Function used to translte sentence from arabic to english"""
    # Translte from english to arabic
    arabic_sentence = GoogleTranslator(source="en", target="ar").translate(english_sentence) 
    # Return the reults
    return arabic_sentence

### Data Scraping ###
"""Functions help on scraping data from internet"""

# Scraping
def scrape_data(period, country):
    """Function to scrape data from countey on google"""

    # Get news
    news = GoogleNews(period=period)
    news.search(country)
    results = news.result()

    # Store the news on dataframe
    data = pd.DataFrame.from_dict(results)
    data = data.drop(columns=['img'])
    print(data.head())
    
    # Store only title
    newshort = pd.DataFrame({'Title':data['title']})
    print(newshort)

    # Return the data
    return newshort
    

