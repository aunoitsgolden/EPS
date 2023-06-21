from bs4 import BeautifulSoup
import requests
import re

search_term = str(input("What product do you want to search for? "))

minimum_price = input("How low in price would you like me to search? > $")
while not minimum_price.isdigit():
    minimum_price = input("Please input a valid number: $") 

maximum_price = input("How high in price would you like me to search? < $")
while not maximum_price.isdigit():
    maximum_price = input("Please input a valid number: $")

url = f"https://www.newegg.com/p/pl?N=4131&d={search_term}&LeftPriceRange={minimum_price}+{maximum_price}"
page = requests.get(url).text
doc = BeautifulSoup(page, "html.parser")

page_text = doc.find(class_="list-tool-pagination-text").strong
pages = int(str(page_text).split("/")[-2].split(">")[-1][:-1])

items_found = {} # items are being placed into this dictionary

for page in range(1, pages + 1): # +1 because naturally range begins at 0 (but our pages do not)
    url = f"https://www.newegg.com/p/pl?N=4131&d={search_term}&LeftPriceRange={minimum_price}+{maximum_price}&page={page}"
    page = requests.get(url).text
    doc = BeautifulSoup(page, "html.parser")

    div = doc.find(class_="item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell")
    items = div.find_all(string=re.compile(search_term))
    for item in items:
        parent = item.parent
        if parent.name != "a": 
            continue
        
        link = parent['href']
        next_parent = item.find_parent(class_="item-container")
        try:    
            price = next_parent.find(class_="price-current").find('strong').string
            items_found[item] = {"price": int(price.replace(",","")), "link": link} # [("3080", {'price': 2999, "link": "www."})]
        except:
            pass

sorted_items = sorted(items_found.items(), key=lambda x: x[1]['price']) # print(str(sorted_items)) for sorted items
    
html_string = """
<!DOCTYPE html>
<html>
    <head>
        <title>Search Query Results</title>
    </head>
    <body>
    <h2>Here are the items you searched for, from least to most expenisve:</h2>
        <ul>
"""

for item in sorted_items: 
    html_string += f"""            <li>{item[0]}</li>
        <ul>
            <li>{f'${item[1]["price"]}'}</li>
            <li><a href="{item[1]['link']}">See on Newegg.com</a></li>
        </ul>\n""" # must be "\n" for newline, "/n" would just be added to the string

html_string += """
        </ul>
    </body>
</html>
"""

with open('output.html', 'w') as html_file:
    html_file.write(html_string)
