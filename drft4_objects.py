from bs4 import BeautifulSoup
import requests
import re

# Version 4: Allow the User to search for a singular item off of 3 Different Sites
# with the option to filter price with a defined range. (x < y < z) y = product
# 
# Use classes and basic OOP to create reusable items to encourage development onto
# other websites.

class query:
    def __init__(self, item):
        self.y = item

class cost(query):
    def __init__(self, item, min, max):
        self.x = min
        self.z = max
        
        query().__init__(item) # you can also use super().

item = str(input("Product Name:"))
min, max = input("Please enter the min and max:") # making this (int) crashes the program... I don't know why

while not min.isdigit() and max.isdigit():
    min, max = (input("Please enter a valid number:"))
while min == 0:
    min = input("Please enter a value greater than 0 for your minimum:")
while max > min:
    max = input("Please input a maximum value greater than the minimum price:")

print("")


    # def dictionary(self):
    #     items_found[self.y] = item


#-------------------Scraper---------------------
class WebScraper:

    def __init__(self, url): # initalizing attribute of the WebScraper Class; takes 'url' as an argument and assigns it to 'url' attribute of the class
        self.url = url 
    
    def parse_page(self, page, doc):
        page = requests.get(self.url).text # gather page with GET request
        doc = BeautifulSoup(page, 'html.parser') # takes a string of HTML content and parses into a format easier to work with
        return doc # returns BeautifulSoup object

    def scrape(self): # uses parse_page to: 
        page_html = self.fetch_page() # fetches HTML content 
        parsed_page = self.parse_page(page_html) # parses the content into a BS object
        return parsed_page # object Returned

#---------------URLs---------------
# url = f"https://www.newegg.com/p/pl?N=4131&d={search_term}&LeftPriceRange={minimum_price}+{maximum_price}"

#---- Page Scraping Example ----
# scraper = WebScraper(url)
# parsed_page = scraper.scrape()

# print(parsed_page)

#------------------Dictionary----------------------

items_found = {} # items are being placed into this dictionary

#----------------------------Newegg----------------------------
# page_text = doc.find(class_="list-tool-pagination-text").strong
# pages = int(str(page_text).split("/")[-2].split(">")[-1][:-1])

# for page in range(1, pages + 1): # +1 because naturally range begins at 0 (but our pages do not)
    # url = f"https://www.newegg.com/p/pl?N=4131&d={search_term}&LeftPriceRange={minimum_price}+{maximum_price}&page={page}"
    # page = requests.get(url).text
    # doc = BeautifulSoup(page, "html.parser")

#   6