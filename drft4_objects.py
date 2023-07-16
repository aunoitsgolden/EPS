from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re

class Scraper:
    def __init__(self, url):
        self.url = url 
        
    def fetch_page(self):
        html = requests.get(self.url)
        doc = BeautifulSoup(html.text, 'html.parser')    
        return doc
    
    def find_matches(self, doc): #we can probably remove these classes
        raise NotImplementedError()
        
    def get_data(self, matches):
        raise NotImplementedError()

class JSP_Scraper:
    def __init__(self, url):
        self.url = url 
        
    def fetch_page(self):
        options = webdriver.ChromeOptions()
        options.headless = True
        
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        html = driver.page_source
        driver.quit()
        
        doc = BeautifulSoup(html, 'html.parser')
        return doc
    
    def find_matches(self, doc):
        raise NotImplementedError()

    def get_data(self, matches):
        raise NotImplementedError()

# Add Manufacturer Name + Seller Rating
class Newegg(Scraper):
    def find_matches(self, doc):
        matches = {}
        counters = {'Keyword Matches': 0, 'Pattern Matches': 0}

        grids = doc.find_all(class_= "item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell")
        items = []
        for grid in grids: 
            items.extend(grid.find_all(class_= "item-cell"))
            
        for item in items: 
            name_tag = item.find('a', {'class': 'item-title'})

            if name_tag:
                name = name_tag.text
                name_kw = set(name.lower().split())

                if keywords.issubset(name_kw): # matches by comparing keywords to name words
                    matches[name] = {'item': item}
                    counters['Keyword Matches'] += 1  

                if pattern.search(name): # matches by searching name.text for keywords. Keywords in words are be included.
                    matches[name] = {'item': item}
                    counters['Pattern Matches'] += 1

        print(counters)
        return matches

    def get_data(self):                
        for name, data in matches.items():
            item = data['item']

            price_current = item.find('li', {'class': 'price-current'})
            price = price_current.find('strong').text if price_current and price_current.find('strong') else "Sorry, the price for this item is not available :("
            
            price_float = price_current.find('sup') if price_current else None
            price += price_float.text if price_float else "\nDecimal value not available"
            
            link_tag = item.find('a', {'class': 'item-title'})
            link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "The link for this item is not available."

            matches[name] = {"Price": price, "Link": link}

class BestBuy(JSP_Scraper):
    def find_matches(self, doc):
        matches = {}
        counters = {'Keyword Matches': 0, 'Pattern Matches': 0}

        grids = doc.find("ol", class_="sku-item-list") 
        items = []
        for grid in grids:
            items.extend(grid.find_all("li", class_= "sku-item"))

        for item in items:
            name_tag = item.find('h4', {'class': 'sku-title'})
            
            if name_tag:
                name = str(name_tag.text)
                name_kw = set(name.lower().split())

                if keywords.issubset(name_kw):
                    matches[name] = {'item': item}
                    counters['Keyword Matches'] += 1            

                if pattern.search(name):
                    matches[name] = {'item': item}
                    counters['Pattern Matches'] += 1

        return matches
    
    def get_data(self):
        for name, data in matches.items():
            item = data['item']
            
            price_current = item.find('div', {'class': 'priceView-hero-price priceView-customer-price'})
            price = price_current.span.text.replace('$','') if price_current else "Price Not Available."

            link_tag = item.find('h4', {'class': 'sku-title'}).find_all('a')['href'] 
            link = (f'https://www.bestbuy.com{link_tag}')
        
            matches[name] = {"Price": price, "Link": link}
        
class HomeDepot(JSP_Scraper):
    def find_matches(self, doc):
        matches = {}
        counters = {'Keyword Matches': 0, 'Pattern Matches': 0}

        super = doc.find(class_="results-wrapped")
        grids = super.find_all(id=(re.compile("browse-search-pods")))
        items = []
        for grid in grids:
            items.extend(grid.find_all(class_="browse-search__pod col__12-12 col__6-12--xs col__4-12--sm col__3-12--md col__3-12--lg"))
            
        for item in items:
            name_tag = item.find(class_='product-header__title--clamp--4y7oa product-header__title--fourline--4y7oa')
            link = name_tag.parent['href']

            if name_tag:
                name = name_tag.text
                name_kw = set(name.lower().split())

                if keywords.issubset(name_kw): # matches by comparing keywords to name words
                    matches[name] = {'item': item, 'link': link}
                    counters['Keyword Matches'] += 1  

                if pattern.search(name): # matches by searching name.text for keywords. Keywords in words are be included.
                    matches[name] = {'item': item, 'link': link}
                    counters['Pattern Matches'] += 1

        print(counters)
        return matches
                
    def get_data(self):
        for name, data in matches.items():
            item = data['item']
            link = (f"https://www.homedepot.com{data['link']}")

            price_current = item.find(class_='price-format__main-price')
            if price_current: price_str = [span.text for span in price_current.find_all('span')]
            price = price_str[1] + price_str[2] if price_str else "Error"
            matches[name] = {'Price': price, 'Link': link}

def price_ascending(matches): 
    return sorted(matches.items(), key=lambda x: float(x[1]['Price']))
def price_descending(matches): 
    return sorted(matches.items(), key=lambda x: float(x[1]['Price']), reverse = True)

sort_items = {
        "1": price_ascending,
        "2": price_descending,}

site_select = (input("What site would you like to search? Newegg, HomeDepot, or BestBuy? ")).strip().lower()
query = str(input("What item would you like to search for? "))

min = input("MinPrice:")
max = input("MaxPrice:")
# selectable = input("Restriction on # of matches?")
# Starting from bottom, working to #
# Starting from top, working to #

words = query.split()
stop_words = ["for", "and", "the", "an", "a", "from"]
keywords = set()

for word in words:
    if word.lower() not in stop_words: 
        keywords.add(word)

pattern = re.compile('|'.join(keywords), re.IGNORECASE)  # matches by searching name.text for keywords. Keywords in words are be included.

format1 = "%20".join(words) if len(words) > 1 else query
format2 = "+".join(words) if len(words) > 1 else query
class_selection = { # Page loop (search pages above 1) 
    "newegg": Newegg(f"https://www.newegg.com/p/pl?N=4131&d={format2}&LeftPriceRange={min}+{max}"),
    "bestbuy": BestBuy(f"https://www.bestbuy.com/site/searchpage.jsp?st={format2}&qp=currentprice_facet%3DPrice~{min}%20to%20{max}"),
    "homedepot": HomeDepot(f"https://www.homedepot.com/s/{format1}?NCNI-5&lowerBound={min}&upperBound={max}")}

selected_class = class_selection.get(site_select)
if selected_class: 
    instance = selected_class
else: 
    print("The scraper for that site hasn't been implemented yet.") 

doc = instance.fetch_page()
matches = instance.find_matches(doc)
instance.get_data()

sort_select = input("How would you like to sort your items? (1): Low to High (2): High to Low ")

sort_function = sort_items.get(sort_select)
if sort_function:
    sorted_items = sort_function(matches) 
    for item in sorted_items:
        print(f"${item[1]['Price']}")
        print(item[0])
        print(item[1]['Link'])
        print("----------------------------------------------")
else: # we get this printed out when there are no results
    print("That kind of sorting hasn't been implemented yet.")

# Error Handling: This page results has no results https://www.newegg.com/p/pl?d=terabyte+x11spa-5
