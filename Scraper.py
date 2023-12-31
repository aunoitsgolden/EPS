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
    def get_stock_filter():
        while True:
            try:
                product = int(input("Only present items in stock? Enter 1 for Yes | Enter 2 for No: "))

                if product == 1: 
                    return 4
                if product == 2: 
                    return 1
                else: 
                    print('Please enter either "1" or "2".')
                    
            except ValueError:
                print("Invalid input. Please try again.")
        # requires function within scraper methods to read "stock" tag, for API it's easily 1 or 4

    @staticmethod
    def get_price_range():
        while True:
            try:
                range_select = int(input("Filter by price? Enter 1 for Yes | Enter 2 for No: "))
                
                if range_select == 1:
                    lower_limit = float(input("Enter lower limit of price range: $"))
                    upper_limit = float(input("Enter upper limit of price range: $"))
                    
                    if lower_limit <= upper_limit:
                        return lower_limit, upper_limit
                    else:
                        print("Upper limit should be greater than or equal to lower limit. Please try again.")
                
                elif range_select == 2:
                    return None, None
                
                else:
                    print("Invalid choice. Please enter 1 or 2.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    @staticmethod
    def get_user_selectable():
        while True:
            try:
                product = int(input("Would you like to limit the amount of items presented? 1[Yes] 2[No]"))
                if product == 1:
                    user_selectable = input("How many items would you like to be presented?")
                    if user_selectable.isdigit():
                        return int(user_selectable)
                    else: 
                        print("Please input a valid integer.")
                
                elif product == 2: 
                    return None
                
                else: 
                    print("Please enter either 1 or 2")
                    
            except ValueError:
                print("Invalid input. Please try again.")

    @staticmethod
    def get_sort_method():
        while True:
            print("How would you like to sort your results? 1 [Low-High], 2 [High-Low], 3 [A-Z], 4 [Z-A] ")
            
            choice = input().strip()
            if choice in ["1", "2", "3", "4"]: 
                return choice
            else: 
                print("Invalid choice. Please try again.")

def keyword_match(product):
    product_words = product.split()
    stop_words = ["for", "and", "the", "an", "a", "from"]
    keywords = set()

    for word in product_words:
        if word.lower() not in stop_words: 
            keywords.add(word)
    
    pattern = re.compile('|'.join(keywords), re.IGNORECASE)
    return pattern

def selenium_driver(url, sleep_time):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(sleep_time)
    html = driver.page_source
    driver.quit()
    
    doc = BeautifulSoup(html, 'html.parser')

    return doc

class LCSC_Scraper():
   
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
                link_tail = product_tag.get('href')
                link = f'https://www.lcsc.com{link_tail}'
            else: raise AttributeError
            
            if name and product_number:
                name_strip = name + product_number
                
                pattern = keyword_match(product)
                if pattern.search(name_strip):  
                    original_key = product_number
                    count = 1
                    while product_number in matches:
                        product_number = f"{original_key}({count})"
                        count += 1

                    matches[product_number] =  {'name': name, 'link':link, 'item': item}
        
        return matches

    def gather_data(matches, stock_opt):
        for product_number, data in matches.items():
            item = data['item']
            
            price_tags = item.find_all("div", class_="price-row")
            for price_tag in price_tags:
                cleaned_tag = re.sub('\s+', ' ', (price_tag.text.strip()).replace('US$', ' ').strip())
                price = (cleaned_tag.split())[1]
                # qty_correlated = (cleaned_tag.split())[0]

            stock_tags = item.find_all("td", attrs={"data-v-3be1a989":""})[3].text.strip()
            if stock_tags and len(stock_tags) > 3:
                stock = re.sub('\s+', ' ', stock_tags.replace('\n', ' ').replace('\r', '').strip())

                if stock_opt and ("0" in stock or "discontinued" in stock.lower()): 
                    continue
                
            else: stock = "N/A"

            manufacturer = item.find("a", class_="link", href=lambda x: x and "/brand-detail/" in x).text.strip()

            matches[product_number] = {
                'name':data['name'], 
                'link':data['link'], 
                'price':price, 
                'stock':stock, 
                'manufacturer':manufacturer, 
                'type':'lcsc'
                }
       
        return matches
       
def scraper_init(_class_, url, sleep_time, stock_option):
    doc            = selenium_driver(url, sleep_time)
    gathered_items = _class_.search(doc) 
    matches        = _class_.gather_data(gathered_items, stock_option)
    return matches

class Mouser_API():
    
    def request(product, stock_option):
        query = {
            "SearchByKeywordRequest": {
                "keyword": product, 
                "records": 0, 
                "startingRecord": 0,
                "searchOptions": stock_option,
                "searchWithYourSignUpLanguage": "true"
            }
        }

        response = requests.post("https://api.mouser.com/api/v1.0/search/keyword?apiKey=ad401d68-e0f0-4cab-88f6-3ab2b02ca78d", json=query)
        data = response.json()
        return data
    
    def gather_data(data):
        matches = {}

        for part in data['SearchResults']['Parts']:
            try: name = part['Description']
            except: name = "N/A"
            
            try: product_number = part['ManufacturerPartNumber']
            except: product_number = "N/A"

            try: link = part['ProductDetailUrl']
            except: link = "N/A"

            try: life_cycle = part['LifecycleStatus']
            except: life_cycle = "N/A"

            try: stock = part['Availability']
            except: stock = "N/A"

            try: manufacturer = part['Manufacturer']
            except: manufacturer = "N/A"
            
            price = 0
            for price_break in part['PriceBreaks']:
                price = float(price_break['Price'].replace("$", ""))

            matches[product_number] = {
                'name':name, 
                'link':link, 
                'price':price, 
                'stock':stock, 
                'manufacturer':manufacturer, 
                'type':f'mouser {life_cycle}'
                }
        
        return matches

def api_init(product, stock_option):
    data    = Mouser_API.request(product, stock_option)
    matches = Mouser_API.gather_data(data)
    return matches

class Process_Data:

    def __init__(self, items):
        self.items = items
        self.sort_functions = {
            "1": self.price_ascending,
            "2": self.price_descending,
            "3": self.manufacturer_a_to_z,
            "4": self.manufacturer_z_to_a
        }
    
    def price_ascending(self, items): 
        return sorted(items.items(), key=lambda x:float(x[1].get('price', 0)))

    def price_descending(self, items): 
        return sorted(items.items(), key=lambda x:float(x[1].get('price', 0)), reverse=True)

    def manufacturer_a_to_z(self, items): 
        return sorted(items.items(), key=lambda x: x[1].get('manufacturer', 0))

    def manufacturer_z_to_a(self, items): 
        return sorted(items.items(), key=lambda x: x[1].get('manufacturer', 0), reverse=True)

    @staticmethod
    def merge_and_rename(d1, d2):
        merged_dict = d1.copy()

        for key, value in d2.items():
            new_key = key
            count = 1
            while new_key in merged_dict:
                new_key = f"{key}({count})"
                count += 1
            merged_dict[new_key] = value

        return merged_dict

    def filter_by_price(self, price_range):
        lower_limit, upper_limit = price_range
        if not lower_limit and upper_limit:
            return self.items
        
        keys_to_remove = []

        for key, value in self.items.items():
            try:
                price = float(value['price'])
            except (TypeError, ValueError, KeyError):
                print(f"Couldn't fetch or convert the price for key: {key}")
                continue
            
            if (lower_limit and price < lower_limit) or (upper_limit and price > upper_limit):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            self.items.pop(key)
            
        return self.items
    
    def filter_returned_amount(self, user_selectable, items):
        if not user_selectable:
            return items
        else: 
            return items[:user_selectable]

    def process_and_sort(self, price_range, user_selectable, sort_method):
        lvl1_filter = self.filter_by_price(price_range) 
        sorted_items = self.sort_functions[sort_method](lvl1_filter)
        lvl2_filter = self.filter_returned_amount(user_selectable, sorted_items)       
    
        return lvl2_filter

# Inputs purely for testing. Will edit for website.
product = User_Input.get_product()
stock_selected = User_Input.get_stock_filter()
price_range = User_Input.get_price_range()
user_selectable = User_Input.get_user_selectable()
sort_method = User_Input.get_sort_method()

lcsc_results = scraper_init(LCSC_Scraper, f"https://www.lcsc.com/search?q={product}", 1, stock_selected)
mouser_results = api_init(product, stock_selected)
combined_results = Process_Data.merge_and_rename(lcsc_results, mouser_results)        

processor = Process_Data(combined_results)
processed_data = processor.process_and_sort(price_range, user_selectable, sort_method)

# Terminal UI purely for testing. Will edit for website.
print("-" * 80)
print("{:<20} {:<30} {:<15} {:<45}".format('Price', 'Stock', 'Manufacturer', 'Product Number | Product Name'))
print("-" * 80)

for result in processed_data: 
    product_details = f"{result[0]} | {result[1]['name']}"
    price           = f"${result[1].get('price', 'N/A')}"
    stock           = result[1].get('stock', 'N/A')
    manufacturer    = result[1].get('manufacturer', 'N/A')
    link            = result[1].get('link', 'N/A')
    type            = result[1].get('type', 'N/A')

    print("{:<20} {:<30} {:<35} {:<45} {:<10}".format(price, stock, manufacturer, product_details, type))
    print(f"Link: {link}")
    print("-" * 80)   
