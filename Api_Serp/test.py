import os.path
import os
from glob import glob
import pandas as pd
from modules.scraper import scrape_data
from datetime import date, datetime
from modules.utils import remove_stopwords
from modules.translator import translate_to_arabic, translate_to_english
import Levenshtein
a = remove_stopwords(translate_to_english('انا مرتبك من الخوف'))
print(a)