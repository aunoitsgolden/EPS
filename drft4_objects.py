from bs4 import BeautifulSoup
import requests

class Scraper:
    def __init__(self, url):
        self.url = url 
    
    def fetch_page(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        html = requests.get(self.url, headers=headers)
        doc = BeautifulSoup(html.text, 'html.parser')    
        return doc
    
    def search(self, doc): # We can probably remove these classes
        raise NotImplementedError()
        
    def gather_data(self, matches):
        raise NotImplementedError()
        
class Newegg(Scraper):
    def search(self, doc):
        matches = {}
        grids = doc.find_all(class_= "item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell")
        for grid in grids:
            items = grid.find_all(class_= "item-cell")
            for item in items:
                name_html = item.find('a', {'class': 'item-title'})
                if name_html: 
                    name_str = str(name_html)
                    name = name_html.text
                    if all(word.lower() in name_str.lower() for word in important_words):
                        matches[name] = {'item': item}
                else:
                    name = ("Title 'item-title' Tag Not Available")
        return matches
                    
    def gather_data(self, matches):
        for name, data in matches.items():
            item = data['item']
            price_current = item.find('li', {'class': 'price-current'})
            if price_current:
                price = price_current.find('strong')
                if price:
                    price = price.text
                    try: 
                        price_float = price_current.find('sup')
                        if price_float:
                            price += price_float.text
                        else: 
                            pass
                    except:
                        price = "Decimal 'sup' Tag Not Available. Please flag this query so we can add this feature."
                else:
                    price = "Price 'strong' Tag Not Available. Please flag this query so we can add this feature."
            else:
                price = "Price Not Available. 'price-current' HTML class not found. Please flag this query so we can add this feature."

            link_tag = item.find('a', {'class': 'item-title'})
            if link_tag and 'href' in link_tag.attrs:
                link = link_tag['href']
            else:
                link = ("Link Not Available. 'item-title' HTML class not found.")

            matches[name] = {"Price": price, "Link": link, "item": item}
            del matches[name]['item']
    
def price_ascending(matches): 
    return sorted(matches.items(), key=lambda x: float(x[1]['Price']))
def price_descending(matches): 
    return sorted(matches.items(), key=lambda x: float(x[1]['Price']), reverse = True)

sort_items = {
        "1": price_ascending,
        "2": price_descending,}

site_select = (input("What site would you like to search? Newegg, HomeDepot, or BestBuy? ")).strip().lower()

product = str(input("What item would you like to search for? "))
product_words = product.split()

# Options: Input Product and Attributes separately, separate by preposition, exclude preposition.
ignore_words = ["for", "and", "the", "an", "a"]
important_words = []
for word in product_words:
    if word.lower() not in ignore_words: 
        important_words.append(word)
        
minprice = input("MinPrice: ") # We have to put in some error handling for this
maxprice = input("MaxPrice: ")

inp_format2 = "+".join(product_words) if len(product_words) > 1 else product
class_selection = {
    "newegg": Newegg(f"https://www.newegg.com/p/pl?N=4131&d={inp_format2}&LeftPriceRange={minprice}+{maxprice}"),
} # Need to add page loop

selected_class = class_selection.get(site_select)
if selected_class: 
    instance = selected_class
else: 
    print("The scraper for that site hasn't been implemented yet.") 

doc = instance.fetch_page()
matches = instance.search(doc)
instance.gather_data(matches)

sort_select = input("How would you like to sort your items? (1): Low to High (2): High to Low ") # (3): Seller, A to Z (4): Seller, Z to A 

sort_function = sort_items.get(sort_select)
if sort_function:
    sorted_items = sort_function(matches) 
    for item in sorted_items:
        print(f"${item[1]['Price']}") 
        print(item[0])
        print(item[1]['Link']) 
        print("----------------------------------------------")
else: 
    print("That kind of sorting hasn't been implemented yet.") 
