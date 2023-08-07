from selenium import webdriver
import time
from bs4 import BeautifulSoup
import requests
import re

class User_Input():

    @staticmethod
    def get_product():
        while True:
            try:
                product = str(input("What item would you like to search for? "))
                if product.strip():
                    return product
                
                else: 
                    print("Please enter a valid product name.")

            except ValueError:
                print("Invalid input. Please try again.")
  
    @staticmethod
    def get_price_range():
        while True:
            try:
                range_select = int(input("Filter by price? Enter 1 for Yes | Enter 2 for No: "))

                if range_select == 1: 
                    lower_limit = float(input("Enter lower limit of price range: $"))
                    upper_limit = float(input("Enter upper limit of price range: $"))

                    if lower_limit <= upper_limit:
                        return (lower_limit, upper_limit)
                    else:
                        print("Upper limit should be greater than or equal to lower limit. Please try again.")

                elif range_select == 2:
                    return None

                else:
                    print("Invalid choice. Please enter 1 or 2.")

            except ValueError:
                print("Invalid input. Please enter a number.")

    @staticmethod
    def stock_filter():
        while True:
            try:
                product = int(input("Only present items in stock? Enter 1 for Yes | Enter 2 for No: "))

                if product == 1: 
                    return True
                if product == 2: 
                    return False
                else: 
                    print('Please enter either "1" or "2".')
                    
            except ValueError:
                print("Invalid input. Please try again.")

    @staticmethod
    def user_selectable():
        while True:
            x = input("How many results would you like to view (0 for all)? ")
            try:
                val = int(x)
                return val

            except ValueError:
                print("Invalid input. Please try again.") 

product     = User_Input.get_product()
price_range = User_Input.get_price_range()
stock_opt   = User_Input.stock_filter()
records     = User_Input.user_selectable()

def keyword_match(product):
    product_words = product.split()
    stop_words = ["for", "and", "the", "an", "a", "from"]
    keywords = set()

    for word in product_words:
        if word.lower() not in stop_words: 
            keywords.add(word)
    
    pattern = re.compile('|'.join(keywords), re.IGNORECASE)
    return pattern

# Scrapers
class LCSC_Scraper():

    def selenium_driver(url, sleep_time):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        driver.get(url)
        time.sleep(sleep_time)
        html = driver.page_source
        driver.quit()
        
        doc = BeautifulSoup(html, 'html.parser')
        page_number = doc.find(class_='v-pagination__item').last_element

        return doc

    def search(doc):
        matches = {}

        items = []
        items.extend(doc.find_all("tr", attrs={"data-v-3be1a989":""}))
        for item in items:
            name_tag = item.find("div", class_="product-intro")
            if name_tag == None: continue
            else: name = name_tag.text.strip()

            product_tag = item.find("a", class_="link", href=lambda x: x and "/product-detail/" in x)
            if product_tag: 
                product_number = product_tag.text.strip()
                link = product_tag.get('href')
            else: raise AttributeError
            
            if name and product_number:
                name_strip = name + product_number
                
                pattern = keyword_match(product)
                if pattern.search(name_strip):  
                    matches[product_number] =  {'name': name, 'link':link, 'item': item}
        
        return matches

    def gather_data(matches):
        for product_number, data in matches.items():
            item = data['item']
            
            price_tags = item.find_all("div", class_="price-row")
            for price_tag in price_tags:
                cleaned_tag = re.sub('\s+', ' ', (price_tag.text.strip()).replace('US$', ' ').strip())
                price = (cleaned_tag.split())[1]
                
                # try: 
                #     price, qty = values
                #     value_dictionary = {float(price):qty}
                #     print(value_dictionary)
                # except ValueError:
                #     print("Discount rate price tag.")

            stock_tag = item.find_all("td", attrs={"data-v-3be1a989":""})[3].text.strip()
            stock = re.sub('\s+', ' ', stock_tag.replace('\n', ' ').replace('\r', '').strip())
            if stock_opt and ("0" in stock or "Discontinued" in stock):
                continue
            
            manufacturer = item.find("a", class_="link", href=lambda x: x and "/brand-detail/" in x).text.strip()

            matches[product_number] = {'name':data['name'], 'link':data['link'], 'price':price, 'stock':stock, 'manufacturer':manufacturer}
       
        return matches
   
# class Newegg():

#     def find_matches(self, doc):
#         matches = {}
#         counters = {'Keyword Matches': 0, 'Pattern Matches': 0}

#         grids = doc.find_all(class_= "item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell")
#         items = []
#         for grid in grids: 
#             items.extend(grid.find_all(class_= "item-cell"))
            
#         for item in items: 
#             name_tag = item.find('a', {'class': 'item-title'})

#             if name_tag:
#                 name = name_tag.text
#                 name_kw = set(name.lower().split())

#                 if keywords.issubset(name_kw): # matches by comparing keywords to name words
#                     matches[name] = {'item': item}
#                     counters['Keyword Matches'] += 1  

#                 if pattern.search(name): # matches by searching name.text for keywords. Keywords in words are be included.
#                     matches[name] = {'item': item}
#                     counters['Pattern Matches'] += 1

#         print(counters)
#         return matches

#     def get_data(self):                
#         for name, data in matches.items():
#             item = data['item']

#             price_current = item.find('li', {'class': 'price-current'})
#             price = price_current.find('strong').text if price_current and price_current.find('strong') else "Sorry, the price for this item is not available :("
            
#             price_float = price_current.find('sup') if price_current else None
#             price += price_float.text if price_float else "\nDecimal value not available"
            
#             link_tag = item.find('a', {'class': 'item-title'})
#             link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else "The link for this item is not available."

#             matches[name] = {"Price": price, "Link": link}

# class BestBuy():

#     def find_matches(self, doc):
#         matches = {}
#         counters = {'Keyword Matches': 0, 'Pattern Matches': 0}

#         grids = doc.find("ol", class_="sku-item-list") 
#         items = []
#         for grid in grids:
#             items.extend(grid.find_all("li", class_= "sku-item"))

#         for item in items:
#             name_tag = item.find('h4', {'class': 'sku-title'})
            
#             if name_tag:
#                 name = str(name_tag.text)
#                 name_kw = set(name.lower().split())

#                 if keywords.issubset(name_kw):
#                     matches[name] = {'item': item}
#                     counters['Keyword Matches'] += 1            

#                 if pattern.search(name):
#                     matches[name] = {'item': item}
#                     counters['Pattern Matches'] += 1

#         return matches
    
#     def get_data(self):
#         for name, data in matches.items():
#             item = data['item']
            
#             price_current = item.find('div', {'class': 'priceView-hero-price priceView-customer-price'})
#             price = price_current.span.text.replace('$','') if price_current else "Price Not Available."

#             link_tag = item.find('h4', {'class': 'sku-title'}).find_all('a')['href'] 
#             link = (f'https://www.bestbuy.com{link_tag}')
        
#             matches[name] = {"Price": price, "Link": link}
        
# class HomeDepot():

#     def find_matches(self, doc):
#         matches = {}
#         counters = {'Keyword Matches': 0, 'Pattern Matches': 0}

#         super = doc.find(class_="results-wrapped")
#         grids = super.find_all(id=(re.compile("browse-search-pods")))
#         items = []
#         for grid in grids:
#             items.extend(grid.find_all(class_="browse-search__pod col__12-12 col__6-12--xs col__4-12--sm col__3-12--md col__3-12--lg"))
            
#         for item in items:
#             name_tag = item.find(class_='product-header__title--clamp--4y7oa product-header__title--fourline--4y7oa')
#             link = name_tag.parent['href']

#             if name_tag:
#                 name = name_tag.text
#                 name_kw = set(name.lower().split())

#                 if keywords.issubset(name_kw): # matches by comparing keywords to name words
#                     matches[name] = {'item': item, 'link': link}
#                     counters['Keyword Matches'] += 1  

#                 if pattern.search(name): # matches by searching name.text for keywords. Keywords in words are be included.
#                     matches[name] = {'item': item, 'link': link}
#                     counters['Pattern Matches'] += 1

#         print(counters)
#         return matches
                
#     def get_data(self):
#         for name, data in matches.items():
#             item = data['item']
#             link = (f"https://www.homedepot.com{data['link']}")

#             price_current = item.find(class_='price-format__main-price')
#             if price_current: price_str = [span.text for span in price_current.find_all('span')]
#             price = price_str[1] + price_str[2] if price_str else "Error"
#             matches[name] = {'Price': price, 'Link': link}
 
def scraper_init(product):
    site_info = [
    (LCSC_Scraper, f"https://www.lcsc.com/search?q={product}", 1)
    ]

    for info in site_info:
        scraper_class, url, driver_sleep = info

        doc            = scraper_class.selenium_driver(url, driver_sleep)
        gathered_items = scraper_class.search(doc) 
        matches        = scraper_class.gather_data(gathered_items)
        results = matches.items()
        process_data(results, price_range)

# API
class Mouser_API():
    
    def request(product):
        # 1[None] | 2[Rohs] | 4[InStock] | 8[RohsAndInStock]
        x = 4 if stock_opt else 1 

        query = {
            "SearchByKeywordRequest": {
                "keyword": product, 
                "records": records, # 
                "startingRecord": 0, # where in the recordset to begin
                "searchOptions": x, # 4
                "searchWithYourSignUpLanguage": "true"
            }
        }

        response = requests.post("https://api.mouser.com/api/v1.0/search/keyword?apiKey=ad401d68-e0f0-4cab-88f6-3ab2b02ca78d", json=query)
        data = response.json()
        return data
    
    def gather_data(data):
        matches = {}

        for part in data['SearchResults']['Parts']:
            name           = part['Description']
            product_number = part['ManufacturerPartNumber']
            link           = part['ProductDetailUrl']
            life_cycle     = part['LifecycleStatus']
            stock          = part['Availability']
            manufacturer   = part['Manufacturer']

            for prices in part['PriceBreaks']:
                price_dict = {}
                price      = float(prices['Price'].replace("$", ""))
                quantity   = prices['Quantity']
                
                price_dict[quantity] = price
                
            last_price = list(price_dict.values())[-1]

            matches[product_number] = {
                'name':name, 
                'link':link, 
                'price':last_price, 
                'stock':stock, 
                'manufacturer':manufacturer, 
                }
        
        return matches

def api_init(product):
    data             = Mouser_API.request(product)
    matches = Mouser_API.gather_data(data)
    results          = matches.items()
    process_data(results, price_range)

# Filter
class Filter_Items():
        
    def byprice(matches, price_range):
        lower_limit, upper_limit = price_range
        return [item for item in matches if lower_limit <= float(item[1]['price']) <= upper_limit]

class Sort_Items():
  
    def __init__(self, some_list):
        self.some_list = some_list
        self.sort_functions = {
            "0": self.none,
            "1": self.price_ascending,
            "2": self.price_descending,
            "3": self.manufacturer_a_to_z,
            "4": self.manufacturer_z_to_a
        }

    def none(self, some_list):
        return some_list
    
    def price_ascending(self, some_list): 
        return sorted(some_list, key=lambda x: float(x[1]['price']))

    def price_descending(self, some_list): 
        return sorted(some_list, key=lambda x: float(x[1]['price']), reverse = True)

    def manufacturer_a_to_z(self, some_list): 
        return sorted(some_list, key=lambda x: x[1]['manufacturer'])

    def manufacturer_z_to_a(self, some_list): 
        return sorted(some_list, key=lambda x: x[1]['manufacturer'], reverse = True)
    
    @staticmethod
    def select():
        while True:
            print("""How would you like to sort your results? 
            1: Low-High
            2: High-Low
            3: A-Z
            4: Z-A
            0: None
            """)
            
            choice = input().strip()
            if choice in ["0", "1", "2", "3", "4"]:
                return choice
            
            else:
                print("Invalid choice. Please try again.")

# Fix, remove, or combine the below (keep in mind the init methods have a method of this within them.)

def process_data(init_output, price_range):
    # print(f"{LCSC/Mouser/Digi/etc...}")
    sorter = Sort_Items(init_output)
    choice = Sort_Items.select()
    sorted_results = sorter.sort_functions[choice](init_output)

    if price_range is None: 
        results = sorted_results
    else: 
        results = Filter_Items.byprice(sorted_results, price_range)
 
    print_ui(results)
    
def print_ui(results):
    print("-" * 80)
    print("{:<20} {:<30} {:<15} {:<45}".format('Price', 'Stock', 'Manufacturer', 'Product Number | Product Name'))
    print("-" * 80)

    for items in results: 
        product_details = f"{items[0]} | {items[1]['name']}"
        price           = f"${items[1]['price']}"
        stock           = items[1]['stock']
        manufacturer    = items[1]['manufacturer']
        link            = items[1]['link']

        print("{:<20} {:<30} {:<35} {:<45}".format(price, stock, manufacturer, product_details))
        print(f"Link: https://www.lcsc.com/{link}")
        print("-" * 80)   

scraper_init(product)
api_init()

# issues:      stock filter (line 48, 305, & 152)
#              pagenumber (line 105)
#              user selectable (64, 310, & create one for scrapers)

# just mouser: records (line 310)
# goal:        consistent input
#              consistent output

