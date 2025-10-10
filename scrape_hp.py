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
        # group_names = ["Scotland", "London and Surrey", "The West Country", "Elsewhere in Britain", "Elsewhere in the World"]

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
        place_types = heading.find_next_sibling("ul")
        for pt in place_types.find_all("a"):
            print("=" * 100)
            print(f"Retrieving type of place: {pt.get_text()}")
            print("=" * 100)
            pt_url = pt.get("href")
            # go through each letter in catalog
            for letter in self.alphabet:
                print("Retrieving letter: ", letter)
                cur_pt_url = f"{pt_url}?letter={letter}"
                cur_pt_page = requests.get(cur_pt_url)
                letter_soup = BeautifulSoup(cur_pt_page.text, "html.parser")
                middle_column = letter_soup.find_all("div", class_="col-md-12")[1]
                cur_pt_items = middle_column.find_all("article")
                for item in cur_pt_items:
                    item_url = item.find("link").get("href")
                    self.scrape_raw_text(item_url)
                    print("Finished scraping place: ", item_url)

if __name__ == "__main__":
    try:
        scraper = Scraper()
        scraper.retrieve_characters()
    except Exception as e:
        print(f"An error occurred: {e}")