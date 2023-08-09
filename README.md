# WebScraper
Draft 2:
Scrapes and parses the HTML on a Newegg search site, based on the user's input, and prints out each item inside the terminal.

Draft 3:
Same as Draft 2, but instead of printing each item in the terminal, the program creates an HTML file.
Added "while/not" statement if price values aren't integers.

Draft 4:
Scrapes Newegg, Bestbuy, or Homedepot for products containing the user's search query.
Uses 'keywords' to match keywords within texts, and 'pattern' keywords within strings.
Filters items based on user input of min and max price values.
Sorts items based on price (low/high, high/low).

Draft 5:
Scrapes LCSC for products containing the user's search query.
Added:
  - More error handling for user inputs
  - Sort alphabetically based on manufactuerer name
  - Prettier UI for Terminal

Scraper:
In the process of fixing page loop for LCSC.

  - **Filtering _Redefined_** [When filtering by price, we flag the key of the item that is outside that price range, and with that flag we delete the key] This is important, as you can not delete items in the dictionary while iterating through that same dictionary.

  - **Exclude Items Out-Of-Stock Within Class** [Check for whether an item is in stock or not when finding the stock tag]

  - **No Key Left Behind** [Never overwrite keys with the same key, even in the combined dictionary]: If keys in the item dictionary are identical (as they might be with "LM324" as the key), a number will be added to the end of the key to show that it's another item, like files on your device. This happens twice: 1st within the class the items are being found and 2nd within the process_data class when both dictionaries are being combined.

  - **Life-Cycle** [Life cycle status added to the end of "mouser" type in dictionary]

  - **Mid Information** [If a key is not accessable (for whatever reason), it will still include any information found]: With the fucntion .get("key", "default_value") and will assign that key to it's default value ("N/A")

Notes on usability: Using the product_number string as a key limited that amount of options I had when it came to filtering and sorting items. In fact, even the "Mid Information" change is because of this fact.
