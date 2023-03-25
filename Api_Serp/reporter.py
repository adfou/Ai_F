### Reporter ###
"""A set of helper functions to be used to create and read reports"""

# Import modules
import os.path
from glob import glob
import pandas as pd
from .modules.scraper import scrape_data
from datetime import date, datetime
from .modules.utils import remove_stopwords
from .modules.translator import translate_to_arabic, translate_to_english
import Levenshtein

# Words classifier
def words_classifier(phrase_ar):
    """Function to classify words"""
    
    # Load table
    table = pd.read_csv("dataset/table.csv")
    
    # Preporocess arabic text
    phrase_en = translate_to_english(phrase_ar)
    phrase_en = phrase_en.replace(',', '')
    phrase_en_sw = remove_stopwords(phrase_en)
    
    # Classification
    table_classes = {}
    repeated_classes = []
    for column in table.columns:
        for word in phrase_en_sw.split(" "):
            if (table[column].eq(word)).any():
                if column not in repeated_classes:
                    repeated_classes.append(column)
                    table_classes[column] = word
                else:
                    table_classes[column] += word+" "
                    
    # Return result
    return table_classes

# Create report
def create_report(id, no, headline, description, feeling, table_classes):
    """Function used to create a report"""
    
    # Create new foldet with id if not exist
    newpath = f"reports/{id}" 
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    
    # Date and time
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
    date = dt_string[0:10]
    time = dt_string[11:]
    
    # Write to a file
    f = open(f"reports/{id}/{no}.txt","w+", encoding="utf-8")
    f.write(f"{headline}\n")
    f.write("=========\n\n")
    f.write(f"الوقت : {time}\n")
    f.write(f"التاريخ : {date}\n")
    f.write(f"الوصف : {description}\n")
    f.write(f"عدد الكلمات : {len(description.split())}\n")
    f.write(f"الشعور : {feeling}\n\n")
    f.write(f"تصنيف الكلمات : \n")
    for key, value in table_classes.items():
        key = translate_to_arabic(key)
        value = translate_to_arabic(value)
        f.write(f"{key} : {value} \n")
    f.close()
    
# Read report
def read_report(id, no):
    """Function used to read a report"""
    
    # Write to a file
    f = open(f"reports/{id}/{no}.txt","r", encoding="utf-8")
    lines = f.readlines()
    
    # Store report data
    date = lines[4].replace("التاريخ : ", "").strip()
    desc = lines[5].replace("الوصف : ", "").strip()
    feel = lines[7].replace("الشعور : ", "").strip()
    
    # Close the file
    f.close()

    # Return the result
    return date, desc, feel

# Compare reports
def compare_report(id, no):
    """Function used to compare between reports"""
    
    # Read current report information
    cur_date, cur_desc, cur_feel = read_report(id, no)
    
    # Loop over all previous reports
    similarity = []
    noms = []
    dates = []
    for filepath in glob(f"reports/{id}/*.txt"):
        file_no = filepath[len(filepath)-5:][0]
        if file_no != no:
            prev_date, prev_desc, prev_feel = read_report(id, file_no)
            a = remove_stopwords(translate_to_english(cur_desc))
            b = remove_stopwords(translate_to_english(prev_desc))
            noms.append(file_no)
            dates.append(prev_date)
            similarity.append(100 - Levenshtein.distance(a, b))
            
    # Return the result            
    return noms, dates, similarity           
    

# Compare reports to news
def compare_report_to_news(id, no, country, period):
    """Function used to compare report to news"""
    
    # Get news
    news = scrape_data(country, period)
    news = news['Title'].values.tolist()
    
    # Read current report information
    cur_date, cur_desc, cur_feel = read_report(id, no)
    
    # Loop over all previous reports
    similarity = []
    vip_news = []
    for new in news:
        a = remove_stopwords(translate_to_english(cur_desc))
        b = remove_stopwords(translate_to_english(new))
        sim = 100 - Levenshtein.distance(a, b)
        similarity.append(sim)
        if sim > 90:
            vip_news.append(new)
        else:
            print(f"There's No to {new}")

    return vip_news
            