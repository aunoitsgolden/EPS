from bs4 import BeautifulSoup
import requests
import re

# Version 4: Allow the User to search for a singular item off of 3 Different Sites
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

items_found = {}

class Scraper:
    def __init__(self, url):
        self.url = url 
    
    def fetch_page(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        html = requests.get(self.url, headers=headers)
        doc = BeautifulSoup(html.text, 'html.parser')    
        return doc
    
    def items(self, doc):
        raise NotImplementedError()

#---------Technology-------------    
class Newegg(Scraper):
    def items(self, doc):
        div = doc.find(class_="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell")
        items = div.find_all(string=re.compile(product))
        for item in items:
            parent = item.parent
            if parent.name != "a":
                continue
        
        link = parent['href']
        next_parent = item.find_parent(class_="item-container")
        try:    
            price = next_parent.find(class_="price-current").find('strong').string
            items_found[item] = {"price": int(price.replace(",","")), "link": link}
        except:
            pass
         
class MicroCenter(Scraper):
    def items(self, doc):
        return

#------------Home---------------     
class HomeDepot(Scraper):
    def items(self, doc):
        grid = doc.find(class_="grid")
        items = grid.find_all(string=re.compile(brand))
        print(items)

# error handling & explore if query class is a good idea
brand = str(input("Is there a specific brand you would like to search?"))
product = str(input("What item would you like to search for?"))
product_words = product.split()
HD_product = "%20".join(product_words) if len(product_words) > 1 else product

minprice = input("MinPrice:")
maxprice = input("MaxPrice:") 

newegg_url = f"https://www.newegg.com/p/pl?N=4131&d={product}&LeftPriceRange={minprice}+{maxprice}"  
homedepot_url = f"https://www.homedepot.com/s/{HD_product}?NCNI-5&lowerBound={minprice}&upperBound={maxprice}"
microcenter_url = f"https://www.microcenter.com/search/search_results.aspx?N=&cat=&Ntt=3080&searchButton=search"

# {site}scraper = {scraper}({site}_url, item)
# doc = {site}scraper.fetch_page()
# {site}scraper.items(doc)

       

