import requests
from bs4 import BeautifulSoup

# TODO: PLACES, COMPLETE MAGIC, EVENTS, THINGS, CREATURES, NOVELS (https://www.hp-lexicon.org/source/the-harry-potter-novels/)

class Scraper:
    def __init__(self, batch_size=20, store_callback=None):
        self.base_url = "https://www.hp-lexicon.org"
        self.documents_scraped = 0
        self.batch_size = batch_size
        self.store_callback = store_callback
        self.alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    
    def increment_documents_scraped(self):
        self.documents_scraped += 1
        
        if self.documents_scraped % self.batch_size == 0:
            self.store_callback()

    def get_documents_scraped(self):
        return self.documents_scraped

    def scrape_raw_text(self, url):
        character_page = requests.get(url)
        soup = BeautifulSoup(character_page.text, "html.parser")
        text = soup.find_all("p")
        text = [p.get_text() for p in text]
        text = "\n".join(text)
        
        filename = url.split('/')[-2]
        with open(f"hp_data/{filename}.txt", "w") as f:
            f.write(text)
        self.increment_documents_scraped()
    
    def scrape_alphabetical_catalog(self, heading):
        categories = heading.find_next_sibling("ul")
        for cat in categories.find_all("a"):
            print("=" * 100)
            print(f"Retrieving category: {cat.get_text()}")
            print("=" * 100)
            cat_url = cat.get("href")
            # go through each letter in catalog
            for letter in self.alphabet:
                print("Retrieving letter: ", letter)
                cur_cat_url = f"{cat_url}?letter={letter}"
                cur_cat_page = requests.get(cur_cat_url)
                letter_soup = BeautifulSoup(cur_cat_page.text, "html.parser")
                middle_column = letter_soup.find_all("div", class_="col-md-12")[1]
                cur_cat_items = middle_column.find_all("article")
                for item in cur_cat_items:
                    item_url = item.find("link").get("href")
                    self.scrape_raw_text(item_url)
                    print("Finished scraping category: ", item_url)
    
    def scrape_quotes(self, url):
        quote_page = requests.get(url)
        soup = BeautifulSoup(quote_page.text, "html.parser")
        quotes_list = soup.find_all("li")
        print(len(quotes_list))
        text = ""
        for quote in quotes_list:
            text += quote.get_text() + "\n"
        filename = url.split('/')[-1]
        with open(f"hp_data/{filename}.txt", "w") as f:
            f.write(text)

    # THIS DOES NOT RETRIEVE TIMELINES
    def retrieve_characters(self):
        print("Retrieving characters...")
        url = "https://www.hp-lexicon.org/characters/"
        characters_page = requests.get(url)
        soup = BeautifulSoup(characters_page.text, "html.parser")
        group_names = ["Notable Characters", "Families", "Groups and Related Resources"]

        for i, group_name in enumerate(group_names):
            heading = soup.find("h2", string=group_name)
            print("=" * 100)
            print("Retrieving group: ", group_name)
            print("=" * 100)
            group = heading.find_next_sibling("ul")
            for character in group.find_all("a"):
                char_url = character.get("href")
                self.scrape_raw_text(char_url)
                print(f"Scraped character: {char_url}")

    def retrieve_places(self):
        print("Retrieving places...")
        url = "https://www.hp-lexicon.org/places/"
        places_page = requests.get(url)
        soup = BeautifulSoup(places_page.text, "html.parser")
        group_names = ["Scotland", "London and Surrey", "The West Country", "Elsewhere in Britain", "Elsewhere in the World"]

        for i, group_name in enumerate(group_names):
            heading = "h3"
            if i == 5:
                heading = "h2"
            heading = soup.find(heading, string=group_name)
            print("=" * 100)
            print("Retrieving group: ", group_name)
            print("=" * 100)
            group = heading.find_next_sibling("ul")
            for place in group.find_all("a"):
                place_url = place.get("href")
                self.scrape_raw_text(place_url)
                print(f"Place: {place_url}")
        
        # types of places
        heading = soup.find("h2", string="Types of Places")
        self.scrape_alphabetical_catalog(heading)
    
    def retrieve_magic(self):
        print("Retrieving magic...")
        url = "https://www.hp-lexicon.org/magic/"
        magic_page = requests.get(url)
        soup = BeautifulSoup(magic_page.text, "html.parser")
        magic_groups_catalogs = ["Spells", "Potions", "Magical Items & Devices", "Magical and Mundane Plants"]
        for group_name in magic_groups_catalogs:
            if group_name != "Magical Items & Devices":
                heading = soup.find("h2", string=group_name)
            else:
                heading = soup.select_one("html > body > article > section > div > div > section > div > div:nth-of-type(1) > div:nth-of-type(1) > h2:nth-of-type(3)")
            self.scrape_alphabetical_catalog(heading)
        magic_groups = ["Miscellaneous Magic", "Fields of Magical Study", "Quotes from J.K. Rowling"]
        for group_name in magic_groups:
            if group_name == "Fields of Magical Study":
                heading = soup.select_one("#content > div > div > section > div > div:nth-of-type(1) > div:nth-of-type(1) > h2:nth-of-type(7)")
            else:
                heading = soup.find("h2", string=group_name)
            print("=" * 100)
            print("Retrieving group: ", group_name)
            print("=" * 100)
            group = heading.find_next_sibling("ul")
            for magic in group.find_all("a"):
                magic_url = magic.get("href")
                if (group_name != "Quotes from J.K. Rowling"):
                    self.scrape_raw_text(magic_url)
                else:
                    self.scrape_quotes(magic_url)
                print(f"Magic: {magic_url}")

if __name__ == "__main__":
    try:
        scraper = Scraper(batch_size=20, store_callback=lambda: print(f"Scraped {scraper.documents_scraped} documents"))
        scraper.retrieve_magic()
    except Exception as e:
        print(f"An error occurred: {e}")