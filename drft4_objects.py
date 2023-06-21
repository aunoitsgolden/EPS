from bs4 import BeautifulSoup
import requests
import re

# Version 4: Allow the User to search for a singular item off of 3 Different Sites
# with the option to filter price with a defined range. (x < y < z) y = product
# 
# Use classes and basic OOP to create reusable items to encourage development onto
# other websites.

#--------------Query--------------
item = str(input("Product Name:"))
minprice = input("MinPrice:")
maxprice = input("MaxPrice:")

# Error Handling
while not minprice.isdigit() and maxprice.isdigit(): 
    minprice, maxprice = (input("Please enter a valid number:"))
while minprice == 0:
    minprice = input("Please enter a value greater than 0 for your minimum:")
while maxprice > minprice:
    maxprice = input("Please input a maximum value greater than the minimum price:")

items_found = {}

#-------------------Scraper---------------------
class WebScraper:
    def __init__(self, url, query):
        self.url = url 
        self.query = query
    
    def fetch_page(self):
        raise NotImplementedError("Method will be implemented in subclass.")
            
    def parse_page(self, html):
        doc = BeautifulSoup(html, 'html.parser') 
        return doc 

    def scrape(self): 
        page_html = self.fetch_page() 
        parsed_page = self.parse_page(page_html) 
        return parsed_page 

#----Newegg Scraper----
class NeweggScraper(WebScraper):
    def fetch_page(self, page):
        full_url = f"https://www.newegg.com/p/pl?N=4131&d={item}&LeftPriceRange={minprice}+{maxprice}"
        response = requests.get(full_url)
        return response.text 
        
        page_text = doc.find(class_="list-tool-pagination-text").strong # We could get rid of this, however currently keeping for possible future use.
        pages = int(str(page_text).split("/")[-2].split(">")[-1][:-1])

        for page in range(1, pages + 1): # +1 because naturally range begins at 0 (but our pages do not)  
            full_url = f"https://www.newegg.com/p/pl?N=4131&d={item}&LeftPriceRange={minprice}+{maxprice}&page={page}"
            response = requests.get(full_url)
            return response.text 
        
# Creates instance
ScraperResults = NeweggScraper.parsed_page
print(ScraperResults)

