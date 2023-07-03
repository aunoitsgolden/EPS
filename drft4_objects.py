from bs4 import BeautifulSoup
import requests
import re

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

class Newegg(Scraper):
    def items(self, doc):
        item_container = doc.find(class_="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell")
        items = item_container.find_all(string=re.compile(product))
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

class HomeDepot(Scraper):
    def items(self, doc):
        grid = doc.find(class_="results-wrapped")
        item_container = grid.find_all(id=(re.compile("browse-search-pods"))) # done this way because I have not found a way to access containers individually
        for items in item_container:
            details = items.find_all(class_="product-pod--s5vy1") # bs4 only searches the first container (browser-search-pods1) and no other.
                
class BestBuy(Scraper):
    def items(self, doc):
        list = doc.find(class_="sku-item-list")
        items = list.find_all(string=re.compile(product))
        print(items)

select = input("What site would you like to search? Newegg, HomeDepot, or BestBuy? ")
select = select.strip().lower()

product = str(input("What item would you like to search for? "))
product_words = product.split()

minprice = input("MinPrice: ") 
maxprice = input("MaxPrice: ")

# sort = input("Would you like to sort by price or seller?")

inp_format1 = "%20".join(product_words) if len(product_words) > 1 else product
inp_format2 = "+".join(product_words) if len(product_words) > 1 else product
class_selection = {
    "newegg": Newegg(f"https://www.newegg.com/p/pl?N=4131&d={inp_format2}&LeftPriceRange={minprice}+{maxprice}"),
    "homedepot": HomeDepot(f"https://www.homedepot.com/s/{inp_format1}?NCNI-5&lowerBound={minprice}&upperBound={maxprice}"),
    "bestbuy": BestBuy(f"https://www.bestbuy.com/site/searchpage.jsp?st={inp_format2}&qp=currentprice_facet%3DPrice~{minprice}%20to%20{maxprice}"),
} # Need to add page loop

selected_class = class_selection.get(select)
if selected_class:
    instance = selected_class
else:
    print("The scraper for Site {site} hasn't been implemented yet.")

doc = instance.fetch_page()
instance.items(doc)

# sorted_items = sorted(items_found.items(), key=lambda x: x[1]['price'])

# print(sorted_items)

# sorted = sorted(items_found.items(), key=lambda x: x[1]['seller'])
# sort_option = sort_select.get(items_found)
# if sort_option:
#     instance = sort_option
# else:
#     print("We cannot sort by that yet.")


