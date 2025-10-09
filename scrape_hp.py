import requests
from bs4 import BeautifulSoup

# TODO: PLACES, COMPLETE MAGIC, EVENTS, THINGS, CREATURES, NOVELS (https://www.hp-lexicon.org/source/the-harry-potter-novels/)

class Scraper:
    def __init__(self, batch_size=20, store_callback=None):
        self.base_url = "https://www.hp-lexicon.org"
        self.documents_scraped = 0
        self.batch_size = batch_size
        self.store_callback = store_callback
    
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

    # TODO: COMPLETE TYPES OF PLACES
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

if __name__ == "__main__":
    try:
        scraper = Scraper()
        scraper.retrieve_characters()
    except Exception as e:
        print(f"An error occurred: {e}")