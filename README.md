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
Life cycle status added to "mouser" type
Filters stock within the scraper themselves
Never overwrite keys with the same key, even in the combined dictionary
