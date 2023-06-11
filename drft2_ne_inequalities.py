from bs4 import BeautifulSoup
import requests
import re

search_term = input("What product do you want to search for? ")
minimum_price = int(input("How low in price would you like me to search? < $... "))
maximum_price = int(input("How high in price would you like me to search? > $... "))
# Make loop incase price input is not an integer

url = f"https://www.newegg.com/p/pl?N=4131&d={search_term}&LeftPriceRange={minimum_price}+{maximum_price}" #[Good]
page = requests.get(url).text
doc = BeautifulSoup(page, "html.parser")

page_text = doc.find(class_="list-tool-pagination-text").strong 
pages = int(str(page_text).split("/")[-2].split(">")[-1][:-1])

items_found = {} 

for page in range(1, pages + 1): # +1 because naturally range begins at 0 (but our pages do not)
    url = f"https://www.newegg.com/p/pl?N=4131&d={search_term}&LeftPriceRange={minimum_price}+{maximum_price}&page={page}" #[Good!]
    page = requests.get(url).text
    doc = BeautifulSoup(page, "html.parser")

    div = doc.find(class_="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell")
    items = div.find_all(text=re.compile(search_term)) # DeprecationWarning: The 'text' argument to find()-type methods is deprecated. Use 'string' instead
    for item in items:
        parent = item.parent
        if parent.name != "a": 
            continue
        
        link = parent['href']
        next_parent = item.find_parent(class_="item-container")
        try:    
            price = next_parent.find(class_="price-current").find('strong').string # if there's an error here, it's because in this div there is not a strong tag
            items_found[item] = {"price": int(price.replace(",","")), "link": link} # [("3080", {'price': 2999, "link": "www."})]
        except:
            pass

sorted_items = sorted(items_found.items(), key=lambda x: x[1]['price'])

for item in sorted_items:
    print(item[0])
    print(f"${item[1]['price']}")
    print(item[1]['link'])
    print("----------------------------------------------")
